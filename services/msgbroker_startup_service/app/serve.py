from contextlib import ExitStack
from os import environ
import pika

with ExitStack() as stack:
    msgbroker = pika.BlockingConnection(pika.ConnectionParameters(environ.get('RABBITMQ_HOST', 'localhost')))
    stack.enter_context(msgbroker)
    chan = msgbroker.channel()
    stack.enter_context(chan)

    # setup tasks exchange
    chan.exchange_declare(exchange='tasks', exchange_type='direct')


    def declare_tasks_queue(name: str, args=None):
        chan.queue_declare(queue=name, durable=True, arguments=args)
        chan.queue_bind(queue=name, exchange='tasks', routing_key=name)


    # setup tasks queues
    declare_tasks_queue('spfd')
    declare_tasks_queue('junglescout')
    declare_tasks_queue('kalodata')
    declare_tasks_queue('tiktok')
    declare_tasks_queue('products')
    declare_tasks_queue('bsr')
    declare_tasks_queue('kwt', {'x-max-priority': 20})

    # setup results exchange
    chan.exchange_declare(exchange='results', exchange_type='direct')

    def declare_results_queue(name: str, args=None):
        sname = 'result.success.' + name
        ename = 'result.error.' + name
        chan.queue_declare(queue=sname, durable=True, arguments=args)
        chan.queue_declare(queue=ename, durable=True, arguments=args)
        chan.queue_bind(queue=sname, exchange='results', routing_key=sname)
        chan.queue_bind(queue=ename, exchange='results', routing_key=ename)

    # setup results queues
    declare_results_queue('kwt')
    declare_results_queue('bsr')
    declare_results_queue('products')
