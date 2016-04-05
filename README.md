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
- extends RTP statistics for incoming streams (bitrate, packets loss)
- introduces `key-frame` based scheduling for stream and mountpoint switching
- introduces `auto-switch` of active stream based on client bandwidth (`WebRTC/REMB`)
- pushes new media event to the subscriber if stream or mountpoint switched by `scheduler`
- allows to manually switch the stream or turn off the `auto-switch`
- introduce IP based white-listing for incoming RTP packages
- automatically records the first provided stream (per mountpoint) into configurable archives
- dumps stream RTP payload into configurable thumbnailer archives
- creates job files and store events like new `archive-finished` or `thumbnailing-finished`
- introduces `UDP` relay gateway and allows to switch session between `WebRTC` and `UDP` relay mode
- introduces `switch-source` end point for switching the stream in the mountpoint
- introduces capability for scaling on the `UDP` level by introducing `watch-udp` end point
- introduces `superuser` end point which upgrades/downgrades session for receiving detailed admin info
- introduces bad connection simulator (UDP packet loss) 

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

; Session streams status update interval, seconds
; session_info_update_time = 10

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

; Enable auto recording and thumbnailing
; recording_enabled = yes

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

; Bad connection simulator, only for debug purpose
; Note: defaults are 0, comment the options to disable
; simulate_bad_connection = yes

; Packet loss percentage
; packet_loss_rate = 5
```

#### Stream definition for responses
The response for multiple actions contains the `stream-definition` like follows:

```json
{
   "id": "<string>",
   "uid": "<string>",
   "index": "<int>",
   "audioport": "<int>",
   "videoport": "<int>",
   "listeners": "<int>",
   "waiters": "<int>",
   "stats": {
      "min": "<float>",
      "max": "<float>",
      "cur": "<float>",
      "avg": "<float>",
      "audio": {
         "cur_loss": "<float>",
         "avg_loss": "<float>"
      },
      "video": {
         "cur_loss": "<float>",
         "avg_loss": "<float>"
      }
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
- `session` is set only for `list` action and reference to current connection/session
- `cur_loss` is an estimate of UDP packets loss for the window of last `source_avg_time` seconds as regular stats
- `avg_loss` is an estimate of UDP packets loss for the whole time the connection is on

#### Mountpoint definition for responses
The response for multiple actions contains the `mountpoint-definition` like follows:

```json
{
  "id": "<string>",
  "uid": "<string>",
  "name": "<string>",
  "description": "<string>",
  "enabled": "<boolean>",
  "recorded": "<boolean>",
  "whitelisted": "<boolean>",
  "streams": [
    "<stream-definition-1>",
    "<stream-definition-2>",
    "<stream-definition-N>",
  ]
}
```

Synchronous actions
-------------------
It supports `create`, `destroy` actions and drops support for `recording` action. It extends `list` action with new features. 

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
  "stream": {
    "id": "<string>",
    "uid": "<string>",
    "description": "<string>",
    "streams": [
      {
        "audioport": "<int>",
        "videoport": "<int>",
      }
    ]
  }
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

#### `list`
It returns mountpoint with specific `id`. If `id` is not provided it return all existing mountpoints.

**Request**:
```json
{
  "id": "<string|null>"
}
```

**Response**:
```json
{
  "streaming": "list",
  "list": [
    {
       "id": "<string>",
       "uid": "<string>",
       "name": "<string>",
       "description": "<string>",
       "streams": [
          "<stream-definition-1>",
          "<stream-definition-2>",
          "<stream-definition-N>"
       ]
    }
  ]
}
```

Asychronous actions
-------------------
It supports `start`, `stop`, `pause`, `switch` actions like native `janus/streaming` plugins. It changes `watch` action and introduces new 
`switch-source` action.

Asynchronous action gets janus `ack` response for request and then receives `event` with plugin response.

**Response**
```json
{
  "janus": "ack",
  "session_id": "<int>",
  "transaction": "<string>"
}
```

#### `watch`
It will pick up first stream from the mountpoint list and assigns to the user session.

**Request**:
```json
{
  "id": "<string>"
}
```

**Event**:
```json
{
  "streaming": "event",
  "result": {
    "status": "preparing",
    "stream": "<stream-definition>"
  }
}
```

#### `watch-udp`
It allows to relay incoming `UDP` traffic as `UDP` without any conversion. In general it forwards packets from the `UDP` server to the `UDP` client.
This request has to provide a full destination list for all streams defined by mountpoint. It will link the current list of streams with new
destination list by index/position of the stream in the array.

**Request**:
```json
{
  "id": "<string>",
  "streams": [
    {
      "audioport": "<integer>",
      "audiohost": "<string>",
      "videoport": "<integer>",
      "videohost": "<string>",
    }
  ],
}
```

**Event**:
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

**Event**:
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

**Event**:
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

#### `superuser`
By passing `true` it upgrades current session into super user session and downgrade into regular one by passing `false`.

**Request**:
```json
{
  "enabled": "<boolean>"
}
```

**Event**:
```json
{
  "streaming": "superuser",
  "enabled": 1
}
```

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
        "uid": "<string>",
        "createdAt": "<int>",
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
        "uid": "<string>",
        "createdAt": "<int>",
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

#### Mountpoints information event
It sends updates with current state of mountpoints to the `superuser` sessions. This is currently triggerd by `create` and `destroy` end point. 
```json
{
  "streaming": "event",
  "result": {
    "event": "mountpoints-info",
    "list": [
      "<mountpoint-definition-1>",
      "<mountpoint-definition-2>",
      "<mountpoint-definition-N>",
    ],
  }
}
```

#### Bad connection simulator
Randomly drops the UDP packets from incoming stream. Provides config file interface:

- `simulate_bad_connection` : boolean

Master switch, when set to yes, enables code for simulating packet drop.

- `packet_loss_rate` : integer

If bad connection simulator is enabled, specifies the percentage of packets which are artificially "lost".

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
