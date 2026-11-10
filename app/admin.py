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

class ModelIpAddressInline(admin.TabularInline):
    model = ModelIpAddress
    fk_name = "model"
    extra = 1

class EquipmentModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'code')
    list_filter = ('category',)
    search_fields = ['name', 'code']
    inlines = [ModelIpAddressInline]
admin.site.register(EquipmentModel, EquipmentModelAdmin)

class ModelIpAddressAdmin(admin.ModelAdmin):
    list_display = ('model', 'ipAddress')
    search_fields = ['model', 'ipAddress']
admin.site.register(ModelIpAddress, ModelIpAddressAdmin)

class AccessKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'sale', 'is_used', 'created_at', 'used_at', 'expired_at')
    search_fields = ['user', 'sale']
    exclude = ('key',)
admin.site.register(AccessKey, AccessKeyAdmin)

class ProfileDeviceInline(admin.TabularInline):
    model = ProfileDevice
    extra = 0
    autocomplete_fields = ['nameFarm']

class ProfileAlarmInline(admin.TabularInline):
    model = ProfileAlarm
    extra = 0
    autocomplete_fields = ['nameFarm']

class ProfileSilonicInline(admin.TabularInline):
    model = ProfileSilonic
    extra = 0
    autocomplete_fields = ['nameFarm']

class ProfileEggInline(admin.TabularInline):
    model = ProfileEgg
    extra = 0
    autocomplete_fields = ['nameFarm']

class ProfileUserAppInline(admin.TabularInline):
    model = ProfileUserApp
    extra = 0
    autocomplete_fields = ['nameFarm']

class ProfileFarmMenu(admin.ModelAdmin):
    list_display = ('nameFarm', 'numbOfHouse', 'ip_address', 'date_created')
    search_fields = ['nameFarm', 'numbOfHouse', 'ip_address']

    def number_Of_House(self, obj):
        _numberOfHouse = ProfileDevice.objects.filter(nameFarm=obj.id).count()
        _numberOfHouse += ProfileAlarm.objects.filter(nameFarm=obj.id).count()
        _numberOfHouse += ProfileSilonic.objects.filter(nameFarm=obj.id).count()
        _numberOfHouse += ProfileEgg.objects.filter(nameFarm=obj.id).count()
        _numberOfHouse += ProfileUserApp.objects.filter(nameFarm=obj.id).count()
        return _numberOfHouse

    inlines = [ProfileDeviceInline, ProfileAlarmInline, ProfileSilonicInline, ProfileEggInline, ProfileUserAppInline]
admin.site.register(ProfileFarm, ProfileFarmMenu)

class ProfileUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'token')
    search_fields = ('username', 'first_name', 'last_name', 'token')
admin.site.register(ProfileUser, ProfileUserAdmin)

class ProfileDeviceAdmin(admin.ModelAdmin):
    list_display = ('nameFarm', 'modelTemp', 'house', 'controllerSN', 'smartlinkSN')
    search_fields = ['nameFarm', 'modelTemp', 'controllerSN', 'smartlinkSN']
admin.site.register(ProfileDevice, ProfileDeviceAdmin)

class ProfileAlarmAdmin(admin.ModelAdmin):
    list_display = ('nameFarm', 'house', 'serialNumber')
    search_fields = ['nameFarm', 'serialNumber']
admin.site.register(ProfileAlarm, ProfileAlarmAdmin)

class ProfileSilonicAdmin(admin.ModelAdmin):
    list_display = ('nameFarm', 'house', 'serialNumber')
    search_fields = ['nameFarm', 'serialNumber']
admin.site.register(ProfileSilonic, ProfileSilonicAdmin)

class ProfileEggAdmin(admin.ModelAdmin):
    list_display = ('nameFarm', 'house', 'serialNumber')
    search_fields = ['nameFarm', 'serialNumber']
admin.site.register(ProfileEgg, ProfileEggAdmin)