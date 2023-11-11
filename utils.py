from flask_restful import Api, Resource

from pylon.core.tools import log
from .api.v1.chat_completion import ChatCompletionAPI
from .api.v1.completion import CompletionAPI
from .api.v1.models import ModelsAPI


def _add_resource_to_api(api: Api, resourse: Resource):
    module_name = 'open_ai_azure_api'
    api_version = 'v1'
    resource_name = 'api'

    resource_urls = list()
    for url_param in resourse.url_params:
        url_param = url_param.lstrip("/").rstrip("/")
        resource_urls.append(
            f"/api/{api_version}/{module_name}/{resource_name}/{url_param}"
        )
        resource_urls.append(
            f"/api/{api_version}/{module_name}/{resource_name}/{url_param}/"
        )
    api.add_resource(resourse, *resource_urls)


def init_api(api: Api):
    """ Register all API resources from this module """
    _add_resource_to_api(api, ChatCompletionAPI)
    _add_resource_to_api(api, CompletionAPI)
    _add_resource_to_api(api, ModelsAPI)
