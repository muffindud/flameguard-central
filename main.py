#!./venv/bin/python
import pika
import dotenv

from src.TelegramRPC import TelegramRPC
from src.DroneRPC import DroneRPC

config = dotenv.dotenv_values(".env")
connection = pika.BlockingConnection(pika.ConnectionParameters(config["RABBITMQ_HOST"]))
channel = connection.channel()

telegramRPC = TelegramRPC(channel)
droneRPC = DroneRPC(channel)

def main():
    ...


if __name__ == "__main__":
    main()

