import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import (
    CheckTokenException,
    ConnectionErrorException,
    ErrorException,
    HTTPErrorException,
    IndexErrorException,
    KeyErrorException,
    SendMessageException,
    StatusErrorException,
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
REQUEST_TIME = int(time.time())

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(name=__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """
    Проверка доступности переменных окружения,
    которые необходимы для работы программы.
    """
    logger.debug('Проверка доступности переменных окружения.')

    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }

    for key in tokens:
        if not tokens[key]:
            raise CheckTokenException(
                f'Отсутствует переменная окружения {key}.'
            )

    if all(tokens.keys()):
        logger.debug(
            'Проверка доступности переменных окружения успешно выполнена.'
        )
        return None


def send_message(bot, message):
    """
    Отправка сообщения в Telegram чат.
    Принимает на вход два параметра:
    экземпляр класса Bot и строку с текстом сообщения.
    """
    logger.debug('Попытка отправить сообщение в телеграм.')

    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)

    except Exception as error:
        raise SendMessageException(f'Ошибка {error} при отправке '
                                    f'сообщения "{message}" в телеграмм.')

    logger.debug(f'Бот отправил сообщение "{message}"')


def get_api_answer(timestamp):
    """
    Запрос к эндпоинту API-сервиса.
    В качестве параметра в функцию передается временная метка.
    В случае успешного запроса возвращается ответ API,
    приведенный из формата JSON к типам данных Python.
    """
    PARAMS = {'from_date': timestamp}
    message_params = (
        (f'URL: {ENDPOINT}'),
        (f'headers: {HEADERS}'),
        (f'params: {PARAMS}')
    )

    logger.debug('Попытка запроса')

    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=PARAMS
        )
        if response.status_code != HTTPStatus.OK:
            raise HTTPErrorException('', message_params)

    except HTTPErrorException:
        raise HTTPErrorException('Неудачный HTTP-запрос.', message_params)
    except requests.ConnectionError:
        raise ConnectionErrorException('Проблема с подключением.')
    except requests.RequestException as err:
        raise ErrorException(f'Возникла ошибка: {err}.')

    logger.debug('Успешный запрос')

    return response.json()


def check_response(response):
    """
    Проверка ответа API на соответствие документации
    из урока API сервиса Практикум.Домашка.
    В качестве параметра функция получает ответ API,
    приведенный к типам данных Python.
    """
    global REQUEST_TIME

    logger.debug('Проверка ответа API.')

    try:
        REQUEST_TIME = response['current_date']
        if not isinstance(response['homeworks'], list):
            raise TypeError
        homework = response['homeworks'][0]

    except KeyError as key_err:
        raise KeyErrorException(
            f'Отсутствует ключ {key_err} в ответе API.'
        )
    except TypeError:
        raise TypeError(
            'В ответе API структура данных не соответствует ожиданиям.'
        )
    except IndexError:
        raise IndexErrorException('Новых статусов домашней работы нет.')
    except Exception as err:
        raise ErrorException(f'Возникла ошибка: {err}.')

    logger.debug('Ответ API успешно проверен.')

    return homework


def parse_status(homework):
    """
    Извлечение из информации о конкретной домашней работе
    статус этой работы.
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
            raise StatusErrorException('', status)

    except StatusErrorException:
        raise StatusErrorException(
            f'Неожиданный статус домашней работы: {status}',
            status
        )
    except KeyError as key_err:
        raise KeyErrorException(
            f'Отсутствует ключ {key_err} в информации о домашней работе. '
        )
    except Exception as err:
        raise ErrorException(f'Возникла ошибка: {err}.')

    logger.debug('Информация извлечена успешно.')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    try:
        check_tokens()

    except CheckTokenException as token_err:
        logger.critical(token_err)
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    last_message = ''

    while True:
        try:
            timestamp = REQUEST_TIME
            api_answer = get_api_answer(timestamp)
            message = parse_status(check_response(api_answer))

            send_message(bot, message)

        except SendMessageException as send_err:
            logger.error(send_err)
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
