import grpc
import time
import threading
import random
from google.protobuf import json_format, struct_pb2
from proto.digitalkin.module.v1.lifecycle_pb2 import StartModuleRequest
from proto.digitalkin.module.v1.module_service_pb2_grpc import ModuleServiceStub
import signal
import contextlib


def generate_request():
    input_data = {"number": 4, "factor": random.randint(1, 10)}
    return StartModuleRequest(
        input=json_format.ParseDict(input_data, struct_pb2.Struct()),
        setup_id="setups:test",
        module_ids=[],
        request_type=2,  # SEND
    )


@contextlib.contextmanager
def create_channel(server_address):
    channel = grpc.insecure_channel(server_address)
    try:
        yield channel
    finally:
        channel.close()


def run_client(server_address, num_requests, results, event):
    try:
        print(f"Client started, processing {num_requests} requests")

        with create_channel(server_address) as channel:
            metadata = [("module_id", "test"), ("module_role", "owner")]
            stub = ModuleServiceStub(channel)

            start_time = time.time()
            for i in range(num_requests):
                print(f"{i + 1}/{num_requests}", end="\r")
                try:
                    response_iterator = stub.StartModule(
                        iter([generate_request()]), metadata=metadata
                    )

                    timeout = time.time() + 5  # 5 seconds timeout
                    for response in response_iterator:
                        if time.time() > timeout:
                            print("Response timeout")
                            break
                        # Process response if needed
                except grpc.RpcError as e:
                    results["errors"] += 1
                    print(f"RPC Error: {e}")
                except Exception as e:
                    results["errors"] += 1
                    print(f"Unexpected error: {e}")

            end_time = time.time()
            results["time"] = end_time - start_time
            results["requests"] = num_requests

        print(f"Client finished, processed {num_requests} requests")
        event.set()  # Signal that this client has finished
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        event.set()  # Assurez-vous que l'événement est toujours défini


def run_load_test(server_address, num_clients, requests_per_client):
    threads = []
    results = []
    events = []

    for i in range(num_clients):
        client_results = {"time": 0, "requests": 0, "errors": 0}
        results.append(client_results)
        event = threading.Event()
        events.append(event)
        thread = threading.Thread(
            target=run_client,
            args=(server_address, requests_per_client, client_results, event),
        )
        threads.append(thread)
        thread.start()
        print(f"Started client {i+1}")

    # Wait for all clients to finish or timeout
    for i, (thread, event) in enumerate(zip(threads, events)):
        event.wait(timeout=30)  # 30 seconds timeout for each thread
        if not event.is_set():
            print(f"Thread {i+1} did not finish in time")

    print("All clients finished or timed out")

    # Calculate and print results
    total_time = sum(r["time"] for r in results)
    total_requests = sum(r["requests"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    avg_time = total_time / num_clients if num_clients > 0 else 0

    print("Load Test Results:")
    print(f"Total Clients: {num_clients}")
    print(f"Requests per Client: {requests_per_client}")
    print(f"Total Requests: {total_requests}")
    print(f"Total Errors: {total_errors}")
    print(f"Average Time per Client: {avg_time:.2f} seconds")
    print(
        f"Requests per Second: {total_requests / total_time:.2f}"
        if total_time > 0
        else "N/A"
    )


def timeout_handler(signum, frame):
    print("Test timed out")
    exit(1)


if __name__ == "__main__":
    server_address = "localhost:50052"  # Replace with your server address
    num_clients = 124
    requests_per_client = 64

    # Set a global timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(300)  # 5 minutes timeout

    try:
        run_load_test(server_address, num_clients, requests_per_client)
    finally:
        signal.alarm(0)  # Cancel the alarm

    print("Test completed successfully")
