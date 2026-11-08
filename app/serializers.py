from rest_framework import serializers
from .models import *
from .farm_function import (
    RequestFarmFail,
    clean_sale_contract,
    validate_timezone_value,
    validate_username_format,
)


def _run_validator(func, *args):
    """farm_function helpers raise RequestFarmFail; convert to DRF ValidationError."""
    try:
        return func(*args)
    except RequestFarmFail as e:
        raise serializers.ValidationError(e.detail.get("detail"))


class ProfileFarmSerializer(serializers.ModelSerializer):
    # owner info (read-only) for admin views
    user = serializers.SerializerMethodField()
    timezone = serializers.CharField(max_length=50, required=False)
    saleContract = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = ProfileFarm
        exclude = ['ip_address', 'ip_manage']
        read_only_fields = ['id', 'date_created', 'date_edit', 'status']
        extra_kwargs = {
            'country': {'error_messages': {'invalid_choice': 'Invalid country "{input}".'}},
        }

    def get_user(self, obj):
        owner = obj.user
        auth_user = owner.username
        return {
            "id": owner.id,
            **ProfileUser.account_identity(auth_user, owner),
            "first_name": owner.first_name,
            "last_name": owner.last_name,
            "mobile": owner.mobile,
        }

    def validate_numbOfHouse(self, value):
        if not str(value).isdigit() or int(value) < 1:
            raise serializers.ValidationError("numbOfHouse must be a positive integer")
        return str(int(value))

    def validate_timezone(self, value):
        return _run_validator(validate_timezone_value, value)

    def validate_saleContract(self, value):
        return _run_validator(clean_sale_contract, value)


class ProfileDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDevice
        exclude = ['nameFarm']
        read_only_fields = ['id']

    def validate(self, attrs):
        # SMARTLINK ต้องมี smartlinkSN, TEMPVIEW ต้องไม่มี (EquipmentCategoryGuardMixin
        # เช็คเฉพาะ category ของ modelTemp ไม่ได้เช็ค field คู่นี้)
        device_type = attrs.get('type', getattr(self.instance, 'type', None))
        smartlink_sn = attrs.get('smartlinkSN', getattr(self.instance, 'smartlinkSN', None))
        if device_type == TypeChoices.SMARTLINK and not smartlink_sn:
            raise serializers.ValidationError({"smartlinkSN": "This field is required when type=SMARTLINK"})
        if device_type == TypeChoices.TEMPVIEW and smartlink_sn:
            raise serializers.ValidationError({"smartlinkSN": "This field must be empty when type=TEMPVIEW"})
        return attrs


class ProfileAlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAlarm
        exclude = ['nameFarm']
        read_only_fields = ['id']


class ProfileSilonicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSilonic
        exclude = ['nameFarm']
        read_only_fields = ['id']


class ProfileEggSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileEgg
        exclude = ['nameFarm']
        read_only_fields = ['id']


class ProfileUserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUserApp
        exclude = ['nameFarm']
        read_only_fields = ['id']

    def validate_username(self, value):
        return _run_validator(validate_username_format, value.strip())

    def validate_deviceModel(self, value):
        if value.category != EquipmentCategory.CONTROLLER:
            raise serializers.ValidationError("deviceModel must be a CONTROLLER model.")
        return value


class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUser
        exclude = ['id']


class EquipmentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModel
        fields = ['id', 'category', 'code', 'name']
        read_only_fields = fields
