from pika.adapters.blocking_connection import BlockingChannel


class ExchangeAdapter:
    commands = {}
    exchange: str
    channel: BlockingChannel

    def __callback(self, ch, method, properties, body):
        body = body.decode("utf-8")
        command_key, command = body.split(" ", 1)
        print(f"Received: {body}")

        if command_key in self.commands:
            print(f"Executing function \"{self.commands[command_key].__name__}\" with argument \"{command}\".")
            self.commands[command_key](command)
        else:
            print(f"Command key {command_key} not found for {body}.")

    def __init__(self, channel: BlockingChannel, exchange: str) -> None:
        self.channel = channel
        self.exchange = exchange

        self.channel.exchange_declare(f"{self.exchange}", exchange_type="direct")

        result = self.channel.queue_declare("", exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.queue_bind(
            exchange=f"{self.exchange}", queue=self.callback_queue, routing_key="receive"
        )
        self.channel.basic_consume(
            queue=self.callback_queue, on_message_callback=self.__callback, auto_ack=True
        )
    

    def command_wrapper(self, command: str):
        def decorator(func: callable):
            print(f"[{self.exchange}] Registered command: \"{command}\" with function \"{func.__name__}\".")
            self.commands[command] = func
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def send_command(self, command: str):
        print(f"Sent: {command}")
        self.channel.basic_publish(
            exchange=f"{self.exchange}",
            routing_key="send",
            body=f"{command}",
        )
