#!/usr/bin/python3 -i
# -*- coding: utf-8 -*-

import requests, json, subprocess

janus_url = "http://localhost:8088/janus"
mountpoint_id = "Ababagalamaga"
session_id = None
handle_id = None
ports = None
streamer = None

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
            print(json.dumps(j,indent=4, separators=(',', ': ')))
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

def list(id=None):
    body = not id and { "request": "list" } or { "request": "list", "id": id}
    janus_cmd({ "janus": "message",
                "transaction": "tester.py",
                "session_id": session_id,
                "handle_id": handle_id,
                "body": body}, not session_id or not handle_id)

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

# Streaming bitrates
videorate_min = 20000
videorate_max = 156000
audiorate_min = 6000
audiorate_max = 20000

# Various parameters feel free to change in runtime
pattern = "ball"
fontsize = 100
keyframedist = 120


def stream(vmin = videorate_min, vmax = videorate_max, amin = audiorate_min, amax = audiorate_max):
    global streamer
    args = "gst-launch-1.0 "
    nstreams = int(len(ports)/2)
    if streamer:
        print("Streamer already active!")
    else:
        for i in range(0,nstreams):
            arate = int(amin+i*(amax-amin)/(nstreams-1))
            vrate = int(vmin+i*(vmax-vmin)/(nstreams-1))
            args+="  audiotestsrc !  "
            args+="    audioresample ! audio/x-raw,channels=1,rate=16000 ! "
            args+="    opusenc bitrate=" + str(arate) + " ! "
            args+="      rtpopuspay ! udpsink host=127.0.0.1 port=" + str(ports[i*2]) + "  "
            args+="  videotestsrc pattern = '" + pattern + "' ! "
            args+="    video/x-raw,width=320,height=240,framerate=15/1 ! "
            args+="    videoscale ! videorate ! videoconvert ! timeoverlay ! "
            args+="    textoverlay font-desc='sans, " + str(fontsize) + "' text='Quality " + str(i) + "' !"
            args+="    vp8enc keyframe-max-dist=" + str(keyframedist) + " error-resilient=true target-bitrate=" + str(vrate) + " ! "
            args+="      rtpvp8pay ! udpsink host=127.0.0.1 port=" + str(ports[i*2 + 1]) + " "
        # args += ">/dev/null 2>&1"
        print("Running: " + args)
        streamer = subprocess.Popen(args, shell=True)

def unstream():
    global streamer
    if not streamer:
        print("Streamer not active!")
    else:
        streamer.terminate()
        print("Streamer stopped")
        streamer = None

def session():
    greet()
    attach()
    destroy()
    create()
