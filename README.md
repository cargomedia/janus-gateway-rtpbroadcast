janus-gateway-rtpbroadcast
==========================
[janus-gateway](https://github.com/meetecho/janus-gateway) plugin for [cm-janus](https://github.com/cargomedia/cm-janus)

[![Build Status](https://travis-ci.org/cargomedia/janus-gateway-rtpbroadcast.svg)](https://travis-ci.org/cargomedia/janus-gateway-rtpbroadcast)

Overview
--------
This plugin is based on native `janus` streaming plugin. It drops support for `LIVE`, `RTSP`, `VOD` and extends support for `RTP` streaming.
 
Main extensions:
- changes type of `id` from `integer` to `string`
- allows to create multiple streams per mountpoint
- tracks VP8 rtp header workflow and provides width, height for frame and fps and key frame distance for stream
- extends RTP statistics for incoming streams
- introduce key-frame based scheduling for stream switching
- automatically switches streams based on WebRTC client bandwidth (REMB)
- allows to manually switch stream by subscriber
- introduce whitelisting for incoming RTP packages based on IP
- automatically records first provided stream in the list of streams
- dumps stream into tiny thumbnailer archives
- creates job files with events like new `record-archive` or `thumbnailer-archive`

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

### `create`

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

### `destroy`

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

### `list`
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

### `watch`
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

### `switch`
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

### `switch-source`
It will schedule switching of the stream for current session mountpoint to requested by `index` (position in the `streams`, see `list` action). 
The switch will happened when first kef-frame arrives for requested stream.

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

### `stop`, `start`, `pause`
Events has the same bahaviour as native `janus/streaming` plugin.

## Building

If you got janus-gateway-rtpbroadcast from the git repository, you will first need to run the included `autogen.sh` script
to generate the `configure` script.

```
./autogen.sh
./configure  --prefix=/opt/janus
make
make install
```
