janus-gateway-rtpbroadcast
==========================
[janus-gateway](https://github.com/meetecho/janus-gateway) custom plugin.

[![Build Status](https://travis-ci.org/cargomedia/janus-gateway-rtpbroadcast.svg)](https://travis-ci.org/cargomedia/janus-gateway-rtpbroadcast)

Overview
--------
This plugin is based on native `janus` streaming plugin. It drops support for `LIVE`, `RTSP`, `VOD` and extends support for `RTP` streaming.

Main extensions:
- renames plugin with `janus.plugin.cm.rtpbroadcast`
- changes type of mountpoint `id` from `integer` to `string`
- allows to create multiple streams (sources) per mountpoint
- tracks `RTP/VP8` header workflow and provides `width`, `height` for frame and `fps`, `key-frame-distance` for stream
- extends RTP statistics for incoming streams
- introduces `key-frame` based scheduling for stream and mountpoint switching
- introduces `auto-switch` of active stream based on client bandwidth (`WebRTC/REMB`)
- pushes new media event to the subscriber if stream or mountpoint switched by `scheduler`
- allows to manually switch the stream or turn off the `auto-switch`
- introduce IP based white-listing for incoming RTP packages
- automatically records the first provided stream (per mountpoint) into configurable archives
- dumps stream RTP payload into configurable thumbnailer archives
- creates job files and store events like new `archive-finished` or `thumbnailing-finished`

Configuration
-------------
```
[general]
; Port range for automatic port generation
; minport = 8000
; maxport = 9000

; Source bitrate averaging interval, seconds
; source_avg_time = 10
; Watcher REMB averageing interval, seconds
; remb_avg_time = 3
; Switching interval, seconds
; switching_delay = 1

; Log error if keyframe is not found within this amount of frames
; keyframe_distance_alert = 600

; NOTE: all paths should exist beforehead

; Path for job JSONs
; job_path = /tmp/jobs

; printf pattern for job filenames (.json is auto)
; Short usage, the following gets substituted:
; #{time}     is timestamp (guint64)
; #{rand}     is random integer (guin32)
; #{md5}      is md5 of (timestamp + plugin name + random integer)
; #{plugin}   is plugin name ("janus.plugin.cm.rtpbroadcast")
; job_pattern = job-#{md5}

; Path for recording and thumbnailing
; archive_path = /tmp/recordings"

; printf pattern for recordings filenames
; Short usage, the following gets substituted:
; #{id}       is streamChannelKey (string)
; #{time}     is timestamp (guint64)
; #{type}     is type ("audio", "video" or "thumb" string)
; recording_pattern = rec-#{id}-#{time}-#{type}

; Same for thumbnails
; thumbnailing_pattern = thum-#{id}-#{time}-#{type}

; Thumbnailing interval in seconds
; thumbnailing_interval = 60

; Thumbnailing duration in seconds
; thumbnailing_duration = 10
```

Synchronous actions
-------------------
It supports `create`, `destroy` actions and drops support for `recording` action.

#### `create`

**Request**:
```json
{
  "id": "<string>",
  "name": "<string>",
  "description": "<string>",
  "recorded": "<boolean>",
  "whitelist": "<string>",
  "streams": [
    {
      "audiopt": 111,
      "audiortpmap": "opus/48000/2",
      "videopt": 100,
      "videortpmap": "VP8/90000"
    }
  ],
}
```

**Response**:
It responses with auto generated port number for audio and video using `minport` and `maxport` of config file.

```json
{
  "streaming": "created",
  "created": "<string>",
  "id": "<string>",
  "description": "<string>",
  "streams": [
    {
      "audioport": "<int>",
      "videoport": "<int>",
    }
  ]
}
```

#### `destroy`

**Request**:

```json
{
  "id": "<string>"
}
```

**Response**:
```json
{
  "streaming": "created",
  "destroyed": "<string>"
}
```

Asychronous actions
-------------------
It supports `start`, `stop`, `pause`, `switch` actions like native `janus/streaming` plugins. It extends `list` action with new features, changes
`watch` action and introduces new `switch-source` action.

##### Stream definition for responses
The response for multiple actions contains the `stream-definition` like follows:

```json
{
   "id": "<string>",
   "index": "<int>",
   "audioport": "<int>",
   "videoport": "<int>",
   "stats": {
      "min": "<float>",
      "max": "<float>",
      "cur": "<float>",
      "avg": "<float>"
   },
   "frame": {
      "width": "<int>",
      "height": "<int>",
      "fps": "<int>",
      "key-distance": "<int>"
   },
   "session": {
      "webrtc-active": "<boolean>",
      "autoswitch-enabled": "<boolean>",
      "remb-avg": "<int>"
   }
}
```

- `id` is the mountpoint identification
- `index` is position of stream in the mountpoint/streams array
- `session` is set only for `list` action and reference to current connection/session.

#### `list`
It return mountpoint with specific `id`. If `id` is not provided it return all existing mountpoints.

**Request**:
```json
{
  "id": "<string|null>"
}
```

**Response**:
```json
[
  {
     "id": "<string>",
     "name": "<string>",
     "description": "<string>",
     "streams": [
        "<stream-definition-1>",
        "<stream-definition-2>",
        "<stream-definition-N>"
     ]
  }
]
```

#### `watch`
It will pick up first stream from the mountpoint list and assigns to the user session.

**Request**:
```json
{
  "id": "<string>"
}
```

**Response**:
```json
{
  "streaming": "event",
  "result": {
    "status": "preparing",
  }
}
```

#### `switch`
It will switch the mountpoint for the session. By default will pick up first stream from the mountpoint list.

**Request**:
```json
{
  "id": "<string>"
}
```

**Response**:
```json
{
  "streaming": "event",
  "result": {
    "next": "<stream-definition>",
    "current": "<stream-definition>"
   }
}
```

#### `switch-source`
It will schedule switching of the stream with `index` for current session mountpoint (position in the `streams`, see `list` action).
The switch will be triggered when first kef-frame arrives for requested stream. If `index` is higher than `0` then `auto-switch` support will be `OFF`.
If `index` is equal to `0` then `auto-switch` support will be `ON`.

**Request**:
```json
{
  "index": "<integer>"
}
```

**Response**:
```json
{
  "streaming": "event",
  "result": {
    "next": "null|<stream-definition>",
    "current": "<stream-definition>",
    "autoswitch": "<boolean>"
  }
}
```

`next` source definition is not available if `autoswitch` is set to `true`.

#### `stop`, `start`, `pause`
Events has the same bahaviour as native `janus/streaming` plugin.

Job files
---------
It creates configurable `job-files` with plugin events. It support for `archive-finished` or `thumbnailing-finished` event.

##### `archive-finished`
```json
{
    "data": {
        "id": "<string>",
        "video": "<archive_path/recording_pattern>.mjr",
        "audio": "<archive_path/recording_pattern>.mjr"
    },
    "plugin": "janus.plugin.cm.rtpbroadcast",
    "event": "archive-finished"
}
```

##### `thumbnailing-finished`
Thumbnailer creates archives of configurable duration for configurable interval of time.

```json
{
    "data": {
        "id": "<string>",
        "thumb": "<archive_path/thumbnailing_pattern>.mjr"
    },
    "plugin": "janus.plugin.cm.rtpbroadcast",
    "event": "thumbnailing-finished"
}
```

Advanced
--------

#### Autoswitch
It calculates advanced statistics for incomming `RTP` streams and for incomming `REMB` per `WebRTC` session. It allows to switch streams in
configurable manner (see config file) which depends on runtime condition of incomming RTP payload of publisher and outgoing RTP payload of subscriber.
If "switch" condition is matched the switch action is queued in the `scheduler`.

#### Scheduling
It tracks `RTP/VP8` payload for `key-frames` and triggers the switch of waiting subscribers. The waiting list of subscribers is defined per
stream and keeps `WebRTC` session as reference. The `session` can be allocated to the waiting queue or by:
- setting `autoswitch` to `ON`
- sending the `switch-source` action request
- sending the `switch` action request

If scheduled task is executed the subscriber receives media event:
```json
{
  "streaming": "event",
  "result": {
    "event": "changed",
    "current": "<stream-definition>",
    "previous": "<stream-definition>"
  }
}
```

#### Mountpoint information event
It sends updates with current state of mountpoint which is watched by session. `mountpoint-info` event contains current state of `sources` and configuration 
used for calculating statistics.
```json
{
  "streaming": "event",
  "result": {
    "event": "mountpoint-info",
    "streams": [
      "<stream-definition-1>",
      "<stream-definition-2>",
      "<stream-definition-N>",
    ],
    "config": {
      "source_avg_duration": "<int>",
      "remb_avg_duration": "<int>"
    }
  }
}
```

Clients support
---------------
This plugin can be directly managed by [`janus-gateway-ruby`](https://github.com/cargomedia/janus-gateway-ruby) client using
[mountpoint](https://github.com/cargomedia/janus-gateway-ruby#plugins) resource.

Additionally the `ACL` for publishers and subscribers, `job-file` handling can be directly managed by [cm-janus](https://github.com/cargomedia/cm-janus)

Testing
-------
There is a simple testing script placed in the `test/tester.py` which allow for triggering basic actions on the plugin. Please find the
[test/README](test/README.md) for more details.

Building
--------
If you got janus-gateway-rtpbroadcast from the git repository, you will first need to run the included `autogen.sh` script
to generate the `configure` script.

```
./autogen.sh
./configure  --prefix=/opt/janus
make
make install
```
