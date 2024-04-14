FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN chmod 755 .
COPY . .

EXPOSE 8000
COPY django_run.sh /app/
RUN chmod +x /app/django_run.sh
CMD ["/app/django_run.sh"]