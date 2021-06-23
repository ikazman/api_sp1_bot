import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='bot.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    """Получаем имя и текущий статус проекта."""
    homework_name = homework.get('homework_name')
    current_status = homework.get('status')

    if current_status == 'reviewing':
        verdict = 'Работа взята на проверку.'
    elif current_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    """Получаем данные по всем домашним работам."""
    header = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}

    homework_statuses = requests.get(API_URL,
                                     headers=header,
                                     params=params)
    return homework_statuses.json()


def send_message(message):
    """Направляем сообщение пользователю."""
    return bot.send_message(CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            if homeworks.get('homeworks'):
                current_homework = homeworks.get('homeworks')[0]
                current_status = parse_homework_status(current_homework)
                logger.info(send_message(current_status))
            time.sleep(300)
            current_timestamp = homeworks.get('current_date')

        except Exception as e:
            error_message = f'Бот упал с ошибкой: {e}'
            logging.exception(send_message(error_message))
            time.sleep(5)


if __name__ == '__main__':
    main()
