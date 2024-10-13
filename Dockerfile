FROM python:3.12

RUN mkdir -p /srv/weather_bot/bot
RUN mkdir -p /srv/weather_bot/sql
WORKDIR /srv/weather_bot/bot

COPY . /srv/weather_bot/bot
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]