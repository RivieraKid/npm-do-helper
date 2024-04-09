#!/bin/python
import base64
import socket
import os
import digitalocean
import requests
import json

HOSTNAME=os.getenv("HOSTNAME")
SERVICENAME=os.getenv("SERVICENAME")
NPMINSTANCE=os.getenv("NPMINSTANCE")
DOMAIN="do.example.com"
NPMBASEURL="npm.example.com:81"
NPMUSERNAME = os.getenv("NPM_USERNAME").strip()
NPMPASSWORD = os.getenv("NPM_PASSWORD").strip()
NAMESPACE = os.getenv("NAMESPACE")

print(f'Hostname is {HOSTNAME}')
print(f'Service name is {SERVICENAME}')
print(f'NPM instance is {NPMINSTANCE}')
print(f'NPM_USERNAME is {NPMUSERNAME}')
print(f'NPM_PASSWORD is {NPMPASSWORD}')

npm_instance_ip = socket.gethostbyname(NPMINSTANCE.strip())

print(f'NPM instance IP address: {npm_instance_ip}')

TOKEN = os.getenv("DIGITALOCEAN_TOKEN").strip()
domain = digitalocean.Domain(token=TOKEN, name=DOMAIN)
records = domain.get_records()
record = None
for r in records:
    if r.name == SERVICENAME:
        record = r
if record is None:
    # Create a new record
    new_record = domain.create_new_domain_record(
        type='A',
        name=SERVICENAME,
        data=npm_instance_ip,
        ttl=300
    )
    print(new_record)
else:
    # Update an existing one
    record.type = 'A'
    record.data = npm_instance_ip
    record.ttl = 300
    record.save()

url = f"http://{NPMBASEURL}/api/tokens"

payload = json.dumps({
  "identity": NPMUSERNAME,
  "secret": NPMPASSWORD
})

auth_token = base64.b64encode(bytes(f"{NPMUSERNAME}:{NPMPASSWORD}", "utf-8"))

headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Basic {auth_token}'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

auth_response = json.loads(response.text)

url = f"http://{NPMBASEURL}/api/nginx/proxy-hosts"

payload = json.dumps({
  "domain_names": [
    f"{SERVICENAME}.{DOMAIN}"
  ],
  "forward_scheme": "http",
  "forward_host": f"{SERVICENAME}.{NAMESPACE}.svc.cluster.local",
  "forward_port": 80,
  "block_exploits": True,
  "access_list_id": 0,
  "certificate_id": 0,
  "meta": {
    "letsencrypt_agree": False,
    "dns_challenge": False
  },
  "advanced_config": "",
  "locations": [],
  "http2_support": True
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {auth_response["token"]}'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
