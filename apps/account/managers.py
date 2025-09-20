import re
from django.contrib.auth.base_user import BaseUserManager
from safedelete.managers import SafeDeleteManager

from core.common.random import generate_random_string


class UserManager(BaseUserManager, SafeDeleteManager):
    # def get_by_natural_key_and_store(self, username, store, user_type):
    #     user_type = user_type if user_type else "su"
    #     return self.get(
    #         **{
    #             self.model.USERNAME_FIELD: username,
    #             "deleted__isnull": True,
    #             "store": store,
    #             "user_type": user_type,
    #             "is_guest": False,
    #         }
    #     )

    def create_user(
        self,
        auth_provider="email",
        email=None,
        email_verified=False,
        phone_verified=False,
        phone_number=None,
        password=None,
        first_name=None,
        middle_name=None,
        last_name=None,
        **kwargs,
    ):
        if not email and not phone_number:
            raise ValueError("Users must have an email address or phone number")
        if auth_provider == "email" and not password:
            raise ValueError("Password is required for email sign up")
        # generate a username for the user
        # username will be in format <user_type>-<email_name or phone_number>-<random_string[6]>
        # username = ""
        if email:
            email = self.normalize_email(email)
            email_name, domain_part = email.strip().rsplit("@", 1)
            username = email_name
        elif phone_number:
            username = phone_number
        username += f"-{generate_random_string(5)}"
        username = username.lower()
        username = re.sub(r"[^a-z0-9\-_]", "", username)

        user = self.model(
            email=email,
            phone_number=phone_number,
            username=username,
            auth_provider=auth_provider,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email_verified=email_verified,
            phone_verified=phone_verified,
            **kwargs,
        )
        if auth_provider == "email":
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
