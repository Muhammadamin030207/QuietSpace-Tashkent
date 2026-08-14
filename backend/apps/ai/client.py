"""Single Google Gemini client wrapper — all AI calls go through here."""
import json
import logging
import re
import threading
import time
from collections import deque

from google import genai
from google.genai import errors, types
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Free-tier Gemini quota is ~5 requests/minute per model. We keep a safe
# in-process buffer so bursts (tool loops, celery moderation) never hit 429.
MAX_CALLS_PER_MINUTE = int(getattr(settings, "GEMINI_MAX_CALLS_PER_MINUTE", 4))
_CALL_WINDOW = 60.0
_call_lock = threading.Lock()
_call_timestamps: deque[float] = deque()


def _throttle():
    """Wait until a Gemini call slot is available (in-process token bucket)."""
    now = time.monotonic()
    with _call_lock:
        while _call_timestamps and now - _call_timestamps[0] >= _CALL_WINDOW:
            _call_timestamps.popleft()
        if len(_call_timestamps) < MAX_CALLS_PER_MINUTE:
            _call_timestamps.append(time.monotonic())
            return
        wait = _call_timestamps[0] + _CALL_WINDOW - now
    if wait > 0:
        logger.info("Gemini quota slot busy — waiting %.1fs", wait)
        time.sleep(wait)
    with _call_lock:
        _call_timestamps.append(time.monotonic())
        while _call_timestamps and time.monotonic() - _call_timestamps[0] >= _CALL_WINDOW:
            _call_timestamps.popleft()


def _retry_delay_seconds(exc: errors.APIError) -> float | None:
    """Extract suggested retry delay from Gemini error payload."""
    try:
        details = (exc.details or {}).get("error", {}).get("details", [])
        for item in details:
            if "@type" in item and "RetryInfo" in item["@type"]:
                delay = item.get("retryDelay", "")
                match = re.search(r"([\d.]+)", delay)
                if match:
                    return float(match.group(1))
    except (AttributeError, TypeError):
        pass
    match = re.search(r"Please retry in ([\d.]+)s", str(exc))
    if match:
        return float(match.group(1))
    return None


def _should_retry(exc: Exception) -> bool:
    """429 quota / 5xx server errors are worth retrying."""
    if isinstance(exc, errors.APIError):
        code = exc.code or getattr(exc, "status_code", None)
        return code in (429, 500, 502, 503, 504) or getattr(exc, "status", "") in (
            "RESOURCE_EXHAUSTED",
            "UNAVAILABLE",
            "INTERNAL",
        )
    return False


def _generate_with_retry(client, model, contents, config, retries: int = 3):
    """Call Gemini once with backoff on 429/5xx. Throttles in-process."""
    for attempt in range(retries + 1):
        _throttle()
        try:
            return client.models.generate_content(
                model=model, contents=contents, config=config
            )
        except errors.APIError as exc:
            if not _should_retry(exc) or attempt == retries:
                raise
            delay = _retry_delay_seconds(exc) or min(2 ** attempt * 2, 30)
            logger.warning(
                "Gemini call failed (%s), retry %s/%s in %.1fs",
                exc.status, attempt + 1, retries, delay,
            )
            time.sleep(delay)
    raise RuntimeError("Gemini retry loop exhausted")


def get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=settings.GEMINI_API_KEY)


CACHE_TTL = 600  # 10 minutes for identical requests


def cached_or_run(cache_key: str, producer):
    cached = cache.get(cache_key)
    if cached:
        return cached
    result = producer()
    cache.set(cache_key, result, CACHE_TTL)
    return result


def _strip_comments(json_text: str) -> str:
    """Gemini sometimes emits JSON with trailing commas / comments — clean up."""
    import re

    json_text = re.sub(r",\s*([}\]])", r"\1", json_text)
    return json_text


def parse_ai_json(text: str):
    """Parse 'pure JSON' AI replies (strips markdown fences, one retry attempt)."""
    if not isinstance(text, str):
        return None
    candidates = [text]
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
    if fenced:
        candidates.append(fenced.group(1).strip())
    for candidate in candidates + [_strip_comments(c) for c in candidates]:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def _to_contents(messages: list[dict]) -> list[types.Content]:
    """Convert {role, content} history into Gemini Contents."""
    contents = []
    for msg in messages:
        role = "model" if msg.get("role") == "assistant" else "user"
        content = msg.get("content", "")
        if isinstance(content, str):
            contents.append(
                types.Content(role=role, parts=[types.Part(text=content)])
            )
    return contents


def _to_gemini_tool(tool: dict) -> types.Tool:
    """Convert an Anthropic-style tool dict ({name, description, input_schema}) to Gemini."""

    def to_schema(props: dict) -> types.Schema:
        properties = {}
        for name, spec in (props or {}).get("properties", {}).items():
            type_key = str(spec.get("type", "string")).upper()
            schema_kwargs = {"type": getattr(types.Type, type_key, types.Type.STRING)}
            if spec.get("enum"):
                schema_kwargs["enum"] = spec["enum"]
            if spec.get("description"):
                schema_kwargs["description"] = spec["description"]
            properties[name] = types.Schema(**schema_kwargs)
        return types.Schema(
            type=types.Type.OBJECT,
            properties=properties,
            required=(props or {}).get("required", []),
        )

    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool.get("description", ""),
                parameters=to_schema(tool.get("input_schema", {})),
            )
        ]
    )


def _split_response(response) -> tuple[str, list]:
    """Extract (combined text, function_calls) from a Gemini response."""
    fn_calls = []
    texts = []
    if response.candidates and response.candidates[0].content:
        for part in response.candidates[0].content.parts or []:
            if part.function_call:
                fn_calls.append(part.function_call)
            elif part.text:
                texts.append(part.text)
    return "".join(texts), fn_calls


def complete(
    messages: list[dict],
    system: str,
    tools: list[dict] | None = None,
    max_tokens: int = 1024,
) -> str:
    """Single Gemini call, returns final text content."""
    client = get_client()
    config = types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=max_tokens,
    )
    if tools:
        config.tools = [_to_gemini_tool(t) for t in tools]
    response = _generate_with_retry(client, settings.GEMINI_MODEL, _to_contents(messages), config)
    return _split_response(response)[0]


def run_tool_loop(
    messages: list[dict],
    system: str,
    tools: list[dict],
    tool_executor,
    max_turns: int = 6,
):
    """Run Gemini with tools until it returns a final text answer."""
    client = get_client()
    contents = _to_contents(messages)
    config = types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=1024,
        tools=[_to_gemini_tool(t) for t in tools],
    )
    for _ in range(max_turns):
        response = _generate_with_retry(client, settings.GEMINI_MODEL, contents, config)
        text, fn_calls = _split_response(response)
        if not fn_calls:
            return text
        if response.candidates and response.candidates[0].content:
            contents.append(response.candidates[0].content)
        else:
            contents.append(
                types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            function_call=types.FunctionCall(name=fc.name, args=fc.args)
                        )
                        for fc in fn_calls
                    ],
                )
            )
        tool_results = []
        for fc in fn_calls:
            result = tool_executor(fc.name, fc.args or {})
            tool_results.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fc.name,
                        response={"results": result},
                    )
                )
            )
        contents.append(types.Content(role="user", parts=tool_results))
        logger.info("AI tool loop: executed %s", [fc.name for fc in fn_calls])
    return "AI tool loop exhausted"