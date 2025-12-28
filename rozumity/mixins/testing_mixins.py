from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileCreationMixin:
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for tests in classes that inherit from this mixin.
        
        Creates two users: a client and an expert, and their associated profiles.
        The users are created with the email addresses "client@user.com" and
        "expert@user.com", and the password "password123".
        """
        cls.u_client = User.objects.create_user(
            email="client@user.com", password="password123", is_client=True
        )
        cls.u_expert = User.objects.create_user(
            email="expert@user.com", password="password123", is_expert=True
        )
        cls.p_client = cls.u_client.clientprofile
        cls.p_expert = cls.u_expert.expertprofile
