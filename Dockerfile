FROM python:3.11.7

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

WORKDIR /bot

COPY ./bot /bot/

CMD ["python", "/bot/main.py"]