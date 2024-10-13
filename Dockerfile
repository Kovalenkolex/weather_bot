FROM python:3.12

RUN mkdir -p /opt/weather_bot/bot
RUN mkdir -p /opt/weather_bot/sql
WORKDIR /opt/weather_bot/bot

COPY . /opt/weather_bot/bot
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]