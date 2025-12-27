import requests
import json
import sys

SN_API_URL = "https://dev339830.service-now.com/api/1835622/cmdbchangevalidationapi/validate"

with open("change.json") as f:
    payload = json.load(f)

response = requests.post(
    SN_API_URL,
    json={"data": payload},
    auth=("admin", "Charlie@22"),
    headers={"Content-Type": "application/json"}
)

print("ServiceNow response:", response.text)

result = response.json()

if result.get("decision") == "BLOCK":
    print("❌ AI blocked the change")
    sys.exit(1)   # ❌ Fail pipeline
else:
    print("✅ AI approved the change")
