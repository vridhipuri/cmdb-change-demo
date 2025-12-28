# import requests
# import json
# import sys

# SN_API_URL = "https://dev339830.service-now.com/api/1835622/cmdbchangevalidationapi/validate"

# with open("change.json") as f:
#     payload = json.load(f)

# response = requests.post(
#     SN_API_URL,
#     json=payload,
#     auth=("admin", "Charlie@22"),
#     headers={"Content-Type": "application/json"}
# )

# print("ServiceNow response:", response.text)

# # 🔥 FIX STARTS HERE
# resp_json = response.json()

# # ServiceNow wraps output inside "result"
# result = resp_json.get("result", resp_json)

# decision = result.get("decision")


# if decision == "BLOCK":
#     print("❌ AI blocked the change")
#     sys.exit(1)

# elif decision == "APPROVE":
#     print("✅ AI approved the change")
#     sys.exit(0)

# elif decision == "REQUIRES_APPROVAL":
#     print("⏸️ AI requires manual approval")
#     print(f"Change created in ServiceNow: {result.get('change_sys_id')}")
#     sys.exit(2)   # special exit for manual approval

# else:
#     print("❌ Unknown decision, failing pipeline")
#     sys.exit(1)



import requests
import json
import sys

SN_API_URL = "https://dev339830.service-now.com/api/1835622/cmdbchangevalidationapi/validate"

print("\n===== LOADING CHANGE PAYLOAD =====")
with open("change.json") as f:
    payload = json.load(f)

print(json.dumps(payload, indent=2))

print("\n===== CALLING SERVICENOW SCRIPTED REST API =====")

response = requests.post(
    SN_API_URL,
    json=payload,
    auth=("admin", "Charlie@22"),
    headers={"Content-Type": "application/json"}
)

print("\n===== RAW SERVICENOW RESPONSE =====")
print(response.text)

try:
    resp_json = response.json()
except Exception:
    print("❌ Invalid JSON from ServiceNow")
    sys.exit(1)

# ServiceNow wraps everything inside "result"
result = resp_json.get("result", {})

print("\n===== PARSED RESPONSE =====")
print(json.dumps(result, indent=2))

decision   = result.get("decision")
ai_risk    = result.get("ai_risk")
confidence = result.get("confidence")
reason     = result.get("reason")
change_id  = result.get("change_sys_id")

print("\n===== AI DECISION SUMMARY =====")
print(f"Decision    : {decision}")
print(f"AI Risk     : {ai_risk}")
print(f"Confidence  : {confidence}")
print(f"Explanation : {reason}")
print(f"Change ID   : {change_id}")

# Optional audit visibility (if ServiceNow sends it)
print("\n===== HISTORICAL CHANGES USED =====")
audit = result.get("audit_context", {})

hist_changes = audit.get("historical_changes", [])
incidents = audit.get("related_incidents", [])

if hist_changes:
    for ch in hist_changes:
        print(f"- {ch.get('number')} | {ch.get('short_description')}")
else:
    print("No historical changes provided")

print("\n===== RECENT INCIDENTS USED =====")
incidents = result.get("related_incidents", [])
if incidents:
    for inc in incidents:
        print(f"- {inc.get('number')} | {inc.get('short_description')}")
else:
    print("No incidents provided")

# ===== PIPELINE CONTROL (THIS WAS YOUR BUG) =====

if decision == "BLOCK":
    print("\n❌ PIPELINE FAILED: AI BLOCKED THE CHANGE")
    sys.exit(1)

elif decision == "APPROVE":
    print("\n✅ PIPELINE PASSED: AI APPROVED THE CHANGE")
    sys.exit(0)

elif decision == "REQUIRES_APPROVAL":
    print("\n⏸️ PIPELINE PASSED: MANUAL APPROVAL REQUIRED")
    print("Change created in ServiceNow:", change_id)
    sys.exit(0)

else:
    print("\n❌ PIPELINE FAILED: UNKNOWN DECISION")
    sys.exit(1)
