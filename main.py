#!./venv/bin/python
import pika
import dotenv

from src.TelegramRPC import TelegramRPC
from src.DroneRPC import DroneRPC
from src.GUIRPC import GUIRPC

config = dotenv.dotenv_values(".env")
connection = pika.BlockingConnection(pika.ConnectionParameters(config["RABBITMQ_HOST"]))
channel = connection.channel()

telegramRPC = TelegramRPC(channel)
droneRPC = DroneRPC(channel)
guiRPC = GUIRPC(channel)

def main():
    ...


if __name__ == "__main__":
    main()

