import logging

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import chat, recommend
from .throttling import UserAIThrottle

logger = logging.getLogger(__name__)


class AIChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserAIThrottle]

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response({"detail": "message is required"}, status=400)
        try:
            result = chat(
                user=request.user,
                message=message[:4000],
                conversation_id=request.data.get("conversation_id"),
                user_lat=request.data.get("user_lat"),
                user_lng=request.data.get("user_lng"),
                channel=request.data.get("channel", "web"),
            )
        except RuntimeError as exc:
            return Response({"detail": str(exc)}, status=503)
        except Exception as exc:  # noqa: BLE001
            logger.exception("AI chat failed")
            return Response(
                {"detail": "AI xizmati hozircha ishlamayapti. Keyinroq urinib ko'ring."},
                status=503,
            )
        return Response(result)


class AIRecommendView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserAIThrottle]

    def post(self, request):
        try:
            result = recommend(
                user=request.user,
                user_lat=request.data.get("user_lat"),
                user_lng=request.data.get("user_lng"),
                limit=int(request.data.get("limit") or 5),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("AI recommend failed")
            return Response(
                {"detail": "AI xizmati hozircha ishlamayapti. Keyinroq urinib ko'ring."},
                status=503,
            )
        return Response(result)
