#!/usr/bin/python3 -i
# -*- coding: utf-8 -*-

import requests, json

janus_url = "http://localhost:8088/janus"
mountpoint_id = "Ababagalamaga"
session_id = None
handle_id = None
ports = None

# Older requsests lack normal JSON POST
def mypost(url, json_v):
    return requests.request("POST", url, data=json.dumps(json_v), headers={ "Content-Type" : "application/json" })

# TODO maybe some decorator here?
def janus_cmd(cmd, cond = False, action = lambda x: x ):
    if cond:
        print("misplaced call!")
    else:
        r = mypost(janus_url, cmd)
        if not r:
            print("error in communication!")
        else:
            j = r.json()
            print(j)
            action(j)

def greet():
    def helper(j):
        global session_id
        session_id = j["data"]["id"]
    janus_cmd({ "janus": "create",
                "transaction": "tester.py"}, action = helper)

def keepalive():
    janus_cmd({ "janus": "keepalive",
                "transaction": "tester.py",
                "session_id": session_id }, not session_id)

def attach(plugin = "janus.plugin.cm.rtpbroadcast"):
    def helper(j):
        global handle_id
        handle_id = j["data"]["id"]
    janus_cmd({ "janus": "attach",
                "plugin": plugin,
                "transaction": "tester.py",
                "session_id": session_id }, not session_id, helper)

def list():
    janus_cmd({ "janus": "message",
                "transaction": "tester.py",
                "session_id": session_id,
                "handle_id": handle_id,
                "body": {
                    "request": "list"
                } }, not session_id or not handle_id)

def create(id=mountpoint_id):
    def helper(j):
        global ports
        ports = []
        for i in j["plugindata"]["data"]["stream"]["streams"]:
            ports.append(i["audioport"])
            ports.append(i["videoport"])
    janus_cmd({ "janus": "message",
                "transaction": "tester.py",
                "session_id": session_id,
                "handle_id": handle_id,
                "body": {
                    "request": "create",
                    "id": id,
                    "description": "Opus/VP8 tester.py test stream",
                    "streams": [
                        {
                            "audiopt": 111,
                            "audiortpmap": "opus/48000/2",
                            "videopt": 100,
                            "videortpmap": "VP8/90000"
                        },
                        {
                            "audiopt": 111,
                            "audiortpmap": "opus/48000/2",
                            "videopt": 100,
                            "videortpmap": "VP8/90000"
                        },
                        {
                            "audiopt": 111,
                            "audiortpmap": "opus/48000/2",
                            "videopt": 100,
                            "videortpmap": "VP8/90000"
                        },
                    ]
                }
            }, not session_id or not handle_id, helper)

def destroy():
    janus_cmd({ "janus": "message",
                "transaction": "tester.py",
                "session_id": session_id,
                "handle_id": handle_id,
                "body": {
                    "request": "destroy",
                    "id": mountpoint_id
                } }, not session_id or not handle_id)
