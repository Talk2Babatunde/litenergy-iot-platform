import json
import time
import random
from datetime import datetime
from azure.eventhub import EventHubProducerClient, EventData

# =========================
# Azure Event Hub Config
# =========================

CONNECTION_STR = (
    ""
)

EVENT_HUB_NAME = "litenergy-events"
SLEEP_INTERVAL = 2  # seconds between messages

# =========================
# Connect to Event Hub
# =========================

producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENT_HUB_NAME
)

print("🚀 IoT Simulator Started... Sending telemetry data to Azure Event Hub\n")

# =========================
# Start Simulation Loop
# =========================

try:
    while True:
        # Simulated IoT device data
        data = {
            "deviceId": f"meter-{random.randint(1, 5)}",
            "powerUsage": round(random.uniform(10, 100), 2),
            "voltage": round(random.uniform(210, 240), 2),
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }

        message = json.dumps(data)

        # Create and send event batch
        batch = producer.create_batch()
        batch.add(EventData(message))

        producer.send_batch(batch)

        print(f"✅ Sent: {message}")

        time.sleep(SLEEP_INTERVAL)

except KeyboardInterrupt:
    print("\n🛑 Simulator stopped by user")

finally:
    producer.close()
