FROM python:3

WORKDIR /app

COPY ./postgres/postgres.py .
COPY ./services/data_collection/data_collection.py .
COPY ./services/data_collection/requirements.txt .

RUN pip install --ignore-installed -r requirements.txt

CMD ["python3", "data_collection.py"]