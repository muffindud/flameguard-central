from pika.adapters.blocking_connection import BlockingChannel


class ExchangeAdapter:
    commands = {}

    def __init__(self, channel: BlockingChannel, exchange: str) -> None:
        channel.exchange_declare(f"{exchange}_send", exchange_type="direct")

        channel.exchange_declare(f"{exchange}_receive", exchange_type="direct")
        result = channel.queue_declare("", exclusive=True)
        self.callback_queue = result.method.queue
        channel.queue_bind(
            exchange=f"{exchange}_receive", queue=self.callback_queue, routing_key="response"
        )
        channel.basic_consume(
            queue=self.callback_queue, on_message_callback=self.__callback, auto_ack=True
        )
    
    def __callback(self, ch, method, properties, body):
        command_key, command = body.split(" ")[0], body.split(" ")[1:-1] 
        print(f"Received: {body}")

        if command_key in self.commands:
            self.commands[command_key](command)
        else:
            print(f"Command key {command_key} not found for {body}.")

    def command_wrapper(self, command: str, *args, **kwargs):
        def wrapper(func):
            self.commands[command] = func
            return func
        return wrapper

    def send_command(self, command: str, *args):
        self.channel.basic_publish(
            exchange="telegram_rpc",
            routing_key="send",
            body=f"{command}",
        )
