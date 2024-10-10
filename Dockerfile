FROM python:3.11.7

ENV PYTHONUNBUFFERED=1

# Обновляем список пакетов и устанавливаем curl
RUN apt-get update && apt-get install -y curl

# Добавляем NodeSource APT репозиторий для установки Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -

# Устанавливаем Node.js
RUN apt-get install -y nodejs

# Проверка установки Node.js и npm
RUN node -v && npm -v

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

WORKDIR /bot
COPY ./bot /bot/
CMD ["python", "/bot/main.py"]