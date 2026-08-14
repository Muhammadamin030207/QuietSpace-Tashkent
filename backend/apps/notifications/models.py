from django.db import models


class Notification(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    kind = models.CharField(max_length=30)  # favorite_free | new_place | review_reply
    payload = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id}:{self.kind}"