#coding=utf-8

import requests
from .tools import initDataFromDB

def action(data):
    req_method = data["method"]
    if req_method == "GET":
        resp = requests.get(url=data["url"],params=data["data"])
    elif req_method == "POST":
        resp = requests.post(url=data["url"], data=data["data"])
    return resp.ok








