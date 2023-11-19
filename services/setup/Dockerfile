FROM python:3

WORKDIR /app

COPY ./postgres/postgres.py .
COPY ./services/setup/setup.py .
COPY ./services/setup/requirements.txt .

RUN pip install --ignore-installed -r requirements.txt

CMD ["python3", "setup.py"]