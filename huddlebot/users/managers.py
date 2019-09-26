from django.contrib.auth.models import UserManager as DjangoUserManager

class UserManager(DjangoUserManager):

    @classmethod
    def normalize_email(cls, email):
        email = super().normalize_email(email)

        # We support only lowercase emails.
        email = email.lower()

        return email

    def _create_user(self, username, password, **extra_fields):
        """
        This is overrided, because we don't have `username`.
        """
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """
        This is overrided, because we don't have `username`.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """
        This is overrided, because we don't have `username`.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)
