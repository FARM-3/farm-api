from rest_framework import serializers

class RegisterIPNSerializer(serializers.Serializer):
    url = serializers.URLField()
    ipn_notification_type = serializers.ChoiceField(
        choices=["GET", "POST"],
        default="GET"
    )


class BillingAddressSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    email_address = serializers.EmailField(required=False, allow_blank=True)
    country_code = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    line_1 = serializers.CharField(required=False, allow_blank=True)
    line_2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)
    zip_code = serializers.CharField(required=False, allow_blank=True)


class SubmitOrderSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=50)
    currency = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(max_length=100)
    callback_url = serializers.URLField()
    cancellation_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    notification_id = serializers.UUIDField()
    redirect_mode = serializers.CharField(required=False, allow_blank=True, default="TOP_WINDOW")
    branch = serializers.CharField(required=False, allow_blank=True)
    billing_address = BillingAddressSerializer()


class RefundRequestSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(max_length=128)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    username = serializers.CharField(max_length=128)
    remarks = serializers.CharField(max_length=255)


class CancelOrderSerializer(serializers.Serializer):
    order_tracking_id = serializers.UUIDField()
