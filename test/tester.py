#!/usr/bin/python3 -i
# -*- coding: utf-8 -*-

import requests, json, subprocess, time

janus_url = "http://localhost:8088/janus"
mountpoint_id = "Ababagalamaga"

insttemplate = {
    "session_id" : None,
    "handle_id" : None,
    "ports" : None,
    "streamer" : None,
}

def newinst():
    return insttemplate.copy()

definstance = newinst()

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

def greet(session=None):
    session = session or definstance
    def helper(j):
        session["session_id"] = j["data"]["id"]
    janus_cmd({ "janus": "create",
                "transaction": "tester.py"}, action = helper)

# If delay != 0, sends keepalives every second over delay seconds
def keepalive(delay = 0, session=None):
    session = session or definstance
    janus_cmd({ "janus": "keepalive",
                "transaction": "tester.py",
                "session_id": session["session_id"] }, not session["session_id"])
    if delay > 0:
        for i in range(0,delay):
            time.sleep(1)
            keepalive()

def attach(plugin = "janus.plugin.cm.rtpbroadcast", session=None):
    session = session or definstance
    def helper(j):
        session["handle_id"] = j["data"]["id"]
    janus_cmd({ "janus": "attach",
                "plugin": plugin,
                "transaction": "tester.py",
                "session_id": session["session_id"] }, not session["session_id"], helper)

def list(id=None, session=None):
    session = session or definstance
    body = not id and { "request": "list" } or { "request": "list", "id": id}
    janus_cmd({ "janus": "message",
                "transaction": "tester.py",
                "session_id": session["session_id"],
                "handle_id": session["handle_id"],
                "body": body}, not session["session_id"] or not session["handle_id"])

def create(id=mountpoint_id, session=None):
    session = session or definstance
    def helper(j):
        session["ports"] = []
        for i in j["plugindata"]["data"]["stream"]["streams"]:
            session["ports"].append(i["audioport"])
            session["ports"].append(i["videoport"])
    janus_cmd({ "janus": "message",
                "transaction": "tester.py",
                "session_id": session["session_id"],
                "handle_id": session["handle_id"],
                "body": {
                    "request": "create",
                    "id": id,
                    "description": "Opus/VP8 tester.py test stream",
                    "recorded": True,
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
            }, not session["session_id"] or not session["handle_id"], helper)

def destroy(session=None):
    session = session or definstance
    janus_cmd({ "janus": "message",
                "transaction": "tester.py",
                "session_id": session["session_id"],
                "handle_id": session["handle_id"],
                "body": {
                    "request": "destroy",
                    "id": mountpoint_id
                } }, not session["session_id"] or not session["handle_id"])

# Streaming bitrates
videorate_min = 20000
videorate_max = 156000
audiorate_min = 6000
audiorate_max = 20000

# Various parameters feel free to change in runtime
pattern = "ball"
fontsize = 100
keyframedist = 120


def stream(vmin = videorate_min, vmax = videorate_max, amin = audiorate_min, amax = audiorate_max, session=None):
    session = session or definstance
    args = "gst-launch-1.0 "
    nstreams = int(len(session["ports"])/2)
    if session["streamer"]:
        print("Streamer already active!")
    else:
        for i in range(0,nstreams):
            arate = int(amin+(nstreams-i-1)*(amax-amin)/(nstreams-1))
            vrate = int(vmin+(nstreams-i-1)*(vmax-vmin)/(nstreams-1))
            args+="  audiotestsrc !  "
            args+="    audioresample ! audio/x-raw,channels=1,rate=16000 ! "
            args+="    opusenc bitrate=" + str(arate) + " ! "
            args+="      rtpopuspay ! udpsink host=127.0.0.1 port=" + str(session["ports"][i*2]) + "  "
            args+="  videotestsrc pattern = '" + pattern + "' ! "
            args+="    video/x-raw,width=320,height=240,framerate=15/1 ! "
            args+="    videoscale ! videorate ! videoconvert ! timeoverlay ! "
            args+="    textoverlay font-desc='sans, " + str(fontsize) + "' text='Quality " + str(i) + "' !"
            args+="    vp8enc keyframe-max-dist=" + str(keyframedist) + " error-resilient=true target-bitrate=" + str(vrate) + " ! "
            args+="      rtpvp8pay ! udpsink host=127.0.0.1 port=" + str(session["ports"][i*2 + 1]) + " "
        # args += ">/dev/null 2>&1"
        print("Running: " + args)
        session["streamer"] = subprocess.Popen(args, shell=True)

def unstream(session=None):
    session = session or definstance
    if not session["streamer"]:
        print("Streamer not active!")
    else:
        session["streamer"].terminate()
        print("Streamer stopped")
        session["streamer"] = None

def udp_watch(session=None):
    session = session or definstance
    janus_cmd({ "janus": "message",
                "transaction": "tester.py",
                "session_id": session["session_id"],
                "handle_id": session["handle_id"],
                "body": {
                    "request": "watch-udp",
                    "id": mountpoint_id,
                    # TODO: this is copied from @kris-lab streaming.js
                    "streams": [
                      {
                        "audioport": 5002,
                        "audiohost": '10.10.10.112',
                        "videoport": 5004,
                        "videohost": '10.10.10.112'
                      },
                      {
                        "audioport": 6002,
                        "audiohost": '10.10.10.112',
                        "videoport": 6004,
                        "videohost": '10.10.10.112'
                      },
                      {
                        "audioport": 7002,
                        "audiohost": '10.10.10.112',
                        "videoport": 7004,
                        "videohost": '10.10.10.112'
                      }
                    ]
                } }, not session["session_id"] or not session["handle_id"])

def session():
    greet()
    attach()
    destroy()
    create()

def udp_session():
    udp = newinst()
    greet(session=udp)
    attach(session=udp)
    udp_watch(session=udp)
