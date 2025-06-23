from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response
from pymongo import MongoClient
from kafka import KafkaConsumer
import json
import threading

app = FastAPI()
REQUEST_COUNT = Counter("notification_requests_total", "Total notification service requests")

# Connect to MongoDB
client = MongoClient("mongodb://mongodb:27017/")
db = client["notificationdb"]

# Kafka consumer setup
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers=["kafka:9092"],
    auto_offset_reset="earliest",
    group_id="notification-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

def consume_messages():
    for message in consumer:
        order = message.value
        db.notifications.insert_one(order)
        print(f"Stored order: {order}")

threading.Thread(target=consume_messages, daemon=True).start()

@app.get("/")
def root():
    REQUEST_COUNT.inc()
    count = db.notifications.count_documents({})
    return {"message": f"Notifications stored: {count}"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
