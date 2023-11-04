import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram import Bot

from exceptions import (
    CheckTokenError,
    ConnectionMissingError,
    HTTPFailError,
    IndexMissingError,
    KeyMissingError,
    UnexpectedStatusError,
    UnexpectedTypeError,
    UnknownError,
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(name=__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s %(module)s %(lineno)d '
    '%(funcName)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверка доступности переменных окружения."""
    logger.debug('Проверка доступности переменных окружения.')

    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    missing_tokens = []

    for key, value in tokens.items():
        if not value:
            missing_tokens.append(key)

    if missing_tokens:
        message = (
            'Отсутствуют переменные окружения: '
            f'{", ".join(missing_tokens)}.'
        )
        logger.critical(message)
        raise CheckTokenError(message)

    logger.debug(
        'Проверка доступности переменных окружения успешно выполнена.'
    )


def send_message(bot, message):
    """
    Отправка сообщения в Telegram чат.
    Принимает на вход два параметра:
    экземпляр класса Bot и строку с текстом сообщения.
    """
    logger.debug('Попытка отправить сообщение в Telegram чат.')

    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)

    except telegram.error.TelegramError as error:
        logger.error(
            f'При отправке сообщения "{message}" в '
            f'Telegram чат возникла ошибка: {error}.'
        )

    else:
        logger.debug(f'Бот отправил сообщение "{message}"')


def get_api_answer(timestamp):
    """
    Запрос к эндпоинту API-сервиса.
    В качестве параметра в функцию передается временная метка.
    В случае успешного запроса возвращается ответ API,
    приведенный из формата JSON к типам данных Python.
    """
    PARAMS = {'from_date': timestamp}
    message_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': PARAMS
    }

    logger.debug(
        'Попытка запроса с параметрами:\n'
        'url: {url},\n'
        'headers: {headers},\n'
        'params: {params}.'.format(**message_params)
    )

    try:
        response = requests.get(**message_params)

        if response.status_code != HTTPStatus.OK:
            raise HTTPFailError(
                'Неудачный HTTP-запрос. '
                f'Код ответа API: {response.status_code}.'
            )

    except requests.ConnectionError:
        raise ConnectionMissingError('Проблема с подключением.')
    except requests.RequestException as err:
        raise UnknownError(f'Возникла ошибка: {err}')

    logger.debug('Успешный HTTP-запрос.')

    return response.json()


def check_response(response):
    """
    Проверка ответа API.
    В качестве параметра функция получает ответ API,
    приведенный к типам данных Python.
    """
    logger.debug('Проверка ответа API.')

    try:
        if (
            not isinstance(response, dict)
            or not isinstance(response['homeworks'], list)
        ):
            raise UnexpectedTypeError(
                'В ответе API структура данных не соответствует ожиданиям.'
            )
        homework = response['homeworks'][0]

    except KeyError as key_err:
        raise KeyMissingError(
            f'Отсутствует ключ {key_err} в ответе API.'
        )
    except UnexpectedTypeError as type_err:
        raise TypeError(type_err) from type_err
    except IndexError:
        raise IndexMissingError('Новых статусов домашней работы нет.')
    except Exception as err:
        raise UnknownError(f'Возникла ошибка: {err}')

    logger.debug('Ответ API успешно проверен.')

    return homework


def parse_status(homework):
    """
    Извлечение из информации о конкретной домашней работе статуса этой работы.
    В качестве параметра функция получает только один
    элемент из списка домашних работ.
    В случае успеха, функция возвращает подготовленную
    для отправки в Telegram строку, содержащую один из
    вердиктов словаря HOMEWORK_VERDICTS.
    """
    logger.debug('Извлечение информации о конкретной домашней работе.')

    try:
        status = homework['status']
        homework_name = homework['homework_name']
        verdict = HOMEWORK_VERDICTS.get(status)

        if not verdict:
            raise UnexpectedStatusError(
                f'Неожиданный статус домашней работы: {status}.'
            )

    except KeyError as key_err:
        raise KeyMissingError(
            f'Отсутствует ключ {key_err} в информации о домашней работе.'
        )
    except Exception as err:
        raise UnknownError(f'Возникла ошибка: {err}')

    logger.debug('Информация извлечена успешно.')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = Bot(token=TELEGRAM_TOKEN)
    last_message = ''
    timestamp = 0

    while True:
        try:
            api_answer = get_api_answer(timestamp)
            timestamp = api_answer.get('current_date', timestamp)
            message = parse_status(check_response(api_answer))

            send_message(bot, message)

        except Exception as error:
            logger.error(error)
            message = str(error)
            if message != last_message:
                send_message(bot, message)
            last_message = message

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
