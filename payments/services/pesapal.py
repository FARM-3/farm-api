import logging
import requests
from django.conf import settings

LOG = logging.getLogger(__name__)

# Default to the Pesapal sandbox base URL but allow overriding via Django settings
PESAPAL_DEFAULT_BASE_URL = "https://cybqa.pesapal.com/pesapalv3/api"



def get_pesapal_access_token():
    """Request an access token from Pesapal.

    This function will:
    - use `settings.PESAPAL_BASE_URL` if set, otherwise fall back to the QA URL
    - include a short timeout to avoid hanging
    - raise clear exceptions for network errors, invalid JSON, or missing token
    """
    base_url = getattr(settings, "PESAPAL_BASE_URL", PESAPAL_DEFAULT_BASE_URL)
    url = f"{base_url.rstrip('/')}/Auth/RequestToken"

    payload = {
        "consumer_key": getattr(settings, "PESAPAL_CONSUMER_KEY", None),
        "consumer_secret": getattr(settings, "PESAPAL_CONSUMER_SECRET", None),
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Quick validation of configuration
    if not payload["consumer_key"] or not payload["consumer_secret"]:
        raise Exception(
            "Pesapal credentials not configured. Please set PESAPAL_CONSUMER_KEY and PESAPAL_CONSUMER_SECRET in your environment."
        )

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
    except requests.RequestException as exc:
        LOG.exception("Network error when contacting Pesapal token endpoint")
        raise Exception(f"Network error when contacting Pesapal: {exc}") from exc

    # Try to parse JSON response
    try:
        data = response.json()
    except ValueError:
        # Include status code and a safe preview of the body to help debugging
        body_preview = (response.text[:1000] + '...') if response.text and len(response.text) > 1000 else response.text
        LOG.error("Non-JSON response from Pesapal (status=%s). Body preview: %s", response.status_code, body_preview)
        raise Exception(
            f"Invalid response from Pesapal: status={response.status_code}, body={repr(body_preview)}"
        )

    # Pesapal may return an error structure; provide helpful debugging info
    token = data.get("token")
    if not token:
        LOG.error("Pesapal token missing. Status: %s, response: %s", response.status_code, data)
        raise Exception(
            f"Pesapal token missing. Status code: {response.status_code}. Response: {data}"
        )

    return token

#This is to register an IPN URL with Pesapal
def register_ipn_url(url: str, ipn_notification_type: str = "GET") -> dict:
    """Register an IPN URL with Pesapal and return the parsed JSON response.

    Args:
        url: The publicly-accessible URL Pesapal will call for IPN notifications.
        ipn_notification_type: "GET" or "POST" (default "GET").

    Returns:
        The JSON-decoded response from Pesapal as a dict.

    Raises:
        Exception: for network/JSON errors or if Pesapal returns an error object.
    """
    token = get_pesapal_access_token()

    base_url = getattr(settings, "PESAPAL_BASE_URL", PESAPAL_DEFAULT_BASE_URL)
    endpoint = f"{base_url.rstrip('/')}/URLSetup/RegisterIPN"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "url": url,
        "ipn_notification_type": ipn_notification_type,
    }

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
    except requests.RequestException as exc:
        LOG.exception("Network error when registering IPN URL")
        raise Exception(f"Network error when registering IPN URL: {exc}") from exc

    try:
        data = resp.json()
    except ValueError:
        LOG.error("Non-JSON response from Pesapal when registering IPN: %s", resp.text)
        raise Exception(f"Invalid response from Pesapal when registering IPN: {resp.text}")

    # Pesapal may include an error object
    if data.get("error"):
        LOG.error("Pesapal returned error when registering IPN: %s", data)
        raise Exception(f"Pesapal error when registering IPN: {data}")

    return data


def get_ipn_list() -> list:
    """Fetch all registered IPN URLs for this merchant from Pesapal.

    Returns:
        A list of IPN objects as returned by Pesapal.

    Raises:
        Exception on network errors or if Pesapal returns an invalid response.
    """
    token = get_pesapal_access_token()

    base_url = getattr(settings, "PESAPAL_BASE_URL", PESAPAL_DEFAULT_BASE_URL)
    endpoint = f"{base_url.rstrip('/')}/URLSetup/GetIpnList"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
    except requests.RequestException as exc:
        LOG.exception("Network error when fetching IPN list")
        raise Exception(f"Network error when fetching IPN list: {exc}") from exc

    try:
        data = resp.json()
    except ValueError:
        LOG.error("Non-JSON response from Pesapal when fetching IPN list: %s", resp.text)
        raise Exception(f"Invalid response from Pesapal when fetching IPN list: {resp.text}")

    # Expecting a list from Pesapal
    if not isinstance(data, list):
        LOG.error("Unexpected IPN list response format: %s", data)
        raise Exception(f"Unexpected response format from Pesapal: {data}")

    return data


