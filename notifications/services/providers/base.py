from abc import ABC, abstractmethod
from typing import Tuple

class BaseProvider(ABC):
    """
    Базовый интерфейс провайдера отправки.
    Метод send должен вернуть (success: bool, provider_response: str).
    При исключении — бросаем дальше, чтобы логика ретраев сработала.
    """
    @abstractmethod
    def send(self, *, to: str, subject: str, message: str) -> Tuple[bool, str]:
        ...
