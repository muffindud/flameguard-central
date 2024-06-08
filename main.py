#!./venv/bin/python
from pika import BlockingConnection, ConnectionParameters
from pika.exceptions import AMQPConnectionError
from dotenv import dotenv_values
from threading import Thread

from src.TelegramRPC import TelegramRPC
from src.DroneRPC import DroneRPC
from src.GUIRPC import GUIRPC
from src.ImgRecRPC import ImgRecRPC

config = dotenv_values(".env")
try:
    connection = BlockingConnection(ConnectionParameters(config["RABBITMQ_HOST"]))
    channel = connection.channel()
except AMQPConnectionError: 
    print("Failed to connect to RabbitMQ server.")
    print("Please make sure the server is running and the configuration is correct.")
    exit(1)
except KeyError:
    print("Please make sure the .env file exists and is correctly configured.")
    print("Required keys:")
    print("  - RABBITMQ_HOST")
    print("  - RABBITMQ_PORT")
    exit(1)


# Supproted calls:
#   - send (obj.send_message)
telegramRPC = TelegramRPC(channel)
    #   + exchange: telegram_rpc

# Supported calls:
#   - send (obj.send_command)
#   - receive (obj.get_response)
droneRPC = DroneRPC(channel)
    #   + exchange: drone_rpc_send
    #   - exchange: drone_rpc_rec
guiRPC = GUIRPC(channel)
    #   + exchange: gui_rpc_send
    #   - exchange: gui_rpc_rec
imgRecRPC = ImgRecRPC(channel)
    #   + exchange: img_rec_rpc_send
    #   - exchange: img_rec_rpc_rec

def main():
    while True:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        connection.close()
        exit(0)
