from dataclasses import fields
from rest_framework import serializers
from .models import *

class ProfileFarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileFarm
        exclude = ['token', 'ip_address', 'ip_manage']

class ProfileDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDevice
        exclude = ['nameFarm']

class ProfileSilonicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSilonic
        exclude = ['nameFarm']

class ProfileEggAiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileEggAi
        exclude = ['nameFarm']

class ProfileUserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUserApp
        exclude = ['nameFarm']

class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUser
        exclude = ['nameFarm']