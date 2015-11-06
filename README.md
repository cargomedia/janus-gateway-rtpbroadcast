# janus-gateway-cm
janus-gateway plugin(s) for https://github.com/cargomedia/cm-janus

# Supersessions

In order to receive notifications about events (mostly recording/thumbnailing
for now), send a `superuser` command with boolean `value`:

```
{
  "session_id": 2758347364,
  "handle_id": 1970006684,
  "transaction": "deadbeef",
  "janus": "message",
  "body": {
    "request" : "superuser",
     "value": true
  }
}
```

Afterwards this session will be notified about the events like this:

```
{
   "janus": "event",
   "session_id": 2758347364,
   "sender": 1970006684,
   "transaction": "hoD8Ht48H62b",
   "plugindata": {
      "plugin": "janus.plugin.cm.rtpbroadcast",
      "data": {
         "streaming": "destroyed",
         "destroyed": "Ababagalamaga",
         "timestamp": 91875791143,
         "superuser": true
      }
   }
}
```
