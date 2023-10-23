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


class CompletionRequest(ExtraForbidModel):
    prompt: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[PositiveInt] = None
    temperature: Optional[Temperature] = None
    top_p: Optional[TopP] = None
    logit_bias: Optional[Mapping[int, float]] = None
    user: Optional[StrictStr] = None
    n: Optional[N] = None
    stream: bool = False
    logprobs: Optional[int] = None
    suffix: Optional[str] = None
    echo: Optional[bool] = None
    stop: Optional[Union[StrictStr, Stop]] = None
    presence_penalty: Optional[Penalty] = None
    frequency_penalty: Optional[Penalty] = None
    best_of: Optional[int] = None

    # in case we use Open AI
    model: Optional[StrictStr] = None

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
