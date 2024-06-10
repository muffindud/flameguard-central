#!./venv/bin/python
import os

from pika import BlockingConnection, ConnectionParameters
from pika.exceptions import AMQPConnectionError
from dotenv import dotenv_values
from threading import Thread
from json import loads
from functools import partial
from requests import get

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


# RabbitMQ commands
@img_rec_exchange.command_wrapper("result")
def img_rec_result(result: str):
    result_target, result_rate, result_link = result.split(" ")
    if result_target == "Fire":
        telegram_exchange.send_command(f"{result_link} Fire detected! with {result_rate}% confidence!")
    elif result_target == "Smoke":
        telegram_exchange.send_command(f"{result_link} Smoke detected! with {result_rate}% confidence!")
    print(f"Image recognition result: {result}")


drone_status = {}
@drone_exchange.command_wrapper("status")
def drone_status(status: str):
    status = loads(status)
    print(f"Drone status: {status}")
    drone_status = status


@drone_exchange.command_wrapper("picture")
def drone_picture(picture: str):
    print(f"Drone picture: {picture}")
    picture_name = picture.split("/")[-1]
    with open(f"static/captures/{picture_name}", "wb") as f:
        f.write(get(picture).content)
    img_rec_exchange.send_command(picture)


# Flask routes for the GUI
@app.route("/stats", methods=["GET"])
def gui_stats():
    old_stats = drone_status
    cb = partial(drone_exchange.send_command, "status")
    connection.add_callback_threadsafe(cb)

    while drone_status == old_stats:
        pass

    return jsonify(drone_status)


@app.route("/image", methods=["GET"])
def gui_image():
    items = os.listdir("static/captures")
    items = [item for item in items if item.endswith(".png") or item.endswith(".jpg") or item.endswith(".jpeg")]
    sorted_items = sorted(items, key = lambda x: os.path.getmtime(f"static/captures/{x}"), reverse=True)
    print(sorted_items)

    return jsonify({
        "src": "/static/captures/" + sorted_items[0]
    })


@app.route("/patrol", methods=["GET"])
def gui_patrol():
    cb = partial(drone_exchange.send_command, "patrol")
    connection.add_callback_threadsafe(cb)
    return jsonify({"msg": "OK Patrol"})


def main():
    server_thread.start()
    # img_rec_exchange.send_command("https://assets-api.kathmandupost.com/thumb.php?src=https://assets-cdn.kathmandupost.com/uploads/source/news/2024/news/thumb9-1712799709.jpg")
    # img_rec_exchange.send_command("https://www.ecomatcher.com/wp-content/uploads/2023/08/ForestFires.jpg")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        secure_exit()
