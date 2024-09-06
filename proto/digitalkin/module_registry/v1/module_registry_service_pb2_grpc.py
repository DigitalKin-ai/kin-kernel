"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from proto.digitalkin.module_registry.v1 import action_pb2 as digitalkin_dot_module__registry_dot_v1_dot_action__pb2
from proto.digitalkin.module_registry.v1 import registration_pb2 as digitalkin_dot_module__registry_dot_v1_dot_registration__pb2


class ModuleRegistryServiceStub(object):
    """ModuleRegistryService
    It manages the registration, discovery, and status tracking of modules within a multi-agent system (SMA).
    In the context of SMA, this service allows autonomous agents to register their modules, making their capabilities 
    discoverable by other agents. It facilitates dynamic collaboration by enabling agents to find and interact 
    with available modules in real-time. Additionally, it ensures that the status of each module is kept up to date,
    supporting the overall adaptability and coordination of the multi-agent environment.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterModule = channel.unary_unary(
            '/digitalkin.module_registry.v1.ModuleRegistryService/RegisterModule'
            , request_serializer=
            digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
            RegisterRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
            RegisterResponse.FromString)
        self.DeregisterModule = channel.unary_unary(
            '/digitalkin.module_registry.v1.ModuleRegistryService/DeregisterModule'
            , request_serializer=
            digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
            DeregisterRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
            DeregisterResponse.FromString)
        self.DiscoverModule = channel.unary_unary(
            '/digitalkin.module_registry.v1.ModuleRegistryService/DiscoverModule'
            , request_serializer=
            digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
            DiscoverRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
            DiscoverResponse.FromString)
        self.UpdateModuleStatus = channel.unary_unary(
            '/digitalkin.module_registry.v1.ModuleRegistryService/UpdateModuleStatus'
            , request_serializer=
            digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
            UpdateStatusRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
            UpdateStatusResponse.FromString)


class ModuleRegistryServiceServicer(object):
    """ModuleRegistryService
    It manages the registration, discovery, and status tracking of modules within a multi-agent system (SMA).
    In the context of SMA, this service allows autonomous agents to register their modules, making their capabilities 
    discoverable by other agents. It facilitates dynamic collaboration by enabling agents to find and interact 
    with available modules in real-time. Additionally, it ensures that the status of each module is kept up to date,
    supporting the overall adaptability and coordination of the multi-agent environment.
    """

    async def RegisterModule(self, request, context):
        """RegisterModule
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def DeregisterModule(self, request, context):
        """DeregisterModule
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def DiscoverModule(self, request, context):
        """DiscoverModule
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def UpdateModuleStatus(self, request, context):
        """UpdateModuleStatus
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ModuleRegistryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'RegisterModule': grpc.
        unary_unary_rpc_method_handler(servicer.RegisterModule,
        request_deserializer=
        digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
        RegisterRequest.FromString, response_serializer=
        digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
        RegisterResponse.SerializeToString), 'DeregisterModule': grpc.
        unary_unary_rpc_method_handler(servicer.DeregisterModule,
        request_deserializer=
        digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
        DeregisterRequest.FromString, response_serializer=
        digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
        DeregisterResponse.SerializeToString), 'DiscoverModule': grpc.
        unary_unary_rpc_method_handler(servicer.DiscoverModule,
        request_deserializer=
        digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
        DiscoverRequest.FromString, response_serializer=
        digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
        DiscoverResponse.SerializeToString), 'UpdateModuleStatus': grpc.
        unary_unary_rpc_method_handler(servicer.UpdateModuleStatus,
        request_deserializer=
        digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
        UpdateStatusRequest.FromString, response_serializer=
        digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
        UpdateStatusResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler(
        'digitalkin.module_registry.v1.ModuleRegistryService',
        rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


class ModuleRegistryService(object):
    """ModuleRegistryService
    It manages the registration, discovery, and status tracking of modules within a multi-agent system (SMA).
    In the context of SMA, this service allows autonomous agents to register their modules, making their capabilities 
    discoverable by other agents. It facilitates dynamic collaboration by enabling agents to find and interact 
    with available modules in real-time. Additionally, it ensures that the status of each module is kept up to date,
    supporting the overall adaptability and coordination of the multi-agent environment.
    """

    @staticmethod
    async def RegisterModule(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module_registry.v1.ModuleRegistryService/RegisterModule'
            , digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
            RegisterRequest.SerializeToString,
            digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
            RegisterResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata)

    @staticmethod
    async def DeregisterModule(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module_registry.v1.ModuleRegistryService/DeregisterModule'
            , digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
            DeregisterRequest.SerializeToString,
            digitalkin_dot_module__registry_dot_v1_dot_registration__pb2.
            DeregisterResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata)

    @staticmethod
    async def DiscoverModule(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module_registry.v1.ModuleRegistryService/DiscoverModule'
            , digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
            DiscoverRequest.SerializeToString,
            digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
            DiscoverResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata)

    @staticmethod
    async def UpdateModuleStatus(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module_registry.v1.ModuleRegistryService/UpdateModuleStatus'
            , digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
            UpdateStatusRequest.SerializeToString,
            digitalkin_dot_module__registry_dot_v1_dot_action__pb2.
            UpdateStatusResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata)
