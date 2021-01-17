FROM python:3

WORKDIR /usr/src/app
COPY . .
RUN apt-get update
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install requests
EXPOSE 5000
EXPOSE 465

RUN apt-get install cron -y
RUN crontab cron-job
RUN crontab -l
CMD cron

RUN chmod +x ./cron-python.py
CMD [ "python", "./main.py" ]

