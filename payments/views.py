from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status

from .services.pesapal import (
    get_pesapal_access_token,
    get_transaction_status,
    refund_request,
    register_ipn_url,
    get_ipn_list,
    submit_order_request,
    cancel_order,
)

from .serializers import (
    SubmitOrderSerializer,
    RefundRequestSerializer,
    CancelOrderSerializer,
)


@api_view(["GET"])
def test_pesapal_auth(request):
    try:
        token = get_pesapal_access_token()
    except Exception as exc:
        # Return a friendly JSON error instead of a raw 500 stack trace
        # Provide a safe preview of the PESAPAL key and base URL that this
        # running process currently sees. This helps diagnose when the
        # dev server didn't pick up .env changes. We never return the full
        # secret - only the first/last 4 chars as a mask.
        key = getattr(settings, 'PESAPAL_CONSUMER_KEY', None)
        if key:
            key_preview = f"{key[:4]}...{key[-4:]}"
        else:
            key_preview = None

        base_url = getattr(settings, 'PESAPAL_BASE_URL', None)

        return Response({
            "success": False,
            "error": str(exc),
            "pesapal_key_preview": key_preview,
            "pesapal_base_url": base_url,
        }, status=400)

    return Response({"success": True, "token": token})


@api_view(["POST"])
def register_ipn(request):
    """Register an IPN URL with Pesapal.

    Expected body: { "url": "https://yourdomain.com/ipn", "ipn_notification_type": "GET" }
    """
    url = request.data.get("url")
    ipn_type = request.data.get("ipn_notification_type", "GET")

    if not url:
        return Response({"success": False, "error": "url is required"}, status=400)

    try:
        data = register_ipn_url(url, ipn_type)
    except Exception as exc:
        return Response({"success": False, "error": str(exc)}, status=400)

    return Response({"success": True, "data": data})


@api_view(["POST"])
def refund_request_view(request):
    """Submit a refund request to Pesapal.

    Expected body: { confirmation_code, amount, username, remarks }
    """
    serializer = RefundRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "errors": serializer.errors}, status=400)

    payload = serializer.validated_data

    try:
        res = refund_request(
            confirmation_code=payload["confirmation_code"],
            amount=payload["amount"],
            username=payload["username"],
            remarks=payload["remarks"],
        )
    except Exception as exc:
        return Response({"success": False, "error": str(exc)}, status=400)

    return Response({"success": True, "data": res})


@api_view(["POST"])
def cancel_order_view(request):
    """Cancel a pending/failed order on Pesapal.

    Expected body: { "order_tracking_id": "<guid>" }
    """
    serializer = CancelOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "errors": serializer.errors}, status=400)

    order_tracking_id = serializer.validated_data["order_tracking_id"]

    try:
        res = cancel_order(order_tracking_id)
    except Exception as exc:
        return Response({"success": False, "error": str(exc)}, status=400)

    return Response({"success": True, "data": res})


@api_view(["GET"])
def list_ipns(request):
    """Return the list of IPN URLs registered with Pesapal for this merchant."""
    try:
        data = get_ipn_list()
    except Exception as exc:
        return Response({"success": False, "error": str(exc)}, status=400)

    return Response({"success": True, "data": data})


@api_view(["POST"])
def submit_order(request):
    """Accepts order details from frontend, validates them, submits to Pesapal and returns redirect_url."""
    serializer = SubmitOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    order_payload = serializer.validated_data

    try:
        res = submit_order_request(order_payload)
    except Exception as exc:
        return Response({"success": False, "error": str(exc)}, status=400)

    return Response({"success": True, "data": res})


@api_view(["GET"])
def get_transaction_status_view(request):
    """Query Pesapal for transaction status using orderTrackingId (query param).

    Expects: /api/payments/transaction-status/?orderTrackingId=<guid>
    """
    order_id = request.query_params.get("orderTrackingId") or request.query_params.get("order_tracking_id")
    if not order_id:
        return Response({"success": False, "error": "orderTrackingId query parameter is required"}, status=400)

    try:
        data = get_transaction_status(order_id)
    except Exception as exc:
        return Response({"success": False, "error": str(exc)}, status=400)

    return Response({"success": True, "data": data})
