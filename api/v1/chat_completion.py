from json import dumps
from flask import request, Response
from flask_restful import Resource
from tools import api_tools

from ...models.pd.chat_completion_azure import ChatCompletionRequest

from tools import auth, rpc_tools, config as c

from pylon.core.tools import log


class ChatCompletionAPI(Resource):
    url_params = [
        '<string:mode>/<int:project_id>/<string:integration_uid>/openai/deployments/<string:deployment_id>/chat/completions',
        '<int:project_id>/<string:integration_uid>/openai/deployments/<string:deployment_id>/chat/completions',
    ]

    @auth.decorators.check_api({
    "permissions": ["models.open_ai_azure_api.chat_completion.post"],
    "recommended_roles": {
        c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": False},
        c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": False},
    }})
    def post(self, project_id: int, integration_uid: str, deployment_id: str, **kwargs):
        payload = dict(request.json)
        AIProvider = rpc_tools.RpcMixin().rpc.call.prompts_get_ai_provider()

        payload['project_id'] = project_id
        payload['integration_uid'] = integration_uid
        payload['deployment_id'] = deployment_id
        try:
            request_data = ChatCompletionRequest.parse_obj(payload)
        except Exception as e:
            log.error("Validation Request Model Error")
            log.error(str(e))
            return {"error": str(e)}, 400

        try:
            integration = AIProvider.get_integration(
                project_id=project_id,
                integration_uid=request_data.integration_uid,
            )

        except Exception as e:
            log.error("AIProvider Error")
            log.error(str(e))
            return str(e), 400

        request_data = request_data.dict(exclude_unset=True)

        result = AIProvider.chat_completion(project_id, integration, request_data)
        if not result['ok']:
            log.error("Completion Response Error")
            log.error(str(result['error']))
            return str(result['error']), 400

        if request_data.get('stream'):
            stream = lambda resp: ('data: {chunk}\n\n'.format(chunk=dumps(item)) for item in resp)
            return Response(stream(result['response']), mimetype='text/event-stream')

        return result['response'], 200
