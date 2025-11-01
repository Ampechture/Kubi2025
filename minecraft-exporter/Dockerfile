FROM python:3.9-slim

WORKDIR /app

RUN pip install prometheus-client mcstatus

COPY exporter.py .

EXPOSE 8000

CMD ["python", "exporter.py"]