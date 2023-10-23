from flask import request, Response
from tools import api_tools

from ...models.pd.chat_completion_azure import ChatCompletionRequest
from ...models.pd.completion_azure import CompletionRequest

from tools import db, auth, rpc_tools, config as c

from pylon.core.tools import log


class ProjectAPI(api_tools.APIModeHandler):
    @auth.decorators.check_api({
        "permissions": ["models.open_ai_azure_api.api.post"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": False},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": False},
        }})
    @api_tools.endpoint_metrics
    def post(self, project_id: int, integration_uid: str, deployment_id: str):
        payload = dict(request.json)
        AIProvider = rpc_tools.RpcMixin().rpc.call.prompts_get_ai_provider()

        if request.path.endswith('/chat/completions'):
            validation_model = ChatCompletionRequest
            completion_function = AIProvider.chat_completion
        else:
            validation_model = CompletionRequest
            completion_function = AIProvider.completion

        payload['project_id'] = project_id
        payload['integration_uid'] = integration_uid
        payload['deployment_id'] = deployment_id
        try:
            request_data = validation_model.parse_obj(payload)
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

        result = completion_function(project_id, integration, request_data)
        if not result['ok']:
            log.error("Completion Response Error")
            log.error(str(result['error']))
            return str(result['error']), 400

        if request_data['stream']:
            stream = lambda resp: (f'data: {chunk}\n\n' for chunk in resp)
            return Response(stream(result['response']), mimetype='text/event-stream')

        return result['response'], 200


class API(api_tools.APIBase):
    url_params = [
        # '<string:mode>/<int:project_id>/<string:integration_uid>/openai/models',
        # '<int:project_id>/<string:integration_uid>/openai/models',
        '<string:mode>/<int:project_id>/<string:integration_uid>/openai/deployments/<string:deployment_id>/chat/completions',
        '<int:project_id>/<string:integration_uid>/openai/deployments/<string:deployment_id>/chat/completions',
        '<string:mode>/<int:project_id>/<string:integration_uid>/openai/deployments/<string:deployment_id>/completions',
        '<int:project_id>/<string:integration_uid>/openai/deployments/<string:deployment_id>/completions',
    ]

    mode_handlers = {
        c.DEFAULT_MODE: ProjectAPI,
    }
