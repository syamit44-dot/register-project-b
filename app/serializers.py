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
        fields = '__all__'

class ProfileSilonicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSilonic
        fields = '__all__'

class ProfileEggAiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileEggAi
        fields = '__all__'

class ProfileUserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUserApp
        fields = '__all__'

class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUser
        fields = '__all__'