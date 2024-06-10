#!./venv/bin/python
from pika import BlockingConnection, ConnectionParameters
from pika.exceptions import AMQPConnectionError
from dotenv import dotenv_values
from threading import Thread

from flask import Flask, jsonify
from flask_cors import CORS

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

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
server_thread = Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000})
server_thread.daemon = True

telegram_exchange = ExchangeAdapter(channel, "telegram")
drone_exchange = ExchangeAdapter(channel, "drone")
img_rec_exchange = ExchangeAdapter(channel, "img_rec")


# Flask routes for the GUI
@app.route("/stats", methods=["GET"])
def gui_stats():
    # TODO: Implement stats
    return jsonify({"msg": "OK Stats"})

@app.route("/image", methods=["GET"])
def gui_image():
    # TODO: Implement image
    return jsonify({"msg": "OK Image"})

@app.route("/patrol", methods=["GET"])
def gui_patrol():
    # TODO: Implement patrol
    return jsonify({"msg": "OK Patrol"})


def main():
    server_thread.start()
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        connection.close()
        exit(0)
