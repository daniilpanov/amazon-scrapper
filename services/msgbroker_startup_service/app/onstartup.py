from contextlib import ExitStack
from os import environ
import pika

with ExitStack() as stack:
    msgbroker = pika.BlockingConnection(pika.ConnectionParameters(environ.get('RABBITMQ_HOST', 'localhost')))
    stack.enter_context(msgbroker)
    chan = msgbroker.channel()
    stack.enter_context(chan)

    # setup main exchange
    chan.exchange_declare(exchange='tasks', exchange_type='direct')


    def declare_tasks_queue(name: str):
        chan.queue_declare(queue=name, durable=True)
        chan.queue_bind(queue=name, exchange='tasks', routing_key=name)


    # setup tasks queues
    declare_tasks_queue('spfd')
    declare_tasks_queue('junglescout')
    declare_tasks_queue('kalodata')
    declare_tasks_queue('tiiktok')
    declare_tasks_queue('products')
    declare_tasks_queue('bsr')
    declare_tasks_queue('100asins')

