FROM tensorflow/tensorflow

WORKDIR /app

COPY train_model.py .
# COPY ../postgres/postgres.py .
COPY requirements.txt .

RUN pip install --ignore-installed -r requirements.txt

CMD ["python3", "train_model.py"]