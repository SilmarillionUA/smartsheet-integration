from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.fields import EncryptedCharField


class UserManager(BaseUserManager):
    def _create_user(
        self, email, name, password, is_staff, is_superuser, **extra_fields
    ):
        now = timezone.now()

        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name or "",
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            date_joined=now,
            last_login=now,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra_fields):
        return self._create_user(
            email, name, password, False, False, **extra_fields
        )

    def create_superuser(self, email, name, password=None, **extra_fields):
        return self._create_user(
            email, name, password, True, True, **extra_fields
        )

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email"), max_length=255, unique=True)
    name = models.CharField(_("Full name"), max_length=255)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    smartsheet_token = EncryptedCharField(
        max_length=512, blank=True, default=""
    )

    date_joined = models.DateTimeField(_("Date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["name", "-date_joined"]

    def __str__(self):
        return self.name

    def has_usable_password(self) -> bool:
        return super().has_usable_password()

    has_usable_password.boolean = True
