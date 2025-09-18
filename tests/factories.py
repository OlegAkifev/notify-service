import factory
from django.contrib.auth import get_user_model
from notifications.models import UserProfile

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    # set_password — postgeneration-хук; при включённом skip_postgeneration_save
    # объект уже сохранён на момент вызова, так что дополнительный автосейв не нужен
    password = factory.PostGenerationMethodCall("set_password", "pass1234")


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    phone = factory.Sequence(lambda n: f"+100000000{n}")
    telegram_chat_id = factory.Sequence(lambda n: str(10_000_000 + n))
