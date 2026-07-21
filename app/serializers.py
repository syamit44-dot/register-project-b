from dataclasses import fields
from rest_framework import serializers
from .models import *

class ProfileFarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileFarm
        fields = '__all__'

class ProfileSmartLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSmartLink
        fields = '__all__'

class ProfileTempViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileTempView
        fields = '__all__'

class ProfileSilonicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSilonic
        fields = '__all__'

class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileUser
        fields = ['id', 'username', 'userType', 'mobile']