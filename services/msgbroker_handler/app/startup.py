import time
from contextlib import ExitStack
from os import environ
import pika
from pika.exceptions import ChannelClosedByBroker

from pika.exchange_type import ExchangeType


def startup(logger):
    with ExitStack() as stack:
        msgbroker = pika.BlockingConnection(pika.ConnectionParameters(environ.get('RABBITMQ_HOST', 'localhost')))
        stack.enter_context(msgbroker)
        channel = msgbroker.channel()
        stack.enter_context(channel)

        def recreate_queue_with_messages(queue_name, exchange, new_args=None):
            temp_queue = f"temp.{queue_name}.{int(time.time())}"
            channel.queue_declare(queue=temp_queue, durable=True)

            channel.queue_bind(queue=temp_queue,
                               exchange=exchange,
                               routing_key=queue_name)

            channel.queue_delete(queue=queue_name)
            channel.queue_declare(queue=queue_name, durable=True, arguments=new_args)
            channel.queue_bind(queue=queue_name, exchange=exchange, routing_key=queue_name)

            while True:
                method, _, body = channel.basic_get(queue=temp_queue)
                if not method:
                    break
                channel.basic_publish(
                    exchange=exchange,
                    routing_key=queue_name,
                    body=body,
                )
                channel.basic_ack(method.delivery_tag)

            channel.queue_delete(queue=temp_queue)

        def declare_exchange(name: str, exchange_type=ExchangeType.direct, args=None):
            with msgbroker.channel() as tmp:
                try:
                    tmp.exchange_declare(exchange=name, exchange_type=exchange_type, arguments=args, passive=True)
                    logger.info(f"Exchange {name} is already defined")
                except ChannelClosedByBroker as e:
                    if e.reply_code == 406:
                        logger.info(f"Exchange {name} has changed parameters!")
                        channel.exchange_delete(name)
                        channel.exchange_declare(exchange=name, exchange_type=exchange_type, durable=True, arguments=args)
                    elif e.reply_code == 404:
                        logger.info(f"Exchange {name} does not exist. It must be created")
                        channel.exchange_declare(exchange=name, exchange_type=exchange_type, durable=True, arguments=args)
                    else: raise

        def declare_queues(queues: list[str], exchange, args=None):
            for qname in queues:
                with msgbroker.channel() as tmp:
                    try:
                        tmp.queue_declare(queue=qname, durable=True, arguments=args, passive=True)
                        logger.info(f"Queue {qname} is already defined")
                    except ChannelClosedByBroker as e:
                        if e.reply_code == 406:
                            logger.info(f"Queue {qname} has changed parameters!")
                            recreate_queue_with_messages(qname, exchange, args)
                        elif e.reply_code == 404:
                            logger.info(f"Queue {qname} does not exist. It must be created")
                            channel.queue_declare(queue=qname, durable=True, arguments=args)
                        else: raise
                channel.queue_bind(queue=qname, exchange=exchange, routing_key=qname)

        def declare_tasks_queue(name: str, args=None):
            return declare_queues([name], 'tasks', args)

        def declare_results_queue(name: str, args=None):
            return declare_queues([
                'result.success.' + name,
                'result.error.' + name,
            ], 'results', args)

        ### TASKS ###
        declare_exchange('tasks')

        declare_tasks_queue('spfd')
        declare_tasks_queue('junglescout')
        declare_tasks_queue('kalodata')
        declare_tasks_queue('tiktok')
        declare_tasks_queue('products')
        declare_tasks_queue('bsr')
        declare_tasks_queue('helium_blackbox')
        declare_tasks_queue('kwt', { 'x-max-priority': 20 })

        ### RESULTS ###
        declare_exchange('results')

        declare_results_queue('kwt')
        declare_results_queue('bsr')
        declare_results_queue('helium_blackbox')
        declare_results_queue('products')
