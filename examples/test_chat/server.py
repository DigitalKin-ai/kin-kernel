import grpc
from typing import Iterator
from concurrent import futures
from queue import Queue
from threading import Thread

import digitalkin.service.v1.chat_pb2_grpc as chat_pb2_grpc
import digitalkin.service.v1.chat_pb2 as chat_pb2

# TODO: pubsub data base structure


# https://github.com/melledijkstra/python-grpc-chat/blob/master/server.py
from examples.test_chat.pubsub import PubSub


class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self, pubsub: PubSub):
        self.pubsub = pubsub

    def JoinChat(
        self,
        request_iterator: Iterator[chat_pb2.ChatMessage],
        context: grpc.ServicerContext,
    ) -> Iterator[chat_pb2.ChatMessage]:
        message_queue = Queue()

        def callback(user_name: str, room: str, message: str) -> None:
            message_queue.put(
                chat_pb2.ChatMessage(user_name=user_name, message=message, room=room)
            )

        def message_sender() -> Iterator[chat_pb2.ChatMessage]:
            print("message_sender")
            while True:
                message = message_queue.get()
                if message is None:
                    print("User disconnected")
                    break
                yield message

        print("JoinChat")

        def handle_incoming_messages() -> None:
            has_subscription = False
            try:
                for chat_message in request_iterator:
                    user_name = chat_message.user_name
                    room = chat_message.room

                    if not has_subscription:
                        print("Subscribing to room ", room)
                        self.pubsub.subscribe(room, callback)
                        has_subscription = True

                    if chat_message.message:
                        print(f"Publish message: {chat_message.message}")
                        self.pubsub.publish(user_name, room, chat_message.message)
            except grpc.RpcError as e:
                print(f"Client disconnected with error: {e}")
            finally:
                message_queue.put(None)  # Sentinel to stop the message_sender

        # Start the incoming message handler in a separate thread
        incoming_thread = Thread(target=handle_incoming_messages)
        incoming_thread.start()

        # Return the message sender generator
        return message_sender()


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pubsub = PubSub()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(pubsub), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
