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

print("===== LOADING CHANGE PAYLOAD =====")
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

resp_json = response.json()

# ServiceNow usually wraps response inside "result"
result = resp_json.get("result", resp_json)

print("\n===== PARSED RESPONSE =====")
print(json.dumps(result, indent=2))

decision = result.get("decision")
ai_risk = result.get("ai_risk")
confidence = result.get("confidence")
explanation = result.get("ai_explanation") or result.get("reason")
change_sys_id = result.get("change_sys_id")

# Optional audit data (if returned)
historical_changes = result.get("historical_changes", [])
recent_incidents = result.get("recent_incidents", [])

print("\n===== AI DECISION SUMMARY =====")
print(f"Decision    : {decision}")
print(f"AI Risk     : {ai_risk}")
print(f"Confidence  : {confidence}")
print(f"Explanation : {explanation}")
print(f"Change ID   : {change_sys_id}")

# ---------------- PRINT HISTORY ----------------

print("\n===== HISTORICAL CHANGES USED =====")
if not historical_changes:
    print("No historical changes provided")
else:
    for chg in historical_changes:
        print(
            f"{chg.get('number')} | "
            f"{chg.get('short_description')} | "
            f"Outcome: {chg.get('outcome')}"
        )

print("\n===== RECENT INCIDENTS USED =====")
if not recent_incidents:
    print("No incidents provided")
else:
    for inc in recent_incidents:
        print(
            f"{inc.get('number')} | "
            f"{inc.get('short_description')}"
        )

# ---------------- PIPELINE DECISION ----------------

if decision == "BLOCK":
    print("\n❌ PIPELINE FAILED: AI BLOCKED THE CHANGE")
    sys.exit(1)

elif decision == "REQUIRES_APPROVAL":
    print("\n⏸️ PIPELINE PAUSED: MANUAL APPROVAL REQUIRED")
    sys.exit(0)  # pipeline passes, human approval in SN

elif decision in ["AUTO_APPROVE", "APPROVE"]:
    print("\n✅ PIPELINE PASSED: CHANGE APPROVED")
    sys.exit(0)

else:
    print("\n❌ PIPELINE FAILED: UNKNOWN DECISION")
    sys.exit(1)

