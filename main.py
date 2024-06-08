#!./venv/bin/python
import pika
import dotenv

from src.TelegramRPC import TelegramRPC

config = dotenv.dotenv_values(".env")
connection = pika.BlockingConnection(pika.ConnectionParameters(config["RABBITMQ_HOST"]))
channel = connection.channel()

telegramRPC = TelegramRPC(channel)

def main():
    ...


if __name__ == "__main__":
    main()

