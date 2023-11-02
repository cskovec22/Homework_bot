class SendMessageException(Exception):
    """Класс исключения при отправке сообщения в телеграмм."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class HTTPErrorException(Exception):
    """Класс исключения при неудачном HTTP-запросе."""

    def __init__(self, message, message_params):
        self.message = message
        self.message_params = message_params

    def __str__(self):
        return (f'Ошибка! {self.message} '
                f'Параметры запроса: {self.message_params}')


class ConnectionErrorException(Exception):
    """Класс исключения при проблеме с подключением"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Ошибка! {self.message}'


class IndexErrorException(Exception):
    """Класс исключения при отсутствии данных о домашней работе."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class KeyErrorException(Exception):
    """Класс исключения при отсутствии ключа"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Ошибка! {self.message}'


class StatusErrorException(Exception):
    """Класс исключения при неожиданном статусе домашней работы"""

    def __init__(self, message, status):
        self.message = message
        self.status = status

    def __str__(self):
        return f'Ошибка! {self.message}'


class ErrorException(Exception):
    """Класс исключения при неизвестной ошибке."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Ошибка! {self.message}'


class CheckTokenException(Exception):
    """Класс исключения при отсутствии токенов."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
