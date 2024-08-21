from kin_sdk.grpc_system import ModuleRegistryServer

if __name__ == "__main__":
    server = ModuleRegistryServer(50051)
    server.serve()
