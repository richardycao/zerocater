FROM python:3

WORKDIR /app

COPY data_collection.py .
COPY requirements.txt .

RUN pip install --ignore-installed -r requirements.txt

CMD ["python3", "data_collection.py"]