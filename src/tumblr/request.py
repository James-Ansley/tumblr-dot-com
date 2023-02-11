import json
from io import StringIO

import requests


def post(url, auth, content, files):
    if files:
        content = StringIO(json.dumps(content))
        files = {"json": (None, content, "application/json"), **files}
        request = requests.post(url=url, auth=auth, files=files)
    else:
        request = requests.post(url=url, auth=auth, json=content)
    request.raise_for_status()
    return request.json()


def get(url, auth):
    request = requests.get(url=url, auth=auth)
    request.raise_for_status()
    return request.json()
