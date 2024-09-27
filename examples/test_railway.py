import asyncio
import requests
from google.protobuf.json_format import MessageToJson
from digitalkin.module.v1.monitoring_pb2 import (
    GetModuleJobsRequest,
    GetModuleJobsResponse,
)


class GrpcWebClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def call(self, method, request):
        url = f"{self.base_url}/{method}"
        headers = {"Content-Type": "application/grpc-web+proto", "X-Grpc-Web": "1"}

        # Sérialiser la requête protobuf en bytes
        payload = request.SerializeToString()

        response = requests.post(url, headers=headers, data=payload)

        if response.status_code != 200:
            raise Exception(f"gRPC call failed: {response.status_code} {response.text}")

        # Désérialiser la réponse
        response_message = GetModuleJobsResponse()
        response_message.ParseFromString(response.content[5:])  # Skip gRPC-Web header

        return response_message


def run():
    client = GrpcWebClient("https://fibonacci-railway.digitalkin.ai")

    try:
        # Créer une requête
        request = GetModuleJobsRequest()

        # Appeler la méthode
        response = client.call("ModuleService/GetModuleJobs", request)

        print(response)
        print(f"Réponse reçue: {MessageToJson(response)}")
    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")


if __name__ == "__main__":
    run()
