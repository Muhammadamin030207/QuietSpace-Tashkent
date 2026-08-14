import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from apps.ai.client import run_tool_loop
from apps.ai.tools import SEARCH_PLACES_TOOL, execute_search_places

text = run_tool_loop(
    messages=[{"role": "user", "content": "Toshkentda jim kafe top, wifi bor"}],
    system='Sen yordamchisan. Faqat JSON qaytar: {"reply": "...", "place_ids": [...]}',
    tools=[SEARCH_PLACES_TOOL],
    tool_executor=lambda name, params: (
        execute_search_places(params, None) if name == "search_places" else []
    ),
)
print("RESULT:", text[:500])
