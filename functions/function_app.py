import azure.functions as func
import json
import logging
import os
import uuid
from azure.data.tables import TableServiceClient

# Initialize Azure Function App
app = func.FunctionApp()

# Connect to Azure Table Storage
connection_string = os.getenv("AzureWebJobsStorage")

table_service = TableServiceClient.from_connection_string(
    conn_str=connection_string
)

table_client = table_service.get_table_client(
    table_name="alerts"
)


@app.event_hub_message_trigger(
    arg_name="events",
    event_hub_name="litenergy-hub",
    connection="EventHubConnection",
    cardinality="many"
)

def EventHubProcessor(events: func.EventHubEvent):

    # Process each incoming event
    for event in events:

        try:
            # Decode Event Hub message
            event_body = event.get_body().decode("utf-8")

            # Convert JSON string to Python dictionary
            json_data = json.loads(event_body)

            # Extract telemetry fields
            device_id = json_data.get("deviceId")
            power = json_data.get("powerUsage")
            voltage = json_data.get("voltage")
            timestamp = json_data.get("timestamp")

            # Log incoming telemetry
            logging.info(
                f"📡 Received telemetry from {device_id}"
            )

            # -----------------------------
            # Detection Rule 1 — High Power Usage
            # -----------------------------
            if power is not None and power > 80:

                logging.warning(
                    f"[ALERT_TYPE=HIGH_POWER] "
                    f"Device={device_id} "
                    f"Power={power}"
                )

                alert = {
                    "PartitionKey": "alerts",
                    "RowKey": str(uuid.uuid4()),
                    "deviceId": device_id,
                    "alertType": "HighPower",
                    "severity": "High",
                    "value": power,
                    "timestamp": timestamp
                }

                # Store alert in Azure Table Storage
                table_client.create_entity(entity=alert)

                logging.warning(
                    f"⚠️ Stored high power alert for {device_id}"
                )

            # -----------------------------
            # Detection Rule 2 — Voltage Anomaly
            # -----------------------------
            if voltage is not None and (
                voltage < 210 or voltage > 240
            ):

                logging.error(
                    f"[ALERT_TYPE=VOLTAGE_ANOMALY] "
                    f"Device={device_id} "
                    f"Voltage={voltage}"
                )

                alert = {
                    "PartitionKey": "alerts",
                    "RowKey": str(uuid.uuid4()),
                    "deviceId": device_id,
                    "alertType": "VoltageAnomaly",
                    "severity": "Critical",
                    "value": voltage,
                    "timestamp": timestamp
                }

                # Store alert in Azure Table Storage
                table_client.create_entity(entity=alert)

                logging.error(
                    f"⚡ Stored voltage anomaly alert for {device_id}"
                )

        except Exception as e:

            logging.error(
                f"❌ Error processing event: {str(e)}"
            )
