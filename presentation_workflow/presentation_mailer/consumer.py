import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import time
import sys
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


while True:
    try:
        def process_approval(ch, method, properties, body):
            message = json.loads(body)

            email = message["presenter_email"]
            name = message["presenter_name"]
            title = message["title"]

            sender = "admin@conference.go"
            receiver = email
            subject = "Your presentation has been accepted"
            body = f"{name}, we're happy to tell you that your presentation {title} has been accepted"

            send_mail(
                subject,
                body,
                sender,
                [receiver],
                fail_silently=False,
                )

        def process_rejection(ch, method, properties, body):
            message = json.loads(body)

            email = message["presenter_email"]
            name = message["presenter_name"]
            title = message["title"]

            sender = "admin@conference.go"
            receiver = email
            subject = "Your presentation has been rejected"
            body = f"{name}, unfortunately, we have to inform you that your presentation {title} has been rejected"

            send_mail(
                subject,
                body,
                sender,
                [receiver],
                fail_silently=False,
            )

        parameters = pika.ConnectionParameters(host='rabbitmq')
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='presentation_approvals')
        channel.basic_consume(
            queue='presentation_approvals',
            on_message_callback=process_approval,
            auto_ack=True,
        )
        channel.queue_declare(queue='presentation_rejections')
        channel.basic_consume(
            queue='presentation_rejections',
            on_message_callback=process_rejection,
            auto_ack=True,
        )
        channel.start_consuming()
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)
