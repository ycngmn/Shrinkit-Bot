FROM python:3.8
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD python3 shrink.py
EXPOSE 8081/tcp 8082/tcp
