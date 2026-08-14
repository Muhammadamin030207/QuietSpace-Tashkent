from django.db import models
from django.utils import timezone


class AIConversation(models.Model):
    class Channel(models.TextChoices):
        WEB = "web", "web"
        BOT = "bot", "bot"
        MINIAPP = "miniapp", "miniapp"

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.WEB)
    messages = models.JSONField(default=list)  # Anthropic message format history
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"conversation-{self.pk}"

    def add_message(self, role, content):
        self.messages = self.messages[-39:] + [{"role": role, "content": content}]
        self.save(update_fields=["messages", "updated_at"])


class PlaceAISummary(models.Model):
    place = models.OneToOneField(
        "places.Place", on_delete=models.CASCADE, related_name="ai_summary"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_stale(self):
        age = timezone.now() - self.updated_at
        return age.total_seconds() > 24 * 3600

    def __str__(self):
        return f"summary-{self.place_id}"