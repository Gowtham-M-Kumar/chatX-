from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserBlock(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_blocked = models.BooleanField(default=False)
    blocked_at = models.DateTimeField(null=True, blank=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if self.is_blocked and not self.blocked_at:
            self.blocked_at = timezone.now()
            self.blocked_until = timezone.now() + timedelta(days=7)
        elif not self.is_blocked:
            self.blocked_at = None
            self.blocked_until = None
            self.reason = ''
        super().save(*args, **kwargs)
    
    def is_currently_blocked(self):
        if self.is_blocked and self.blocked_until:
            return timezone.now() < self.blocked_until
        return False
    
    def days_remaining(self):
        if self.is_currently_blocked():
            remaining = self.blocked_until - timezone.now()
            return remaining.days
        return 0
    
    def __str__(self):
        return f"{self.user.username} - {'Blocked' if self.is_blocked else 'Unblocked'}"