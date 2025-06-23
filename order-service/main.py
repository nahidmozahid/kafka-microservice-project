from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response
import psycopg2
from kafka import KafkaProducer
import json

app = FastAPI()
REQUEST_COUNT = Counter("order_requests_total", "Total order service requests")

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname="orderdb",
    user="user",
    password="password",
    host="postgres",
    port=5432
)
cursor = conn.cursor()

# Kafka producer setup
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.get("/create-order")
def create_order():
    REQUEST_COUNT.inc()
    order = {"order_id": 123, "status": "created"}
    # Send event to Kafka
    producer.send("orders", value=order)
    return {"message": "Order created and event sent to Kafka"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
