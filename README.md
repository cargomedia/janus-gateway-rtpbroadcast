janus-gateway-rtpbroadcast
==========================
[janus-gateway](https://github.com/meetecho/janus-gateway) plugin for [cm-janus](https://github.com/cargomedia/cm-janus)

[![Build Status](https://travis-ci.org/cargomedia/janus-gateway-rtpbroadcast.svg)](https://travis-ci.org/cargomedia/janus-gateway-rtpbroadcast)

Overview
--------
This plugin is based on native `janus` streaming plugin. It drops support for `LIVE`, `RTSP`, `VOD` and extends support for `RTP` streaming.
 
Main extensions:
- changes type of mountpoint `id` from `integer` to `string`
- allows to create multiple streams (sources) per mountpoint
- tracks `VP8` RTP header workflow and provides `width`, `height` for frame and `fps`, `key-frame-distance` for stream
- extends RTP statistics for incoming streams
- introduce `key-frame` based scheduling for stream switching
- automatically switches streams based on `WebRTC` client bandwidth (`REMB`)
- allows to manually switch stream or turn off `autoswitch`
- introduce whitelisting for incoming RTP packages based on IP
- automatically records the first provided stream (per mountpoint) into configurable archives
- dumps stream RTP payload into configurable thumbnailer archives
- creates job files with events like new `archive-finished` or `thumbnailing-finished`

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

; NOTE: all paths should exist beforehead

; Path for job JSONs
; job_path = /tmp/jobs

; prinf pattern for job filenames (.json is auto)
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

##### `create`

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

##### `destroy`

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
It supports `start`, `stop`, `pause`, `switch` actions like native `janus` streaming plugins. It extends `list` action with new features, changes 
`watch` action and introduces new `switch-source` action.

##### `list`
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
        {
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
              "webrtc-active": "<boolean>"
           }
        }
     ]
  }
]
```

##### `watch`
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
  "status": "preparing",
}
```

##### `switch`
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
  "switched": "ok",
  "id": "<string>"
}
```

##### `switch-source`
It will schedule switching of the stream for current session mountpoint to requested by `index` (position in the `streams`, see `list` action). 
The switch will happened when first kef-frame arrives for requested stream. If `index` is higher than `0` then `auto-switch` support will be `OFF`.
If `index` is equal to `0` then `auto-switch` support will be `ON`,

**Request**:
```json
{
  "id": "<string>",
  "index": "<integer>"
}
```

**Response**:
```json
{
  "streaming": "event",
  "switched-source": "scheduled",
  "index": "<string>",
  "autoswitch": "<boolean>"
}
```

##### `stop`, `start`, `pause`
Events has the same bahaviour as native `janus/streaming` plugin.

Job files
---------
It creates configurable `job-files` with plugin events. It support for `archive-finished` or `thumbnailing-finished` event.

##### `archive-finished` 
```
{
    "data": {
        "id": "1",
        "video": "<archive_path/recording_pattern>.mjr",
        "audio": "<archive_path/recording_pattern>.mjr"
    },
    "plugin": "janus.plugin.cm.rtpbroadcast",
    "event": "archive-finished"
}
```

##### `thumbnailing-finished`
Thumbnailer creates archives of configurable duration for every configurable interval of time. 

```
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
It calculates advances stats for incomming `RTP` streams and for incomming `REMB` per `WebRTC` session. It allows to switch streams in 
configurable way depends on runtime condition of incomming RTP payload of publisher and outgoing RTP payload per subscriber.

#### Scheduling
It tracks `RTP/VP8` payload for key frames and trigger switch of waiting subscribers. The waiting list is defined per stream and keeps WebRTC session
as reference. `Session` can be in allocated to the waiting queue or if `autoswitch` is `ON` or by `switch-source` action request.

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
