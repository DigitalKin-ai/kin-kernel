"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from digitalkin.common.v1 import common_pb2 as digitalkin_dot_common_dot_v1_dot_common__pb2
from digitalkin.project.v1 import activity_pb2 as digitalkin_dot_project_dot_v1_dot_activity__pb2
from digitalkin.project.v1 import edge_pb2 as digitalkin_dot_project_dot_v1_dot_edge__pb2
from digitalkin.project.v1 import kin_pb2 as digitalkin_dot_project_dot_v1_dot_kin__pb2
from digitalkin.project.v1 import message_pb2 as digitalkin_dot_project_dot_v1_dot_message__pb2
from digitalkin.project.v1 import node_pb2 as digitalkin_dot_project_dot_v1_dot_node__pb2
from digitalkin.project.v1 import thread_pb2 as digitalkin_dot_project_dot_v1_dot_thread__pb2
from digitalkin.project.v1 import workflow_pb2 as digitalkin_dot_project_dot_v1_dot_workflow__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


class ProjectServiceStub(object):
    """ProjectService
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ReadKin = channel.unary_stream(
            '/digitalkin.project.v1.ProjectService/ReadKin',
            request_serializer=digitalkin_dot_project_dot_v1_dot_kin__pb2.
            ReadKinRequest.SerializeToString, response_deserializer=
            digitalkin_dot_project_dot_v1_dot_kin__pb2.Kin.FromString,
            _registered_method=True)
        self.ReadActivities = channel.unary_stream(
            '/digitalkin.project.v1.ProjectService/ReadActivities',
            request_serializer=
            digitalkin_dot_project_dot_v1_dot_activity__pb2.
            ReadActivitiesRequest.SerializeToString, response_deserializer=
            digitalkin_dot_project_dot_v1_dot_activity__pb2.Activities.
            FromString, _registered_method=True)
        self.UpdateOriginAddress = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/UpdateOriginAddress',
            request_serializer=digitalkin_dot_project_dot_v1_dot_kin__pb2.
            UpdateKinOriginAddressRequest.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.
            FromString, _registered_method=True)
        self.CreateMessage = channel.unary_stream(
            '/digitalkin.project.v1.ProjectService/CreateMessage',
            request_serializer=
            digitalkin_dot_project_dot_v1_dot_message__pb2.MessageRequest.
            SerializeToString, response_deserializer=
            digitalkin_dot_project_dot_v1_dot_message__pb2.MessageResponse.
            FromString, _registered_method=True)
        self.CreateThread = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/CreateThread',
            request_serializer=
            digitalkin_dot_project_dot_v1_dot_thread__pb2.
            CreateThreadRequest.SerializeToString, response_deserializer=
            digitalkin_dot_common_dot_v1_dot_common__pb2.ThreadReply.
            FromString, _registered_method=True)
        self.ReadThread = channel.unary_stream(
            '/digitalkin.project.v1.ProjectService/ReadThread',
            request_serializer=
            digitalkin_dot_project_dot_v1_dot_thread__pb2.ReadThreadRequest
            .SerializeToString, response_deserializer=
            digitalkin_dot_project_dot_v1_dot_thread__pb2.Thread.FromString,
            _registered_method=True)
        self.DeleteThread = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/DeleteThread',
            request_serializer=
            digitalkin_dot_project_dot_v1_dot_thread__pb2.
            DeleteThreadRequest.SerializeToString, response_deserializer=
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            _registered_method=True)
        self.CreateWorkflow = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/CreateWorkflow',
            request_serializer=
            digitalkin_dot_project_dot_v1_dot_workflow__pb2.
            CreateWorkflowRequest.SerializeToString, response_deserializer=
            digitalkin_dot_common_dot_v1_dot_common__pb2.WorkflowReply.
            FromString, _registered_method=True)
        self.ReadWorkflow = channel.unary_stream(
            '/digitalkin.project.v1.ProjectService/ReadWorkflow',
            request_serializer=
            digitalkin_dot_project_dot_v1_dot_workflow__pb2.
            ReadWorkflowRequest.SerializeToString, response_deserializer=
            digitalkin_dot_project_dot_v1_dot_workflow__pb2.Workflow.
            FromString, _registered_method=True)
        self.ReadDataNodesList = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/ReadDataNodesList',
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.
            SerializeToString, response_deserializer=
            digitalkin_dot_project_dot_v1_dot_node__pb2.
            ReadDataNodesListResponse.FromString, _registered_method=True)
        self.AddNodeWorkflow = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/AddNodeWorkflow',
            request_serializer=digitalkin_dot_project_dot_v1_dot_node__pb2.
            AddNodeWorkflowRequest.SerializeToString, response_deserializer
            =google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            _registered_method=True)
        self.UpdateNodePositionWorkflow = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/UpdateNodePositionWorkflow',
            request_serializer=digitalkin_dot_project_dot_v1_dot_node__pb2.
            UpdateNodePositionWorkflowRequest.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.
            FromString, _registered_method=True)
        self.DeleteNodeWorkflow = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/DeleteNodeWorkflow',
            request_serializer=digitalkin_dot_project_dot_v1_dot_node__pb2.
            DeleteNodeWorkflowRequest.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.
            FromString, _registered_method=True)
        self.AddEdgeWorkflow = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/AddEdgeWorkflow',
            request_serializer=digitalkin_dot_project_dot_v1_dot_edge__pb2.
            AddEdgeWorkflowRequest.SerializeToString, response_deserializer
            =google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            _registered_method=True)
        self.DeleteEdgeWorkflow = channel.unary_unary(
            '/digitalkin.project.v1.ProjectService/DeleteEdgeWorkflow',
            request_serializer=digitalkin_dot_project_dot_v1_dot_edge__pb2.
            DeleteEdgeWorkflowRequest.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.
            FromString, _registered_method=True)


class ProjectServiceServicer(object):
    """ProjectService
    """

    def ReadKin(self, request, context):
        """ReadKin

        Parameters:

        - kin_id: Kin id

        Returns:

        - Kin
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReadActivities(self, request, context):
        """ReadActivities

        Parameters:

        - optional kin_id: Kin id

        Returns:

        - Activities
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateOriginAddress(self, request, context):
        """UpdateOriginAddress

        Parameters:

        - kin_id: Kin id
        - origin_address: Kin origin address

        Returns:

        - Nothing
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateMessage(self, request, context):
        """CreateMessage

        Parameters:

        - thread_id: Kin thread id
        - message: Message
        - prompt: Prompt

        Returns:

        - MessageResponse
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateThread(self, request, context):
        """CreateThread

        Parameters:

        - kin_id: Kin id

        Returns:

        - ThreadResponse
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReadThread(self, request, context):
        """ReadThread

        Parameters:

        - thread_id: thread id

        Returns:

        - Thread
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteThread(self, request, context):
        """DeleteThread

        Parameters:

        - thread_id: thread id

        Returns:

        - Nothing
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateWorkflow(self, request, context):
        """CreateWorkflow

        Parameters:

        - kin_id: Kin id
        - optional workflow: Workflow to duplicate

        Returns:

        - WorkflowReply
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    async def ReadWorkflow(self, request, context):
        """ReadWorkflow

        Parameters:

        - kin_id: Kin id

        Returns:

        - Workflow
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReadDataNodesList(self, request, context):
        """ReadDataNodesList

        ## Parameters

        - Nothing

        ## Returns

        - ReadDataNodesListResponse
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddNodeWorkflow(self, request, context):
        """AddNodeWorkflow

        Parameters:

        - kin_id: Kin id
        - node: Node

        Returns:

        - Nothing
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateNodePositionWorkflow(self, request, context):
        """UpdateNodePositionWorkflow

        Parameters:

        - kin_id: Kin id
        - node_id: Node id
        - position: Position

        Returns:

        - Nothing
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteNodeWorkflow(self, request, context):
        """DeleteNodeWorkflow

        Parameters:

        - kin_id: Kin id
        - node_id: Node id

        Returns:

        - Nothing
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddEdgeWorkflow(self, request, context):
        """AddEdgeWorkflow

        Parameters:

        - kin_id: Kin id
        - edge: Edge

        Returns:

        - Nothing
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteEdgeWorkflow(self, request, context):
        """DeleteEdgeWorkflow

        Parameters:

        - kin_id: Kin id
        - edge_id: Edge id

        Returns:

        - Nothing
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ProjectServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'ReadKin': grpc.unary_stream_rpc_method_handler(
        servicer.ReadKin, request_deserializer=
        digitalkin_dot_project_dot_v1_dot_kin__pb2.ReadKinRequest.
        FromString, response_serializer=
        digitalkin_dot_project_dot_v1_dot_kin__pb2.Kin.SerializeToString),
        'ReadActivities': grpc.unary_stream_rpc_method_handler(servicer.
        ReadActivities, request_deserializer=
        digitalkin_dot_project_dot_v1_dot_activity__pb2.
        ReadActivitiesRequest.FromString, response_serializer=
        digitalkin_dot_project_dot_v1_dot_activity__pb2.Activities.
        SerializeToString), 'UpdateOriginAddress': grpc.
        unary_unary_rpc_method_handler(servicer.UpdateOriginAddress,
        request_deserializer=digitalkin_dot_project_dot_v1_dot_kin__pb2.
        UpdateKinOriginAddressRequest.FromString, response_serializer=
        google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString),
        'CreateMessage': grpc.unary_stream_rpc_method_handler(servicer.
        CreateMessage, request_deserializer=
        digitalkin_dot_project_dot_v1_dot_message__pb2.MessageRequest.
        FromString, response_serializer=
        digitalkin_dot_project_dot_v1_dot_message__pb2.MessageResponse.
        SerializeToString), 'CreateThread': grpc.
        unary_unary_rpc_method_handler(servicer.CreateThread,
        request_deserializer=digitalkin_dot_project_dot_v1_dot_thread__pb2.
        CreateThreadRequest.FromString, response_serializer=
        digitalkin_dot_common_dot_v1_dot_common__pb2.ThreadReply.
        SerializeToString), 'ReadThread': grpc.
        unary_stream_rpc_method_handler(servicer.ReadThread,
        request_deserializer=digitalkin_dot_project_dot_v1_dot_thread__pb2.
        ReadThreadRequest.FromString, response_serializer=
        digitalkin_dot_project_dot_v1_dot_thread__pb2.Thread.
        SerializeToString), 'DeleteThread': grpc.
        unary_unary_rpc_method_handler(servicer.DeleteThread,
        request_deserializer=digitalkin_dot_project_dot_v1_dot_thread__pb2.
        DeleteThreadRequest.FromString, response_serializer=
        google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString),
        'CreateWorkflow': grpc.unary_unary_rpc_method_handler(servicer.
        CreateWorkflow, request_deserializer=
        digitalkin_dot_project_dot_v1_dot_workflow__pb2.
        CreateWorkflowRequest.FromString, response_serializer=
        digitalkin_dot_common_dot_v1_dot_common__pb2.WorkflowReply.
        SerializeToString), 'ReadWorkflow': grpc.
        unary_stream_rpc_method_handler(servicer.ReadWorkflow,
        request_deserializer=
        digitalkin_dot_project_dot_v1_dot_workflow__pb2.ReadWorkflowRequest
        .FromString, response_serializer=
        digitalkin_dot_project_dot_v1_dot_workflow__pb2.Workflow.
        SerializeToString), 'ReadDataNodesList': grpc.
        unary_unary_rpc_method_handler(servicer.ReadDataNodesList,
        request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.
        FromString, response_serializer=
        digitalkin_dot_project_dot_v1_dot_node__pb2.
        ReadDataNodesListResponse.SerializeToString), 'AddNodeWorkflow':
        grpc.unary_unary_rpc_method_handler(servicer.AddNodeWorkflow,
        request_deserializer=digitalkin_dot_project_dot_v1_dot_node__pb2.
        AddNodeWorkflowRequest.FromString, response_serializer=
        google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString),
        'UpdateNodePositionWorkflow': grpc.unary_unary_rpc_method_handler(
        servicer.UpdateNodePositionWorkflow, request_deserializer=
        digitalkin_dot_project_dot_v1_dot_node__pb2.
        UpdateNodePositionWorkflowRequest.FromString, response_serializer=
        google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString),
        'DeleteNodeWorkflow': grpc.unary_unary_rpc_method_handler(servicer.
        DeleteNodeWorkflow, request_deserializer=
        digitalkin_dot_project_dot_v1_dot_node__pb2.
        DeleteNodeWorkflowRequest.FromString, response_serializer=
        google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString),
        'AddEdgeWorkflow': grpc.unary_unary_rpc_method_handler(servicer.
        AddEdgeWorkflow, request_deserializer=
        digitalkin_dot_project_dot_v1_dot_edge__pb2.AddEdgeWorkflowRequest.
        FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.
        Empty.SerializeToString), 'DeleteEdgeWorkflow': grpc.
        unary_unary_rpc_method_handler(servicer.DeleteEdgeWorkflow,
        request_deserializer=digitalkin_dot_project_dot_v1_dot_edge__pb2.
        DeleteEdgeWorkflowRequest.FromString, response_serializer=
        google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler(
        'digitalkin.project.v1.ProjectService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers(
        'digitalkin.project.v1.ProjectService', rpc_method_handlers)


class ProjectService(object):
    """ProjectService
    """

    @staticmethod
    def ReadKin(request, target, options=(), channel_credentials=None,
        call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target,
            '/digitalkin.project.v1.ProjectService/ReadKin',
            digitalkin_dot_project_dot_v1_dot_kin__pb2.ReadKinRequest.
            SerializeToString, digitalkin_dot_project_dot_v1_dot_kin__pb2.
            Kin.FromString, options, channel_credentials, insecure,
            call_credentials, compression, wait_for_ready, timeout,
            metadata, _registered_method=True)

    @staticmethod
    def ReadActivities(request, target, options=(), channel_credentials=
        None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target,
            '/digitalkin.project.v1.ProjectService/ReadActivities',
            digitalkin_dot_project_dot_v1_dot_activity__pb2.
            ReadActivitiesRequest.SerializeToString,
            digitalkin_dot_project_dot_v1_dot_activity__pb2.Activities.
            FromString, options, channel_credentials, insecure,
            call_credentials, compression, wait_for_ready, timeout,
            metadata, _registered_method=True)

    @staticmethod
    def UpdateOriginAddress(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/UpdateOriginAddress',
            digitalkin_dot_project_dot_v1_dot_kin__pb2.
            UpdateKinOriginAddressRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def CreateMessage(request, target, options=(), channel_credentials=None,
        call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target,
            '/digitalkin.project.v1.ProjectService/CreateMessage',
            digitalkin_dot_project_dot_v1_dot_message__pb2.MessageRequest.
            SerializeToString,
            digitalkin_dot_project_dot_v1_dot_message__pb2.MessageResponse.
            FromString, options, channel_credentials, insecure,
            call_credentials, compression, wait_for_ready, timeout,
            metadata, _registered_method=True)

    @staticmethod
    def CreateThread(request, target, options=(), channel_credentials=None,
        call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/CreateThread',
            digitalkin_dot_project_dot_v1_dot_thread__pb2.
            CreateThreadRequest.SerializeToString,
            digitalkin_dot_common_dot_v1_dot_common__pb2.ThreadReply.
            FromString, options, channel_credentials, insecure,
            call_credentials, compression, wait_for_ready, timeout,
            metadata, _registered_method=True)

    @staticmethod
    def ReadThread(request, target, options=(), channel_credentials=None,
        call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target,
            '/digitalkin.project.v1.ProjectService/ReadThread',
            digitalkin_dot_project_dot_v1_dot_thread__pb2.ReadThreadRequest
            .SerializeToString,
            digitalkin_dot_project_dot_v1_dot_thread__pb2.Thread.FromString,
            options, channel_credentials, insecure, call_credentials,
            compression, wait_for_ready, timeout, metadata,
            _registered_method=True)

    @staticmethod
    def DeleteThread(request, target, options=(), channel_credentials=None,
        call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/DeleteThread',
            digitalkin_dot_project_dot_v1_dot_thread__pb2.
            DeleteThreadRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def CreateWorkflow(request, target, options=(), channel_credentials=
        None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/CreateWorkflow',
            digitalkin_dot_project_dot_v1_dot_workflow__pb2.
            CreateWorkflowRequest.SerializeToString,
            digitalkin_dot_common_dot_v1_dot_common__pb2.WorkflowReply.
            FromString, options, channel_credentials, insecure,
            call_credentials, compression, wait_for_ready, timeout,
            metadata, _registered_method=True)

    @staticmethod
    async def ReadWorkflow(request, target, options=(), channel_credentials
        =None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target,
            '/digitalkin.project.v1.ProjectService/ReadWorkflow',
            digitalkin_dot_project_dot_v1_dot_workflow__pb2.
            ReadWorkflowRequest.SerializeToString,
            digitalkin_dot_project_dot_v1_dot_workflow__pb2.Workflow.
            FromString, options, channel_credentials, insecure,
            call_credentials, compression, wait_for_ready, timeout,
            metadata, _registered_method=True)

    @staticmethod
    def ReadDataNodesList(request, target, options=(), channel_credentials=
        None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/ReadDataNodesList',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            digitalkin_dot_project_dot_v1_dot_node__pb2.
            ReadDataNodesListResponse.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddNodeWorkflow(request, target, options=(), channel_credentials=
        None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/AddNodeWorkflow',
            digitalkin_dot_project_dot_v1_dot_node__pb2.
            AddNodeWorkflowRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdateNodePositionWorkflow(request, target, options=(),
        channel_credentials=None, call_credentials=None, insecure=False,
        compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/UpdateNodePositionWorkflow',
            digitalkin_dot_project_dot_v1_dot_node__pb2.
            UpdateNodePositionWorkflowRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def DeleteNodeWorkflow(request, target, options=(), channel_credentials
        =None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/DeleteNodeWorkflow',
            digitalkin_dot_project_dot_v1_dot_node__pb2.
            DeleteNodeWorkflowRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddEdgeWorkflow(request, target, options=(), channel_credentials=
        None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/AddEdgeWorkflow',
            digitalkin_dot_project_dot_v1_dot_edge__pb2.
            AddEdgeWorkflowRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def DeleteEdgeWorkflow(request, target, options=(), channel_credentials
        =None, call_credentials=None, insecure=False, compression=None,
        wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target,
            '/digitalkin.project.v1.ProjectService/DeleteEdgeWorkflow',
            digitalkin_dot_project_dot_v1_dot_edge__pb2.
            DeleteEdgeWorkflowRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString, options,
            channel_credentials, insecure, call_credentials, compression,
            wait_for_ready, timeout, metadata, _registered_method=True)
