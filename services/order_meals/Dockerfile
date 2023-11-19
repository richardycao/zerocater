FROM python:3

WORKDIR /app

COPY ./postgres/postgres.py .
COPY ./services/order_meals/order_meals.py .
COPY ./services/order_meals/requirements.txt .

RUN pip install --ignore-installed -r requirements.txt

CMD ["python3", "order_meals.py"]