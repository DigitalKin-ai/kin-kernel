"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from proto.digitalkin.module.v1 import information_pb2 as digitalkin_dot_module_dot_v1_dot_information__pb2
from proto.digitalkin.module.v1 import lifecycle_pb2 as digitalkin_dot_module_dot_v1_dot_lifecycle__pb2
from proto.digitalkin.module.v1 import monitoring_pb2 as digitalkin_dot_module_dot_v1_dot_monitoring__pb2


class ModuleServiceStub(object):
    """ModuleService
    It represents a functional unit within an agent in the multi-agent system (SMA). 
    Modules can be of three types: Kin, Tool, and Trigger. 
    - Kin: Represents the agent's core data architecture or "brain", such as a workflow-based model or an LLM (Large Language Model).
    - Tool: Refers to external utilities or tools that the agent uses to perform tasks or enhance its capabilities.
    - Trigger: Serves as the entry point for the agent, initiating processes or actions based on external inputs.
    This service manages the lifecycle and interactions of these modules, including starting, stopping, 
    and monitoring the module's status, as well as handling input and output operations.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.StartModule = channel.stream_stream(
            '/digitalkin.module.v1.ModuleService/StartModule',
            request_serializer=
            digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.
            StartModuleRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.
            StartModuleResponse.FromString, _registered_method=True)
        self.StopModule = channel.unary_unary(
            '/digitalkin.module.v1.ModuleService/StopModule',
            request_serializer=
            digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.
            StopModuleRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.
            StopModuleResponse.FromString, _registered_method=True)
        self.GetModuleStatus = channel.unary_unary(
            '/digitalkin.module.v1.ModuleService/GetModuleStatus',
            request_serializer=
            digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
            GetModuleStatusRequest.SerializeToString, response_deserializer
            =digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
            GetModuleStatusResponse.FromString, _registered_method=True)
        self.GetModuleJobs = channel.unary_unary(
            '/digitalkin.module.v1.ModuleService/GetModuleJobs',
            request_serializer=
            digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
            GetModuleJobsRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
            GetModuleJobsResponse.FromString, _registered_method=True)
        self.GetModuleInput = channel.unary_unary(
            '/digitalkin.module.v1.ModuleService/GetModuleInput',
            request_serializer=
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleInputRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleInputResponse.FromString, _registered_method=True)
        self.GetModuleOutput = channel.unary_unary(
            '/digitalkin.module.v1.ModuleService/GetModuleOutput',
            request_serializer=
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleOutputRequest.SerializeToString, response_deserializer
            =digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleOutputResponse.FromString, _registered_method=True)
        self.GetModuleSetup = channel.unary_unary(
            '/digitalkin.module.v1.ModuleService/GetModuleSetup',
            request_serializer=
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleSetupRequest.SerializeToString, response_deserializer=
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleSetupResponse.FromString, _registered_method=True)


class ModuleServiceServicer(object):
    """ModuleService
    It represents a functional unit within an agent in the multi-agent system (SMA). 
    Modules can be of three types: Kin, Tool, and Trigger. 
    - Kin: Represents the agent's core data architecture or "brain", such as a workflow-based model or an LLM (Large Language Model).
    - Tool: Refers to external utilities or tools that the agent uses to perform tasks or enhance its capabilities.
    - Trigger: Serves as the entry point for the agent, initiating processes or actions based on external inputs.
    This service manages the lifecycle and interactions of these modules, including starting, stopping, 
    and monitoring the module's status, as well as handling input and output operations.
    """

    async def StartModule(self, request_iterator, context):
        """StartModule
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def StopModule(self, request, context):
        """StopModule
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def GetModuleStatus(self, request, context):
        """GetModuleStatus
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def GetModuleJobs(self, request, context):
        """GetModuleJobs
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def GetModuleInput(self, request, context):
        """GetModuleInput
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def GetModuleOutput(self, request, context):
        """GetModuleOutput
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def GetModuleSetup(self, request, context):
        """GetModuleSetup
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ModuleServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'StartModule': grpc.
        stream_stream_rpc_method_handler(servicer.StartModule,
        request_deserializer=
        digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.StartModuleRequest.
        FromString, response_serializer=
        digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.StartModuleResponse
        .SerializeToString), 'StopModule': grpc.
        unary_unary_rpc_method_handler(servicer.StopModule,
        request_deserializer=
        digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.StopModuleRequest.
        FromString, response_serializer=
        digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.StopModuleResponse.
        SerializeToString), 'GetModuleStatus': grpc.
        unary_unary_rpc_method_handler(servicer.GetModuleStatus,
        request_deserializer=
        digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
        GetModuleStatusRequest.FromString, response_serializer=
        digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
        GetModuleStatusResponse.SerializeToString), 'GetModuleJobs': grpc.
        unary_unary_rpc_method_handler(servicer.GetModuleJobs,
        request_deserializer=
        digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
        GetModuleJobsRequest.FromString, response_serializer=
        digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
        GetModuleJobsResponse.SerializeToString), 'GetModuleInput': grpc.
        unary_unary_rpc_method_handler(servicer.GetModuleInput,
        request_deserializer=
        digitalkin_dot_module_dot_v1_dot_information__pb2.
        GetModuleInputRequest.FromString, response_serializer=
        digitalkin_dot_module_dot_v1_dot_information__pb2.
        GetModuleInputResponse.SerializeToString), 'GetModuleOutput': grpc.
        unary_unary_rpc_method_handler(servicer.GetModuleOutput,
        request_deserializer=
        digitalkin_dot_module_dot_v1_dot_information__pb2.
        GetModuleOutputRequest.FromString, response_serializer=
        digitalkin_dot_module_dot_v1_dot_information__pb2.
        GetModuleOutputResponse.SerializeToString), 'GetModuleSetup': grpc.
        unary_unary_rpc_method_handler(servicer.GetModuleSetup,
        request_deserializer=
        digitalkin_dot_module_dot_v1_dot_information__pb2.
        GetModuleSetupRequest.FromString, response_serializer=
        digitalkin_dot_module_dot_v1_dot_information__pb2.
        GetModuleSetupResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler(
        'digitalkin.module.v1.ModuleService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('digitalkin.module.v1.ModuleService',
        rpc_method_handlers)


class ModuleService(object):
    """ModuleService
    It represents a functional unit within an agent in the multi-agent system (SMA). 
    Modules can be of three types: Kin, Tool, and Trigger. 
    - Kin: Represents the agent's core data architecture or "brain", such as a workflow-based model or an LLM (Large Language Model).
    - Tool: Refers to external utilities or tools that the agent uses to perform tasks or enhance its capabilities.
    - Trigger: Serves as the entry point for the agent, initiating processes or actions based on external inputs.
    This service manages the lifecycle and interactions of these modules, including starting, stopping, 
    and monitoring the module's status, as well as handling input and output operations.
    """

    @staticmethod
    async def StartModule(request_iterator, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target,
            '/digitalkin.module.v1.ModuleService/StartModule',
            digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.
            StartModuleRequest.SerializeToString,
            digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.
            StartModuleResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata, _registered_method=True)

    @staticmethod
    async def StopModule(request, target, options=(), channel_credentials=
        None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module.v1.ModuleService/StopModule',
            digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.
            StopModuleRequest.SerializeToString,
            digitalkin_dot_module_dot_v1_dot_lifecycle__pb2.
            StopModuleResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata, _registered_method=True)

    @staticmethod
    async def GetModuleStatus(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module.v1.ModuleService/GetModuleStatus',
            digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
            GetModuleStatusRequest.SerializeToString,
            digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
            GetModuleStatusResponse.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    async def GetModuleJobs(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module.v1.ModuleService/GetModuleJobs',
            digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
            GetModuleJobsRequest.SerializeToString,
            digitalkin_dot_module_dot_v1_dot_monitoring__pb2.
            GetModuleJobsResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata, _registered_method=True)

    @staticmethod
    async def GetModuleInput(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module.v1.ModuleService/GetModuleInput',
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleInputRequest.SerializeToString,
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleInputResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata, _registered_method=True)

    @staticmethod
    async def GetModuleOutput(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module.v1.ModuleService/GetModuleOutput',
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleOutputRequest.SerializeToString,
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleOutputResponse.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    async def GetModuleSetup(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.module.v1.ModuleService/GetModuleSetup',
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleSetupRequest.SerializeToString,
            digitalkin_dot_module_dot_v1_dot_information__pb2.
            GetModuleSetupResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata, _registered_method=True)
