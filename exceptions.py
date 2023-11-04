class HTTPFailError(Exception):
    """Класс исключения при неудачном HTTP-запросе."""

    pass


class ConnectionMissingError(Exception):
    """Класс исключения при проблеме с подключением."""

    pass


class IndexMissingError(Exception):
    """Класс исключения при отсутствии данных о домашней работе."""

    pass


class KeyMissingError(Exception):
    """Класс исключения при отсутствии ключа."""

    pass


class UnexpectedStatusError(Exception):
    """Класс исключения при неожиданном статусе домашней работы."""

    pass


class UnknownError(Exception):
    """Класс исключения при неизвестной ошибке."""

    pass


class CheckTokenError(Exception):
    """Класс исключения при отсутствии токенов."""

    pass


class UnexpectedTypeError(Exception):
    """
    Класс исключения.
    В ответе API структура данных не соответствует ожиданиям.
    """

    pass
