FROM python:3

WORKDIR /app

COPY ./postgres/postgres.py .
COPY ./services/server/server.py .
COPY ./services/server/requirements.txt .

RUN pip install --ignore-installed -r requirements.txt

EXPOSE 3001

CMD ["python3", "server.py"]