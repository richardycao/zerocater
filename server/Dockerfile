FROM tensorflow/tensorflow

WORKDIR /app

COPY server.py .
COPY requirements.txt .

RUN pip install --ignore-installed -r requirements.txt

EXPOSE 3001

CMD ["python3", "server.py"]