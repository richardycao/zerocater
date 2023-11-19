FROM python:3

WORKDIR /app

COPY order_meals.py .
COPY requirements.txt .

RUN pip install --ignore-installed -r requirements.txt

CMD ["python3", "order_meals.py"]