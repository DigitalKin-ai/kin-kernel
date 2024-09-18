"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from proto.digitalkin.setup.v2 import setup_pb2 as digitalkin_dot_setup_dot_v2_dot_setup__pb2


class SetupServiceStub(object):
    """SetupService
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetNodeSetup = channel.unary_unary(
            '/digitalkin.setup.v2.SetupService/GetNodeSetup',
            request_serializer=digitalkin_dot_setup_dot_v2_dot_setup__pb2.
            GetNodeSetupRequest.SerializeToString, response_deserializer=
            digitalkin_dot_setup_dot_v2_dot_setup__pb2.GetNodeSetupResponse
            .FromString, _registered_method=True)
        self.ReadSetup = channel.unary_unary(
            '/digitalkin.setup.v2.SetupService/ReadSetup',
            request_serializer=digitalkin_dot_setup_dot_v2_dot_setup__pb2.
            ReadSetupRequest.SerializeToString, response_deserializer=
            digitalkin_dot_setup_dot_v2_dot_setup__pb2.ReadSetupResponse.
            FromString, _registered_method=True)


class SetupServiceServicer(object):
    """SetupService
    """

    async def GetNodeSetup(self, request, context):
        """GetNodeSetup
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def ReadSetup(self, request, context):
        """ReadSetup
        This route is used to get a setup by its ID.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SetupServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetNodeSetup': grpc.
        unary_unary_rpc_method_handler(servicer.GetNodeSetup,
        request_deserializer=digitalkin_dot_setup_dot_v2_dot_setup__pb2.
        GetNodeSetupRequest.FromString, response_serializer=
        digitalkin_dot_setup_dot_v2_dot_setup__pb2.GetNodeSetupResponse.
        SerializeToString), 'ReadSetup': grpc.
        unary_unary_rpc_method_handler(servicer.ReadSetup,
        request_deserializer=digitalkin_dot_setup_dot_v2_dot_setup__pb2.
        ReadSetupRequest.FromString, response_serializer=
        digitalkin_dot_setup_dot_v2_dot_setup__pb2.ReadSetupResponse.
        SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler(
        'digitalkin.setup.v2.SetupService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('digitalkin.setup.v2.SetupService',
        rpc_method_handlers)


class SetupService(object):
    """SetupService
    """

    @staticmethod
    async def GetNodeSetup(request, target, options=(), channel_credentials
        =None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.setup.v2.SetupService/GetNodeSetup',
            digitalkin_dot_setup_dot_v2_dot_setup__pb2.GetNodeSetupRequest.
            SerializeToString, digitalkin_dot_setup_dot_v2_dot_setup__pb2.
            GetNodeSetupResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata, _registered_method=True)

    @staticmethod
    async def ReadSetup(request, target, options=(), channel_credentials=
        None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.setup.v2.SetupService/ReadSetup',
            digitalkin_dot_setup_dot_v2_dot_setup__pb2.ReadSetupRequest.
            SerializeToString, digitalkin_dot_setup_dot_v2_dot_setup__pb2.
            ReadSetupResponse.FromString, options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready,
            timeout, metadata, _registered_method=True)
