from pika.adapters.blocking_connection import BlockingChannel


class TelegramRPC:
    def __init__(self, channel: BlockingChannel) -> None:
        channel.exchange_declare(exchange="telegram_rpc", exchange_type="direct")
    
    def send_message(self, message: str) -> None:
        self.channel.basic_publish(exchange="telegram_rpc", routing_key="message", body=message)
