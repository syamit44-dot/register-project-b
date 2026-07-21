from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
import uuid

admin.site.site_header = "TempNet Register V.zero"
admin.site.site_title = 'TempNet'
admin.site.unregister(Group)

def new_generate_token(modeladmin, request, queryset):
    queryset.update(token=uuid.uuid1().hex)

def generate_farm_id(modeladmin, request, queryset):
    queryset.update(farmId=uuid.uuid4().hex)

class ProfileFarmAdmin(admin.ModelAdmin):
    list_display = ('nameFarm', 'modelTemp', 'numbOfHouse', 'ip_address')
    search_fields = ['nameFarm', 'modelTemp', 'numbOfHouse', 'ip_address']
admin.site.register(ProfileFarm, ProfileFarmAdmin)

class ProfileUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'token')
    search_fields = ('username', 'first_name', 'last_name', 'token')
admin.site.register(ProfileUser, ProfileUserAdmin)

class ProfileSmartLinkAdmin(admin.ModelAdmin):
    list_display = ('nameFarm', 'house', 'serialNumber')
    search_fields = ['nameFarm', 'house', 'serialNumber']
admin.site.register(ProfileSmartLink, ProfileSmartLinkAdmin)

class ProfileSilonicAdmin(admin.ModelAdmin):
    list_display = ('nameFarm', 'house', 'serialNumber')
    search_fields = ['nameFarm', 'house', 'serialNumber']
admin.site.register(ProfileSilonic, ProfileSilonicAdmin)

class ProfileTempViewAdmin(admin.ModelAdmin):
    list_display = ('nameFarm', 'house')
    search_fields = ['nameFarm', 'house']
admin.site.register(ProfileTempView, ProfileTempViewAdmin)