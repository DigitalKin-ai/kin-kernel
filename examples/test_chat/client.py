import grpc
from typing import Iterator
from threading import Thread
import proto.digitalkin.service.v1.chat_pb2 as chat_pb2
import proto.digitalkin.service.v1.chat_pb2_grpc as chat_pb2_grpc


def run() -> None:
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        user_name = input("Enter your username: ")
        room = input("Enter room name: ")

        def generate_messages() -> Iterator[chat_pb2.ChatMessage]:
            try:
                while True:
                    message = input()
                    if message.lower() == "exit":
                        print("Disconnecting...")
                        break
                    yield chat_pb2.ChatMessage(
                        user_name=user_name, message=message, room=room
                    )
            except grpc.RpcError as e:
                print(f"Error: {e}")

        def receive_messages(responses: Iterator[chat_pb2.ChatMessage]) -> None:
            try:
                for response in responses:
                    print(f"\r{response.user_name}: {response.message}\n> ", end="")
            except grpc.RpcError as e:
                print(f"Error: {e}")

        responses = stub.JoinChat(generate_messages())

        # Start a thread to handle incoming messages
        receive_thread = Thread(target=receive_messages, args=(responses,))
        receive_thread.start()

        # Keep the main thread running to handle user input
        receive_thread.join()


if __name__ == "__main__":
    run()
