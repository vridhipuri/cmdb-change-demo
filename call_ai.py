import requests
import json
import sys

SN_API_URL = "https://dev339830.service-now.com/api/1835622/cmdbchangevalidationapi/validate"

with open("change.json") as f:
    payload = json.load(f)

response = requests.post(
    SN_API_URL,
    json=payload,
    auth=("admin", "Charlie@22"),
    headers={"Content-Type": "application/json"}
)

print("ServiceNow response:", response.text)

# 🔥 FIX STARTS HERE
resp_json = response.json()

# ServiceNow wraps output inside "result"
result = resp_json.get("result", resp_json)

decision = result.get("decision")

if decision == "BLOCK":
    print("❌ AI blocked the change")
    sys.exit(1)   # ❌ Fail pipeline
elif decision == "APPROVE":
    print("✅ AI approved the change")
    sys.exit(0)
else:
    print("❌ Unknown decision, failing pipeline")
    sys.exit(1)
