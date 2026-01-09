from django.urls import path
from .views import test_pesapal_auth, register_ipn, list_ipns
from .views import submit_order, get_transaction_status_view, refund_request_view, cancel_order_view

urlpatterns = [
    path("test-auth/", test_pesapal_auth),
    path("register-ipn/", register_ipn),
    path("list-ipn/", list_ipns),
    path("submit-order/", submit_order),
    path("transaction-status/", get_transaction_status_view),
    path("refund-request/", refund_request_view),
    path("cancel-order/", cancel_order_view),
]
