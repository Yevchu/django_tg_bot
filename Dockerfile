FROM python:3.12

# Встановлюємо робочу директорію в контейнері
WORKDIR /usr/src/app

# Копіюємо весь проєкт у контейнер
COPY . /usr/src/app/
COPY telegram_bot/bot_app/bot.py /usr/src/app/bot.py

# Встановлюємо Poetry (якщо використовуєте його)
RUN pip install poetry && poetry config virtualenvs.create false

# Встановлюємо залежності
RUN poetry install --no-root --no-interaction

# Встановлюємо змінну середовища для коректного імпорту Django
ENV PYTHONPATH="/usr/src/app/telegram_bot"
ENV DJANGO_SETTINGS_MODULE=telegram_bot.settings

# Запускаємо бота (замініть при необхідності)
CMD ["python", "telegram_bot/bot.py"]
