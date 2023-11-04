class HTTPFailError(Exception):
    """Класс исключения при неудачном HTTP-запросе."""


class ConnectionMissingError(Exception):
    """Класс исключения при проблеме с подключением."""


class IndexMissingError(Exception):
    """Класс исключения при отсутствии данных о домашней работе."""


class KeyMissingError(Exception):
    """Класс исключения при отсутствии ключа."""


class UnexpectedStatusError(Exception):
    """Класс исключения при неожиданном статусе домашней работы."""


class UnknownError(Exception):
    """Класс исключения при неизвестной ошибке."""


class CheckTokenError(Exception):
    """Класс исключения при отсутствии токенов."""


class UnexpectedTypeError(Exception):
    """
    Класс исключения.
    В ответе API структура данных не соответствует ожиданиям.
    """