def submit_order_request(order: dict) -> dict:
    """Submit an order to Pesapal (SubmitOrderRequest) and return the response.

    The `order` dict should match Pesapal's expected fields (see docs):
    id, currency, amount, description, callback_url, notification_id, billing_address, etc.
    """
    token = get_pesapal_access_token()
    base_url = getattr(settings, "PESAPAL_BASE_URL", PESAPAL_DEFAULT_BASE_URL)
    endpoint = f"{base_url.rstrip('/')}/Transactions/SubmitOrderRequest"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # FIX: Convert Decimal to float for JSON serialization
    if 'amount' in order:
        from decimal import Decimal
        if isinstance(order['amount'], Decimal):
            order['amount'] = float(order['amount'])

    # FIX: Convert UUID to string for JSON serialization
    from uuid import UUID
    if 'notification_id' in order and isinstance(order['notification_id'], UUID):
        order['notification_id'] = str(order['notification_id'])

    try:
        resp = requests.post(endpoint, json=order, headers=headers, timeout=15)
    except requests.RequestException as exc:
        LOG.exception("Network error when submitting order to Pesapal")
        raise Exception(f"Network error when submitting order to Pesapal: {exc}") from exc

    try:
        data = resp.json()
    except ValueError:
        LOG.error("Non-JSON response from Pesapal when submitting order: %s", resp.text)
        raise Exception(f"Invalid response from Pesapal when submitting order: {resp.text}")

    # Pesapal signals errors via an error object or non-200 status in 'status'
    if data.get("error"):
        LOG.error("Pesapal returned error on SubmitOrderRequest: %s", data)
        raise Exception(f"Pesapal error on SubmitOrderRequest: {data}")

    return data


def get_transaction_status(order_tracking_id: str) -> dict:
    """Query Pesapal for the status of an order using its orderTrackingId.

    Args:
        order_tracking_id: The Pesapal OrderTrackingId (string GUID).

    Returns:
        The parsed JSON response from Pesapal containing transaction status details.

    Raises:
        Exception on network/JSON errors or if Pesapal returns an error structure.
    """
    if not order_tracking_id:
        raise ValueError("order_tracking_id is required")

    token = get_pesapal_access_token()
    base_url = getattr(settings, "PESAPAL_BASE_URL", PESAPAL_DEFAULT_BASE_URL)
    # Pesapal expects the orderTrackingId as a query parameter
    endpoint = f"{base_url.rstrip('/')}/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
    except requests.RequestException as exc:
        LOG.exception("Network error when querying transaction status")
        raise Exception(f"Network error when querying Pesapal transaction status: {exc}") from exc

    try:
        data = resp.json()
    except ValueError:
        LOG.error("Non-JSON response from Pesapal when fetching transaction status: %s", resp.text)
        raise Exception(f"Invalid response from Pesapal when fetching transaction status: {resp.text}")

    # Pesapal may include an error object
    if isinstance(data, dict) and data.get("error"):
        LOG.error("Pesapal returned error for transaction status: %s", data)
        # Return the raw data for caller to inspect, but raise for obvious failures
        raise Exception(f"Pesapal error when fetching transaction status: {data}")

    return data


def refund_request(confirmation_code: str, amount: float, username: str, remarks: str) -> dict:
    """Request a refund for a previously completed transaction.

    Args:
        confirmation_code: The confirmation_code returned by the payment processor (from GetTransactionStatus).
        amount: Amount to refund.
        username: Who is requesting the refund (merchant operator).
        remarks: Reason for refund.

    Returns:
        Parsed JSON response from Pesapal.

    Raises:
        Exception on network/JSON errors or if Pesapal returns an error structure.
    """
    if not confirmation_code:
        raise ValueError("confirmation_code is required")

    token = get_pesapal_access_token()
    base_url = getattr(settings, "PESAPAL_BASE_URL", PESAPAL_DEFAULT_BASE_URL)
    endpoint = f"{base_url.rstrip('/')}/Transactions/RefundRequest"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "confirmation_code": confirmation_code,
        "amount": str(amount),
        "username": username,
        "remarks": remarks,
    }

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=15)
    except requests.RequestException as exc:
        LOG.exception("Network error when submitting refund request to Pesapal")
        raise Exception(f"Network error when submitting refund request to Pesapal: {exc}") from exc

    try:
        data = resp.json()
    except ValueError:
        LOG.error("Non-JSON response from Pesapal when submitting refund: %s", resp.text)
        raise Exception(f"Invalid response from Pesapal when submitting refund: {resp.text}")

    # Pesapal returns status/message; treat error cases as exceptions for callers
    if isinstance(data, dict) and data.get("error"):
        LOG.error("Pesapal returned error on RefundRequest: %s", data)
        raise Exception(f"Pesapal error on RefundRequest: {data}")

    return data


def cancel_order(order_tracking_id: str) -> dict:
    """Cancel a previously submitted order on Pesapal.

    Args:
        order_tracking_id: The Pesapal OrderTrackingId (string GUID).

    Returns:
        Parsed JSON response from Pesapal.

    Raises:
        Exception on network/JSON errors or if Pesapal returns an error structure.
    """
    if not order_tracking_id:
        raise ValueError("order_tracking_id is required")

    token = get_pesapal_access_token()
    base_url = getattr(settings, "PESAPAL_BASE_URL", PESAPAL_DEFAULT_BASE_URL)
    endpoint = f"{base_url.rstrip('/')}/Transactions/CancelOrder"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    payload = {"order_tracking_id": str(order_tracking_id)}

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=15)
    except requests.RequestException as exc:
        LOG.exception("Network error when submitting cancel order request to Pesapal")
        raise Exception(f"Network error when submitting cancel order request to Pesapal: {exc}") from exc

    try:
        data = resp.json()
    except ValueError:
        LOG.error("Non-JSON response from Pesapal when submitting cancel order: %s", resp.text)
        raise Exception(f"Invalid response from Pesapal when submitting cancel order: {resp.text}")

    if isinstance(data, dict) and data.get("error"):
        LOG.error("Pesapal returned error on CancelOrder: %s", data)
        raise Exception(f"Pesapal error on CancelOrder: {data}")

    return data
