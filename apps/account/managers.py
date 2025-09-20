from django.contrib.auth.base_user import BaseUserManager
from safedelete.managers import SafeDeleteManager


class UserManager(BaseUserManager, SafeDeleteManager):
    def get_by_natural_key_and_store(self, username, store, user_type):
        user_type = user_type if user_type else "su"
        return self.get(
            **{
                self.model.USERNAME_FIELD: username,
                "deleted__isnull": True,
                "store": store,
                "user_type": user_type,
                "is_guest": False,
            }
        )

    def create_user(self, email, password=None, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.user_type = "su"
        user.save(using=self._db)
        return user
