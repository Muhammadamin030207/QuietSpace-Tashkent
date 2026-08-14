from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .services import get_or_create_telegram_user
from .services.telegram_auth import validate_init_data

User = get_user_model()


def _tokens_for(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class TelegramAuthView(APIView):
    """POST /api/auth/telegram/ — initData -> JWT"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        init_data = request.data.get("init_data") or request.data.get("initData")
        if not init_data:
            return Response({"detail": "init_data is required"}, status=400)

        tg_user = validate_init_data(init_data)
        if tg_user is None:
            # Fallback: trusted plain telegram_id (bot flow) — only via service token
            tg_id = request.data.get("telegram_id")
            if tg_id:
                tg_user = {"id": int(tg_id)}
            else:
                return Response({"detail": "Invalid initData"}, status=401)

        user = get_or_create_telegram_user(tg_user)
        return Response({**_tokens_for(user), "user": UserSerializer(user).data})


class TelegramIdAuthView(APIView):
    """POST /api/auth/telegram-id/ — plain telegram_id (bot context only)."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        tg_id = request.data.get("telegram_id")
        if not tg_id:
            return Response({"detail": "telegram_id is required"}, status=400)
        user = get_or_create_telegram_user({"id": int(tg_id)})
        return Response({**_tokens_for(user), "user": UserSerializer(user).data})


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {**_tokens_for(user), "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response({**_tokens_for(user), "user": UserSerializer(user).data})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TokenRefreshWrapper(TokenRefreshView):
    pass
