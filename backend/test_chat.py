import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.contrib.auth import get_user_model
from apps.ai.services import chat

u = get_user_model().objects.get(id=1)
try:
    result = chat(user=u, message="salom, qandaysan?", conversation_id=None, user_lat=None, user_lng=None, channel="test")
    print("OK:", result)
except Exception as exc:
    import traceback
    traceback.print_exc()