from flask_restful import Resource
from tools import api_tools

from tools import auth, rpc_tools, config as c

from pylon.core.tools import log


class ModelsAPI(Resource):
    url_params = [
        '<string:mode>/<int:project_id>/<string:integration_uid>/openai/models',
        '<int:project_id>/<string:integration_uid>/openai/models',
        '<string:mode>/<int:project_id>/<string:integration_uid>/openai/models/<string:model_name>',
        '<int:project_id>/<string:integration_uid>/openai/models/<string:model_name>',
        '<string:mode>/<int:project_id>/<string:integration_uid>/openai/deployments',
        '<int:project_id>/<string:integration_uid>/openai/deployments',
        '<string:mode>/<int:project_id>/<string:integration_uid>/openai/deployments/<string:model_name>',
        '<int:project_id>/<string:integration_uid>/openai/deployments/<string:model_name>',
    ]

    @auth.decorators.check_api({
    "permissions": ["models.open_ai_azure_api.models.get"],
    "recommended_roles": {
        c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": False},
        c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": False},
    }})
    def get(self, project_id: int, integration_uid: str, model_name: str = None, **kwargs):
        AIProvider = rpc_tools.RpcMixin().rpc.call.prompts_get_ai_provider()
        try:
            integration = AIProvider.get_integration(
                project_id=project_id,
                integration_uid=integration_uid,
            )
            if model_name:
                models = next((model for model in integration.settings.get('models') if model['name'] == model_name), {})
            else:
                models = integration.settings.get('models')
            return {'data': models}
        except Exception as e:
            log.error("AIProvider Error")
            log.error(str(e))
            return str(e), 400
