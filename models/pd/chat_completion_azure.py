from enum import Enum
from typing import Optional, List, Union, Any, Mapping

from pydantic import (
    BaseModel,
    StrictStr,
    ConstrainedFloat,
    ConstrainedInt,
    ConstrainedList,
    PositiveInt,
    root_validator,
)
from pylon.core.tools import log
from tools import rpc_tools


class ExtraForbidModel(BaseModel):
    class Config:
        extra = "forbid"


class Attachment(ExtraForbidModel):
    type: Optional[StrictStr] = "text/markdown"
    title: Optional[StrictStr] = None
    data: Optional[StrictStr] = None
    url: Optional[StrictStr] = None
    reference_type: Optional[StrictStr] = None
    reference_url: Optional[StrictStr] = None


class CustomContent(ExtraForbidModel):
    attachments: Optional[List[Attachment]] = None
    state: Optional[Any] = None


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class FunctionCall(ExtraForbidModel):
    name: str
    arguments: str


class Message(ExtraForbidModel):
    role: Role
    content: Optional[StrictStr] = None
    custom_content: Optional[CustomContent] = None
    name: Optional[StrictStr] = None
    function_call: Optional[FunctionCall] = None


class Addon(ExtraForbidModel):
    name: Optional[StrictStr] = None
    url: Optional[StrictStr] = None


class Function(ExtraForbidModel):
    name: StrictStr
    description: StrictStr
    parameters: StrictStr


class Temperature(ConstrainedFloat):
    ge = 0
    le = 2


class TopP(ConstrainedFloat):
    ge = 0
    le = 1

class TopK(ConstrainedFloat):
    ge = 1
    le = 40

class N(ConstrainedInt):
    ge = 1
    le = 128


class Stop(ConstrainedList):
    max_items: int = 4
    __args__ = tuple([StrictStr])


class Penalty(ConstrainedFloat):
    ge = -2
    le = 2


class ChatCompletionRequest(ExtraForbidModel):
    model: Optional[StrictStr] = None
    messages: List[Message]
    functions: Optional[List[Function]] = None
    function_call: Optional[Union[StrictStr, Mapping[StrictStr, StrictStr]]] = None
    stream: bool = False
    temperature: Optional[Temperature] = None
    top_p: Optional[TopP] = None
    n: Optional[N] = None
    stop: Optional[Union[StrictStr, Stop]] = None
    max_tokens: Optional[PositiveInt] = None
    presence_penalty: Optional[Penalty] = None
    frequency_penalty: Optional[Penalty] = None
    logit_bias: Optional[Mapping[int, float]] = None
    user: Optional[StrictStr] = None

    # in case we use AI Dial
    addons: Optional[List[Addon]] = None

    # in case we use Vertex AI
    top_k: Optional[TopK] = None
    stop_sequences: Optional[List[str]] = None
    max_output_tokens: Optional[PositiveInt] = None

    deployment_id: StrictStr
    project_id: Optional[int] = None
    integration_uid: StrictStr
    integration_settings: Optional[dict] = {}

    @root_validator
    def check_settings(cls, values: dict):
        project_id, integration_uid = values['project_id'], values['integration_uid']
        AIProvider = rpc_tools.RpcMixin().rpc.call.prompts_get_ai_provider()

        integration = AIProvider.get_integration(project_id, integration_uid)
        model_settings = values['integration_settings']
        response = AIProvider.parse_settings(integration, model_settings)

        if not response['ok']:
            error = response['error']
            raise error

        values['integration_settings'] = response['item']

        return values
