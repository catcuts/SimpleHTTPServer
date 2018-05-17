# SimpleHttpServer

Simple Http Server based on Flask and Flask-HttpAuth. Currently used for remotely controlling rpi3.

## How to use

**1. Get RPi Network Confirguation**

Example request:
```bash
curl $HOST:5000/getNetworkConf | python -m json.tool
```

Example respond:
```javascript
{
    "message": {
        "docker0": {
            "dns_alter": "",
            "dns_prefer": "",
            "ip": "172.17.0.1",
            "netmask": "255.255.0.0"
        },
        "eth0": {
            "dns_alter": "",
            "dns_prefer": "",
            "ip": "192.168.116.160",
            "netmask": "255.255.255.0"
        },
        "lo": {
            "dns_alter": "",
            "dns_prefer": "",
            "ip": "127.0.0.1",
            "netmask": "255.0.0.0"
        },
        "veth140e4c3": {
            "dns_alter": "",
            "dns_prefer": "",
            "ip": "169.254.21.22",
            "netmask": "255.255.0.0"
        },
        "vethfedb7f7": {
            "dns_alter": "",
            "dns_prefer": "",
            "ip": "169.254.59.61",
            "netmask": "255.255.0.0"
        },
        "wlan0": {
            "dns_alter": "",
            "dns_prefer": "",
            "ip": "unknown",
            "netmask": "unknown"
        }
    },
    "status": "ok"
}

```

**2. Set RPi Network Confirguation**

Example request:
```bash
curl -u $USER:$PASSWD "$HOST:5000/changeNetwork?\
ip=192.168.116.160&\
gateway=192.168.116.1&\
netmask=255.255.255.0&\
dns_prefer=8.8.8.8&\
dns_alter=8.8.4.4" \
| python -m json.tool
```

Example respond (if authorized):
```javascript
{
    "message": true,
    "status": "ok"
}
```

Example respond (if unauthorized):
```javascript
{
    "message": "Unauthorized access",
    "status": "error"
}
```

**3. Reset RPi Network Confirguation**

Example request:
```bash
curl -u $USER:$PASSWD "$HOST:5000/resetNetwork | python -m json.tool
```

Example respond (if authorized):
```javascript
{
    "message": true,
    "status": "ok"
}
```

Example respond (if unauthorized):
```javascript
{
    "message": "Unauthorized access",
    "status": "error"
}
```