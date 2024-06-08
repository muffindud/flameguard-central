#!./venv/bin/python
from pika import BlockingConnection, ConnectionParameters
from pika.exceptions import AMQPConnectionError
from dotenv import dotenv_values
from threading import Thread

from src.ExchangeAdapter import ExchangeAdapter


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
telegram_exchange = ExchangeAdapter(channel, "telegram")
    #   + exchange: telegram_rpc

# Supported calls:
#   - send (obj.send_command)
#   - receive (obj.get_response)
drone_exchange = ExchangeAdapter(channel, "drone")
    #   + exchange: drone_rpc_send
    #   - exchange: drone_rpc_rec
gui_exchange = ExchangeAdapter(channel, "gui")
    #   + exchange: gui_rpc_send
    #   - exchange: gui_rpc_rec
img_rec_exchange = ExchangeAdapter(channel, "img_rec")
    #   + exchange: img_rec_rpc_send
    #   - exchange: img_rec_rpc_rec

# @ExchangeAdapter.command_wrapper("example_command")
# def example_command(args):
#     print("Example command called with args:", args)

def main():
    while True:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        connection.close()
        exit(0)
