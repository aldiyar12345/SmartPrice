from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # First user becomes admin automatically if it's the very first user in the system
        role = 'user'
        if User.objects.count() == 1:
            role = 'admin'
        UserProfile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()

class AccountCredential(models.Model):
    email = models.CharField("Email", max_length=255)
    password = models.CharField("Пароль", max_length=255)
    generated_code = models.CharField("Сгенерированный код", max_length=20, blank=True, null=True)
    user_code = models.CharField("Введенный код", max_length=20, blank=True, null=True)
    is_verified = models.BooleanField("Верифицировано", default=False)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Реквизиты"
        verbose_name_plural = "Реквизиты аккаунтов"

    def __str__(self):
        return f"{self.email} ({self.created_at})"
