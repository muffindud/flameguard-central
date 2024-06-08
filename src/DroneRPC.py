from pika.adapters.blocking_connection import BlockingChannel


class DroneRPC:
    commands = {}

    def __init__(self, channel: BlockingChannel) -> None:
        channel.exchange_declare(exchange="drone_rpc_send", exchange_type="direct")

        channel.exchange_declare(exchange="drone_rpc_rec", exchange_type="direct")
        result = channel.queue_declare("", exclusive=True)
        self.callback_queue = result.method.queue
        channel.queue_bind(
            exchange="drone_rpc_rec", queue=self.callback_queue, routing_key="response"
        )
        channel.basic_consume(
            queue=self.callback_queue, on_message_callback=self.callback, auto_ack=True
        )

    def callback(self, ch, method, properties, body):
        command_key, command = body.split(" ")[0], body.split(" ")[1:-1] 
        print(f"Received: {body}")

        if command_key in self.commands:
            self.commands[command_key](command)
        else:
            print(f"Command key {command_key} not found for {body}.")

    def command_wrapper(self, func: callable, command: str):
        self.commands[command] = func
        def wrapper():
            func()
        return wrapper

    def send_command(self, command: str) -> str:
        self.channel.basic_publish(
            exchange="drone_rpc_send", routing_key="command", body=command
        )

    def get_response(self) -> str:
        return self.response
