# Simple Raspberry Pi Monitor with MQTT 

This Python script is designed to monitor a RaspberryPi within a smart home environment that uses MQTT. It allows the user to keep track of the status and performance of the Raspberry Pi, ensuring that it is running smoothly.

It uses a json file called "settings.json" as config file and it can monitor the following

- Temperature
- Uptime
- CPU Usage
- Services
- Ip addresses of the network interfaces
- Free RAM Memory in MB
- Total RAM Memory in MB
- Free SD Space in GB
- Total SD Space in GB

Used packages:

- os
- time
- paho.mqtt.client
- psutil
- subprocess
- json
- shutil
- uptime
- netifaces

The settings.json file must have the following format
```
{
  "mqtt_server": {
    "host": "XXX.XXX.X.X",
    "port": 1883,
    "client": "rpi",
    "user": "MQTT_USERNAME",
    "password": "MQTT_PASSWORD",
    "topic": "MQTT_TOPIC",
    "full_topic": "MQTT_FULL_TOPIC"
  },
  "service-monitor": {
    "TTN": {
      "name": "ttn-gateway.service",
      "status": true
    },
    "OPENVPN": {
      "name": "openvpn.service",
      "status": true
    },
    "test": {
      "name": "cryptdisks.service",
      "status": false
    }
  }
}
```
The script send a json object with the following format

```
{
  "temp": 40.8,
  "uptime": "27h 8m 51s",
  "cpu_usage": [
    0,
    22.2,
    63.6,
    30
  ],
  "services": {
    "TTN": {
      "status": "active"
    },
    "OPENVPN": {
      "status": "active"
    },
    "test": {
      "status": "inactive"
    }
  },
  "ip": {
    "lo": "127.0.0.1",
    "wlan0": "192.168.1.99",
    "tun0": "192.168.2.4"
  },
  "free_ram": "563.86",
  "total_ram": "924.84",
  "sd_free": "12.00",
  "total_sd": "14.33"
}
```

You can easily run this script with crontab
