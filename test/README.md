# Minitest suite

You might need to install `requests` library for Python3 for the tests to work. Please use your
distrubution's package manager or run the following:
```
pip install requests
```

If your python is not in default location, you might either need to edit the hashbang or
just run directly as:
```
python3 -i tester.py
```

For streaming you might need `gstreamer` installed.

When you run the script, you will be dropped to Python3 interpreter with helper functions.

### `greet()`

Run this first to establish a session.

### `attach(plugin_name)`

Attach to the plugin, name is optional, cm.rtpbroadcast is default.

### `keepalive()`

Refresh the session timeout.

### `list()`

Run this after `attach()`, lists the mountpoints.

### `create(id)`

Create a mountpoint `id`, default is `Ababagalamaga`.

### `destroy(id)`

Destroy the mountpoint by `id`, default is `Ababagalamaga`.

### `stream(amin,amax,vmin,vmax)`

Create streaming streams, params means maximal and minimal bitrate and can be omitted with
default values.

### `unstream()`

Stops streaming. *Don't forget* to do this when you stop session. It's *not* done automatically. Manual kill:
```
killall gst-launch-1.0
```

### `session()`

Runs `greet()`, `attach()` and `create()`
