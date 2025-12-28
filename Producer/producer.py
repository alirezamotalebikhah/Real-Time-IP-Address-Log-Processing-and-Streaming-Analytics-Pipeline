from confluent_kafka import Producer
import json
import random
import time



INTERVAL_SECONDS = 0.02

conf = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'python-producer'
}

producer = Producer(conf)
topic = "logs"

def random_ip():
    return f"192.168.{random.randint(0,255)}.{random.randint(0,255)}"

def random_url():
    return f"http://example.com/datapage{random.randint(0,100)}"

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Sent to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")



try:
    while True:
        log = {
            "log_timestamp" : time.time(),
            "ip" : random_ip(),
            "url" : random_url(),
        }
        producer.produce(
            topic=topic,
            value=json.dumps(log).encode('utf-8'),
            callback=delivery_report
        )
        print(log)
        time.sleep(INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("Interupt by user")
finally:
    producer.flush()
