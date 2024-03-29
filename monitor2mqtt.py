import os
import time
import paho.mqtt.client as mqtt
import psutil
import subprocess
import json
import shutil
import uptime
import netifaces
import os
import requests

url = 'https://checkip.amazonaws.com'
response = requests.get(url)

if response.status_code == 200:
    print("Your external IP address is:", response.text.strip())
    publicip = response.text.strip()
else:
    print(f"Error: Unable to fetch external IP. Status code: {response.status_code}")
    publicip = "unknown"


# Get the directory containing the script
script_dir = os.path.dirname(__file__)

# Construct the path to the file
file_path = os.path.join(script_dir, 'settings.json')

def get_cpu_usage():
    # get the CPU usage for each core
    usage = psutil.cpu_percent(percpu=True)

    return usage

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT client connected successfully")
    else:
        print("MQTT client connection failed")

# Read the temperature from the Raspberry Pi
def read_temperature():
  # Run the vcgencmd command to read the temperature
  output = os.popen("vcgencmd measure_temp").read()

  # Parse the temperature from the output
  temperature_str = output.strip().split("=")[1]
  temperature = float(temperature_str.split("'")[0])

  # Return the temperature in degrees Celsius
  return temperature

def check_service_status(service_name):
    command = ["systemctl", "is-active", service_name]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        print(output.decode("utf-8").strip())
        if output.decode("utf-8").strip() == 'active':
                output = True
        else:
                output = False
        return output
    except subprocess.CalledProcessError as error:
        return error.output.decode("utf-8").strip()


def get_free_ram():
    # get information about the system's memory
    memory_info = psutil.virtual_memory()

    # return the amount of free memory in megabytes
    return memory_info.free / (1024 * 1024)

def get_ram():
    # get information about the system's memory
    memory_info = psutil.virtual_memory()

    # return the amount of total memory in megabytes
    return memory_info.total / (1024 * 1024)

def get_free_sd():
    # get the total,used and free space of the root partition
    total, used, free = shutil.disk_usage("/")
    # return the free amount of the root partition in gigabytes
    return free / (1024 * 1024 * 1024)

def get_sd():
    # get the total,used and free space of the root partition
    total, used, free = shutil.disk_usage("/")

    # return the total amount of the root partition in gigabytes
    return total / (1024 * 1024 * 1024)

def get_uptime():
    # get the uptime in seconds
    uptime_seconds = uptime.uptime()
    # convert the uptime to hours, minutes, and seconds
    hours, minutes = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(minutes, 60)

    # format the uptime as a string
    uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

    return uptime_str, int(uptime_seconds)

def get_ip_addresses():
    # get a list of all the network interfaces
    interfaces = netifaces.interfaces()
    net_counters = psutil.net_io_counters(pernic=True)

    if "eth0" not in net_counters:
        print("Interface not found.")
        bytes_sent = 0
        bytes_received = 0

    interface_data = net_counters["eth0"]
    bytes_sent = round(interface_data.bytes_sent/ (1024 ** 2), 2)
    bytes_received = round(interface_data.bytes_recv/ (1024 ** 2),2)

    # create an empty dictionary to store the IP addresses
    ip_addresses = {}

    # loop through the interfaces
    for interface in interfaces:
        # get the IP address of the interface
        iface_data = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in iface_data:
            for link in iface_data[netifaces.AF_INET]:
                ip_addresses[interface] = link['addr']

    return ip_addresses, bytes_sent, bytes_received

# Open the JSON file
with open(file_path, 'r') as f:
    # Load the contents of the file into a variable
    data = json.load(f)

test=[]
if 'service-monitor' in data:
        # create a new JSON object for each service
        for service in data['service-monitor']:
                test.append(service)

serv_res = {}
for services in test:
        serv_res[services] = {
                "status": check_service_status(data['service-monitor'][services]["name"])
        }

# Create a new MQTT client
client = mqtt.Client()
client.on_connect = on_connect

# Connect to the MQTT server
client.username_pw_set(data["mqtt_server"]["user"],data["mqtt_server"]["password"])
client.connect(data["mqtt_server"]["host"], data["mqtt_server"]["port"])

client.loop_start()

ip_addresses, bytes_sent, bytes_received = get_ip_addresses()


to_sent = {
    "temp": read_temperature(),
    "uptime": get_uptime()[0],
    "uptime_sec": get_uptime()[1],
    "cpu_usage": get_cpu_usage(),
    "services": serv_res,
    "ip": ip_addresses,
    "tx": bytes_sent,
    "rx": bytes_received,
    "free_ram": "{:.2f}".format(get_free_ram()),
    "total_ram": "{:.2f}".format(get_ram()),
    "sd_free": "{:.2f}".format(get_free_sd()),
    "total_sd": "{:.2f}".format(get_sd()),
    "public_ip": publicip
}

print(to_sent)

json_string=json.dumps(to_sent);
client.publish(data["mqtt_server"]["full_topic"],json_string)
time.sleep(1)

client.loop_stop()
