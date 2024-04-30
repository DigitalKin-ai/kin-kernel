from kin_sdk.grpc_services import ServiceRegistryServer

if __name__ == "__main__":
    server = ServiceRegistryServer(50051)
    server.serve()
