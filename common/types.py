from __future__ import annotations
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from enum import Enum

# ------------------------------
# Enums
# ------------------------------

class TaskMode(str, Enum):
    STANDARD = 'standard'
    STREAMING = 'streaming'


class TaskStatus(str, Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELED = 'canceled'


# ------------------------------
# Core Models
# ------------------------------

class TaskSendParams(BaseModel):
    id: str
    sessionId: str
    message: str  # or more specific type depending on your context

class TaskQueryParams(BaseModel):
    id: str
    historyLength: int | None = None

class TaskIdParams(BaseModel):
    task_id: str
    
class Output(BaseModel):
    name: str
    value: str

class Artifact(BaseModel):
    name: str
    path: str

class PushNotificationConfig(BaseModel):
    acceptedOutputModes: list[str]

class TaskPushNotificationConfig(BaseModel):
    id: str
    pushNotificationConfig: PushNotificationConfig

class SendTaskStreamingResponse(BaseModel):
    message: str
    isFinal: bool = False

# ------------------------------
# Task Models
# ------------------------------

class Task(BaseModel):
    taskId: str
    name: str
    inputs: list[Output] = Field(default_factory=list)
    outputs: list[Output] = Field(default_factory=list)
    status: TaskStatus
    logs: list[str] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    taskId: str
    outputs: list[Output] = Field(default_factory=list)
    status: TaskStatus | None = None
    logs: list[str] = Field(default_factory=list)


class TaskArtifactUpdate(BaseModel):
    taskId: str
    artifacts: list[Artifact] = Field(default_factory=list)


# ------------------------------
# JSON-RPC Base Classes
# ------------------------------

class JsonRpcRequest(BaseModel):
    jsonrpc: Literal['2.0']
    method: str
    id: str
    sessionId: str | None = Field(default=None)

    @model_validator(mode='before')
    @classmethod
    def set_defaults(cls, data):
        data['jsonrpc'] = '2.0'
        return data


class JsonRpcResponse(BaseModel):
    jsonrpc: Literal['2.0'] = Field(default='2.0')
    id: str


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: dict | None = Field(default=None)


# ------------------------------
# Specific Request Models
# ------------------------------

class CancelTaskResponse(JsonRpcResponse):
    result: Task | None = None
    error: JsonRpcError | None = None

class SendTaskResponse(JsonRpcResponse):
    result: Task
    error: JsonRpcError | None = None

class SetTaskPushNotificationResponse(JsonRpcResponse):
    result: TaskPushNotificationConfig
    error: JsonRpcError | None = None

class SendTaskRequest(JsonRpcRequest):
    method: Literal['sendTask']
    task: Task
    mode: TaskMode = Field(default=TaskMode.STANDARD)


class SendTaskStreamingRequest(JsonRpcRequest):
    method: Literal['sendTaskStreaming']
    task: Task


class GetTaskRequest(JsonRpcRequest):
    method: Literal['getTask']
    taskId: str


class CancelTaskRequest(JsonRpcRequest):
    method: Literal['cancelTask']
    taskId: str


class SetTaskPushNotificationRequest(JsonRpcRequest):
    method: Literal['setTaskPushNotification']
    acceptedOutputModes: list[str]


class GetTaskPushNotificationRequest(JsonRpcRequest):
    method: Literal['getTaskPushNotification']


class TaskResubscriptionRequest(JsonRpcRequest):
    method: Literal['taskResubscription']


# ------------------------------
# Specific Response Models
# ------------------------------

class GetTaskResponse(JsonRpcResponse):
    result: Task


class GetTaskPushNotificationResponse(JsonRpcResponse):
    result: list[str]


# ------------------------------
# Error Response
# ------------------------------

class JsonRpcErrorResponse(JsonRpcResponse):
    error: JsonRpcError


# ------------------------------
# Server → Client Notifications
# ------------------------------

class TaskUpdateNotification(BaseModel):
    jsonrpc: Literal['2.0'] = Field(default='2.0')
    method: Literal['taskUpdate']
    params: TaskUpdate


class TaskArtifactUpdateNotification(BaseModel):
    jsonrpc: Literal['2.0'] = Field(default='2.0')
    method: Literal['taskArtifactUpdate']
    params: TaskArtifactUpdate


# ------------------------------
# Event Streaming Support
# ------------------------------

class TaskEvent(BaseModel):
    taskId: str
    timestamp: datetime = Field(default_factory=datetime.now)


class TaskStatusUpdateEvent(TaskEvent):
    status: TaskStatus


class TaskLogUpdateEvent(TaskEvent):
    logs: list[str]


class TaskArtifactUpdateEvent(TaskEvent):
    artifacts: list[Artifact]


class TaskOutputUpdateEvent(TaskEvent):
    outputs: list[Output]


# ------------------------------
# Custom Exceptions
# ------------------------------

class TaskNotFoundError(Exception):
    """Raised when a task is not found."""
    def __init__(self, message: str = "The requested task was not found."):
        super().__init__(message)

class TaskNotCancelableError(Exception):
    """Raised when a task cannot be cancelled."""
    def __init__(self, message: str = "The task cannot be canceled."):
        super().__init__(message)

class PushNotificationNotSupportedError(Exception):
    code = -32000
    message = "Push notifications are not supported."

class ContentTypeNotSupportedError(Exception):
    pass

class UnsupportedOperationError(Exception):
    pass

class InternalError(Exception):
    pass

# ------------------------------
# Union/Discriminator Models
# ------------------------------

# RequestTypes is now cleaner and centralized
RequestTypes = Annotated[
    SendTaskRequest
    | GetTaskRequest
    | CancelTaskRequest
    | SetTaskPushNotificationRequest
    | GetTaskPushNotificationRequest
    | TaskResubscriptionRequest
    | SendTaskStreamingRequest,
    Field(discriminator='method'),
]

# Used for dynamic request parsing
from pydantic import TypeAdapter
A2ARequest = TypeAdapter(RequestTypes)

JSONRPCError = JsonRpcError 