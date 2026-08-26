from dataclasses import fields
from rest_framework import serializers
from .models import *

class ProfileFarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileFarm
        exclude = ['id', 'user', 'ip_address', 'ip_manage']
        read_only_fields = ['date_edit', 'status']

class ProfileDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDevice
        exclude = ['nameFarm', 'id']

class ProfileAlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAlarm
        exclude = ['nameFarm', 'id']

class ProfileSilonicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSilonic
        exclude = ['nameFarm', 'id']

class ProfileEggSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileEgg
        exclude = ['nameFarm', 'id']

class ProfileUserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUserApp
        exclude = ['nameFarm', 'id']

class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUser
        exclude = ['nameFarm', 'id']