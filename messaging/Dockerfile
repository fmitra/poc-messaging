FROM python:3.8.2

CMD ["python", "-m", "messaging"]
EXPOSE 8080
WORKDIR /messaging

COPY . /messaging/
RUN pip install -r /messaging/requirements.txt
