from django.db import models

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
