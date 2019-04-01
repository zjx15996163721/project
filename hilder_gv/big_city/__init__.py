import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5673, heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue='test')