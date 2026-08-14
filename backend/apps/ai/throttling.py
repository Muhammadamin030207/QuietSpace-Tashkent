from rest_framework.throttling import UserRateThrottle


class UserAIThrottle(UserRateThrottle):
    scope = "user_ai"
