import os
import django
import sys
import uuid

# Add the project root to sys.path
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()

from payments.serializers import SubmitOrderSerializer

def run_tests():
    print("--- Debugging SubmitOrderSerializer ---")

    # Case 1: Missing billing_address
    print("\n[Case 1] Missing 'billing_address'")
    payload_1 = {
        "id": "12345",
        "currency": "UGX",
        "amount": "1000.00",
        "description": "Test Order",
        "callback_url": "http://localhost:3000/callback",
        "notification_id": str(uuid.uuid4()),
    }
    ser_1 = SubmitOrderSerializer(data=payload_1)
    if not ser_1.is_valid():
        print(f"Errors: {ser_1.errors}")
    else:
        print("Valid (Unexpected!)")

    # Case 2: Invalid notification_id (not a UUID)
    print("\n[Case 2] Invalid 'notification_id' (random string)")
    payload_2 = {
        "id": "12345",
        "currency": "UGX",
        "amount": "1000.00",
        "description": "Test Order",
        "callback_url": "http://localhost:3000/callback",
        "notification_id": "NOT-A-UUID",
        "billing_address": {}
    }
    ser_2 = SubmitOrderSerializer(data=payload_2)
    if not ser_2.is_valid():
        print(f"Errors: {ser_2.errors}")
    else:
        print("Valid (Unexpected!)")

    # Case 3: Valid Payload
    print("\n[Case 3] Correct Payload")
    payload_3 = {
        "id": "12345",
        "currency": "UGX",
        "amount": "1000.00",
        "description": "Test Order",
        "callback_url": "http://localhost:3000/callback",
        "notification_id": str(uuid.uuid4()),
        "billing_address": {
             "email_address": "test@example.com"
        }
    }
    ser_3 = SubmitOrderSerializer(data=payload_3)
    if ser_3.is_valid():
        print("VALID! Use this structure.")
    else:
        print(f"Errors: {ser_3.errors}")

if __name__ == "__main__":
    run_tests()
