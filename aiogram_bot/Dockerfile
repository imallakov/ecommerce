FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN chmod 755 .
COPY . .

CMD ["python", "main.py"] 