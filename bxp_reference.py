import json
import time
import uuid
import hashlib
from datetime import datetime

# -----------------------------
# Exposure Event v1 (time-only)
# -----------------------------
def create_exposure_event():
    return {
        "event_id": str(uuid.uuid4()),
        "schema": "bxp.exposure_event.v1",
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "location": {
            "latitude": None,
            "longitude": None
        },
        "exposure_vector": {
            "oxygen": None,
            "nitrogen": None,
            "pollution": None,
            "pollen": None,
            "acidity": None
        },
        "notes": "time-only exposure event"
    }

# -----------------------------
# Hashing / signing (local)
# -----------------------------
def hash_payload(payload):
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

# -----------------------------
# Build BXP container
# -----------------------------
def build_bxp_container(events):
    payload = {
        "protocol": "Breathe Exposure Protocol",
        "version": "1.0",
        "owner": "user",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "events": events
    }

    payload_hash = hash_payload(payload)

    container = {
        "container_schema": "bxp.container.v1",
        "payload": payload,
        "payload_hash": payload_hash,
        "signature": payload_hash,  # self-signed v1
        "verification": {
            "method": "sha256",
            "status": "unverified"
        }
    }

    return container

# -----------------------------
# Verify container
# -----------------------------
def verify_container(container):
    recomputed = hash_payload(container["payload"])
    if recomputed == container["payload_hash"]:
        container["verification"]["status"] = "Verified"
        return True
    else:
        container["verification"]["status"] = "Tampered"
        return False

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    event = create_exposure_event()
    container = build_bxp_container([event])

    result = verify_container(container)

    with open("bxp_event.bxp.txt", "w") as f:
        json.dump(container, f, indent=2)

    print("BXP container written to bxp_export.json")
    print("Verification result:", "Verified" if result else "Failed")