import pika

def run_spfd(rabbit: pika.BlockingConnection, url: str, fname: str, lname: str, email: str, phone: str):
    with rabbit.channel() as chan:
        chan.exchange_declare(exchange="tasks", exchange_type="direct")
        chan.queue_declare(queue="spfd", durable=True)
        chan.queue_bind(queue="spfd", exchange="tasks", routing_key="spfd")
        chan.basic_publish(
            exchange="tasks",
            routing_key="spfd",
            properties=pika.BasicProperties(priority=10, delivery_mode=pika.delivery_mode.DeliveryMode.Persistent, expiration="240000"),
            body=('{"url": "%s", "fname": "%s", "lname": "%s", "email": "%s", "phone": "%s"}' % (url, fname, lname, email, phone)).encode(),
        )

