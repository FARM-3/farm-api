from django.urls import path
from .views import pesapal_ipn_callback
from .views import (
    test_pesapal_auth,
    list_ipns,
    submit_order,
    get_transaction_status_view,
    refund_request_view,
    cancel_order_view,
    RegisterIPNView,
)

urlpatterns = [
    path("test-auth/", test_pesapal_auth),
    path("register-ipn/", RegisterIPNView.as_view(), name="register-ipn"),
    path("list-ipn/", list_ipns),
    path("submit-order/", submit_order),
    path("transaction-status/", get_transaction_status_view),
    path("refund-request/", refund_request_view),
    path("cancel-order/", cancel_order_view),
    path("ipn/", pesapal_ipn_callback, name="pesapal-ipn"),

]
