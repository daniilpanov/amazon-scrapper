import pika

def run_spfd(rabbit: pika.BlockingConnection):
    chan = rabbit.channel()

