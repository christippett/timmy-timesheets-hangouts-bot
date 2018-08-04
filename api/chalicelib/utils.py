import re
import logging


def get_base_url(current_request, path=None):
    headers = current_request.headers
    proto = headers.get('x-forwarded-proto', 'http')
    host = headers.get('host')
    stage = current_request.context.get('stage', '')
    path = path or ''
    url_path = re.sub(r'/{2,}', '/', f'{host}/{stage}/{path}')
    return f'{proto}://{url_path}'


def get_current_url(current_request, params=True):
    headers = current_request.headers
    proto = headers.get('x-forwarded-proto', 'http')
    host = headers.get('host')
    stage = current_request.context.get('stage', '')
    resource_path = current_request.context.get('resourcePath', '')
    url_path = re.sub(r'/{2,}', '/', f'{host}/{stage}/{resource_path}')
    query_params = current_request.query_params
    print(f'HOST: {host}')
    print(f'RESOURCE_PATH: {resource_path}')
    print(f'STAGE: {stage}')
    if params and query_params:
        query_params_string = '&'.join([f'{k}={v}' for k, v in query_params.items()])
        if query_params_string:
            return f'{proto}://{url_path}?{query_params_string}'
    return f'{proto}://{url_path}'
