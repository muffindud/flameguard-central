#!./venv/bin/python
import os

from pika import BlockingConnection, ConnectionParameters
from pika.exceptions import AMQPConnectionError
from dotenv import dotenv_values
from threading import Thread

from flask import Flask, jsonify
from flask_cors import CORS

from src.ExchangeAdapter import ExchangeAdapter

def secure_exit(code: int = 0):
    try:
        connection.close()
    except:
        pass

    exit(code)

# Open the .env file and read the configuration
try:
    config = dotenv_values(".env")
except FileNotFoundError:
    print("Please make sure the .env file exists and is correctly configured.")
    print("Required keys:")
    print("  - RABBITMQ_HOST")
    secure_exit(1)
except:
    secure_exit(1)

# Connect to the RabbitMQ server
try:
    connection = BlockingConnection(ConnectionParameters(config["RABBITMQ_HOST"]))
    channel = connection.channel()
except AMQPConnectionError: 
    print("Failed to connect to RabbitMQ server.")
    print("Please make sure the server is running and the configuration is correct.")
    secure_exit(1)
except KeyError:
    print("Please make sure the .env file exists and is correctly configured.")
    print("Required keys:")
    print("  - RABBITMQ_HOST")
    secure_exit(1)
except:
    secure_exit(1)

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
    items = os.listdir("static/captures")
    items = [item for item in items if item.endswith(".jpg")]
    sorted_items = sorted(items, key = lambda x: os.path.getmtime(f"static/captures/{x}"), reverse=True)

    return jsonify({
        "src": "/static/captures/" + sorted_items[0]
    })


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
    except:
        secure_exit()
