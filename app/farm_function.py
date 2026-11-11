import re
from collections import defaultdict
import pytz
from django.db import IntegrityError
from rest_framework import serializers, status
from .models import *
from django.utils import timezone  # after the star import on purpose

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_MAIN_USERS_PER_MODEL = 5
USERNAME_REGEX = re.compile(r"[a-z0-9]+@[a-z0-9]+")
SALE_CONTRACT_KEYS = ("phone", "line", "email", "other_label", "other_value")


class RequestFarmFail(Exception):
    def __init__(self, detail, http_status=status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.http_status = http_status
        super().__init__(str(detail))


def request_fail(message, http_status=status.HTTP_400_BAD_REQUEST):
    raise RequestFarmFail({"message": "error", "detail": message}, http_status=http_status)


def request_farm(value, message):
    if not value:
        request_fail(message)


# ---------------------------------------------------------------------------
# Generic cleaners
# ---------------------------------------------------------------------------
def normalize_blank(value):
    """None / '' / '   ' -> None. Other values stay as-is (trim strings)."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def to_int(value, label):
    value = normalize_blank(value)
    if value is None:
        return None
    if isinstance(value, bool):
        request_fail(f"Invalid {label}.")
    if isinstance(value, float) and not value.is_integer():
        request_fail(f"Invalid {label}.")
    try:
        return int(value)
    except (TypeError, ValueError):
        request_fail(f"Invalid {label}.")


def get_list(body, key):
    value = body.get(key, [])
    if not isinstance(value, list):
        request_fail(f"'{key}' must be a list.")
    return value


def validate_item(item, label):
    if not isinstance(item, dict):
        request_fail(f"Invalid {label} data.")


def check_dup_in_batch(value, seen_set, message):
    if value is None:
        return
    if value in seen_set:
        request_fail(message)
    seen_set.add(value)


def get_type(raw_value, existing_value=None, provided=True):
    if not provided:
        value = existing_value or TypeChoices.SMARTLINK
    else:
        value = normalize_blank(raw_value) or (existing_value or TypeChoices.SMARTLINK)
    if value not in TypeChoices.values:
        request_fail("Invalid type. Must be one of: " + ", ".join(TypeChoices.values))
    return value


def get_user_type(raw_value, existing_value=None, provided=True):
    valid_values = [c[0] for c in ProfileUserApp.USER_CHOICES]
    if not provided:
        value = existing_value or ProfileUserApp.USER
    else:
        value = normalize_blank(raw_value) or (existing_value or ProfileUserApp.USER)
    if value == "User":
        value = ProfileUserApp.USER
    if value not in valid_values:
        request_fail("Invalid userType. Must be one of: " + ", ".join(valid_values))
    return value


def get_equipment_model(model_id, *categories):
    model_id = to_int(model_id, "equipment model id")
    if not model_id:
        request_fail("No equipment model.")
    try:
        return EquipmentModel.objects.get(id=model_id, category__in=categories)
    except EquipmentModel.DoesNotExist:
        request_fail("Invalid equipment model.")


def normalize_house(value, existing_value=None):
    """House number is a positive integer stored as string ('1'..'N')."""
    value = normalize_blank(value)
    if value is None:
        value = existing_value or "1"
    number = to_int(value, "house")
    if number is None or number < 1:
        request_fail("Invalid house.")
    return str(number)


# ---------------------------------------------------------------------------
# Field validators (shared by serializers and views)
# ---------------------------------------------------------------------------
def validate_username_format(username):
    if not username or len(username) > 50 or not USERNAME_REGEX.fullmatch(username):
        request_fail("App usernames must be name@farm using lowercase English letters and digits only (up to 50 characters).")
    return username


def validate_timezone_value(value):
    if value not in pytz.all_timezones_set:
        request_fail(f"Invalid timezone '{value}'. Use an IANA name such as Asia/Bangkok.")
    return value


def clean_sale_contract(value):
    """saleContract JSON: dict with only known string keys (blank values dropped)."""
    if value is None:
        return None
    if not isinstance(value, dict):
        request_fail("saleContract must be an object.")
    cleaned = {}
    for key, raw in value.items():
        if key not in SALE_CONTRACT_KEYS:
            request_fail(f"Unknown saleContract key '{key}'.")
        if raw is not None and not isinstance(raw, str):
            request_fail(f"saleContract.{key} must be a string.")
        raw = normalize_blank(raw)
        if raw is None:
            continue
        if len(raw) > 200:
            request_fail(f"saleContract.{key} is too long.")
        cleaned[key] = raw
    return cleaned or None


def get_num_houses(farm_obj):
    value = str(farm_obj.numbOfHouse or "").strip()
    if not value.isdigit() or int(value) < 1:
        request_fail("Invalid numbOfHouse.")
    return int(value)


# ---------------------------------------------------------------------------
# Farm
# ---------------------------------------------------------------------------
def create_farm(farm_data, owner, farm_serializer_class):
    """Validate + create ProfileFarm (status PENDING). Readable errors for duplicates."""
    name_farm = normalize_blank(farm_data.get("nameFarm"))
    request_farm(name_farm, "No farm name.")
    if ProfileFarm.objects.filter(nameFarm=name_farm).exists():
        request_fail("Farm name already exists in the system.")

    farm_serializer = farm_serializer_class(data=farm_data)
    farm_serializer.is_valid(raise_exception=True)
    try:
        return farm_serializer.save(user=owner, status=StatusChoices.PENDING)
    except IntegrityError:
        request_fail("Farm name already exists in the system.")


def update_farm(farm_obj, farm_data, farm_serializer_class):
    """
    Partially update a farm awaiting approval and return it to review.
    """
    farm_data = dict(farm_data)
    for key in ("id", "status", "user", "date_created", "date_edit"):
        farm_data.pop(key, None)

    farm_serializer = farm_serializer_class(farm_obj, data=farm_data, partial=True)
    farm_serializer.is_valid(raise_exception=True)
    return farm_serializer.save(date_edit=timezone.now(), status=StatusChoices.EDIT)


# ---------------------------------------------------------------------------
# Devices (controller, 1 row per house)
# ---------------------------------------------------------------------------
def clean_device_payload(device, existing=None):
    validate_item(device, "device")

    device_type = get_type(
        device.get("type"),
        existing_value=(existing.type if existing else None),
        provided="type" in device,
    )

    if "controllerSN" in device:
        controller_sn = normalize_blank(device.get("controllerSN"))
    else:
        controller_sn = existing.controllerSN if existing else None
    request_farm(controller_sn, "controllerSN is required.")

    if "smartlinkSN" in device:
        smartlink_sn = normalize_blank(device.get("smartlinkSN"))
    else:
        smartlink_sn = existing.smartlinkSN if existing else None

    if device_type == TypeChoices.TEMPVIEW:
        smartlink_sn = None
    else:
        request_farm(smartlink_sn, "smartlinkSN is required for SmartLink type.")

    house = normalize_house(device.get("house") if "house" in device else None,
                            existing.house if existing else None)

    return device_type, controller_sn, smartlink_sn, house


def sync_devices(farm_obj, items):
    """Upsert devices by id, delete rows not submitted. Returns kept ids."""
    seen_ids, seen_houses, seen_controller, seen_smartlink = set(), set(), set(), set()
    prepared = []

    for device in items:
        validate_item(device, "device")
        device_id = to_int(device.get("id"), "device id")
        check_dup_in_batch(device_id, seen_ids, "device id duplicated in submitted data.")

        existing = None
        if device_id is not None:
            existing = ProfileDevice.objects.filter(id=device_id, nameFarm=farm_obj).first()
            if not existing:
                request_fail("Device id not found in this farm.")

        device_type, controller_sn, smartlink_sn, house = clean_device_payload(device, existing)
        check_dup_in_batch(house, seen_houses, f"Device house {house} duplicated in submitted data.")
        check_dup_in_batch(controller_sn, seen_controller, "controllerSN duplicated in submitted data.")
        check_dup_in_batch(smartlink_sn, seen_smartlink, "smartlinkSN duplicated in submitted data.")

        if "modelTemp" in device:
            model_temp = get_equipment_model(device.get("modelTemp"), EquipmentCategory.CONTROLLER)
        elif existing:
            model_temp = existing.modelTemp
        else:
            request_fail("No equipment model.")

        exclude_id = existing.id if existing else None
        if ProfileDevice.objects.filter(controllerSN=controller_sn).exclude(id=exclude_id).exists():
            request_fail("controllerSN already exists in the system.")
        if smartlink_sn and ProfileDevice.objects.filter(smartlinkSN=smartlink_sn).exclude(id=exclude_id).exists():
            request_fail("smartlinkSN already exists in the system.")

        prepared.append((existing, device_type, model_temp, house, controller_sn, smartlink_sn))

    # delete rows that were not submitted first (frees unique house / serial values)
    keep_ids = [p[0].id for p in prepared if p[0]]
    ProfileDevice.objects.filter(nameFarm=farm_obj).exclude(id__in=keep_ids).delete()

    for existing, device_type, model_temp, house, controller_sn, smartlink_sn in prepared:
        if existing:
            existing.type = device_type
            existing.modelTemp = model_temp
            existing.house = house
            existing.controllerSN = controller_sn
            existing.smartlinkSN = smartlink_sn
            existing.save()
        else:
            ProfileDevice.objects.create(
                nameFarm=farm_obj, type=device_type, modelTemp=model_temp,
                house=house, controllerSN=controller_sn, smartlinkSN=smartlink_sn,
            )


# ---------------------------------------------------------------------------
# Serial equipment (alarm / egg / silonic, 1 row per house)
# ---------------------------------------------------------------------------
EQUIPMENT_CONFIG = (
    ("silonic", ProfileSilonic, "modelSilonic", EquipmentCategory.SILONIC, "Silonic"),
    ("egg", ProfileEgg, "modelEgg", EquipmentCategory.EGG, "Egg"),
    ("alarm", ProfileAlarm, "modelAlarm", EquipmentCategory.ALARM, "Alarm"),
)


def sync_serial_equipment(farm_obj, items, model_class, model_field, category, label):
    """Upsert by id (or create), delete rows not submitted."""
    seen_ids, seen_serials, seen_houses = set(), set(), set()
    prepared = []

    for item in items:
        validate_item(item, label)
        item_id = to_int(item.get("id"), f"{label} id")
        check_dup_in_batch(item_id, seen_ids, f"{label} id duplicated in submitted data.")

        existing = None
        if item_id is not None:
            existing = model_class.objects.filter(id=item_id, nameFarm=farm_obj).first()
            if not existing:
                request_fail(f"{label} id not found in this farm.")

        serial_number = normalize_blank(item.get("serialNumber")) if "serialNumber" in item \
            else (existing.serialNumber if existing else None)
        request_farm(serial_number, f"{label} serialNumber is required.")
        check_dup_in_batch(serial_number, seen_serials, f"{label} serialNumber duplicated in submitted data.")

        house = normalize_house(item.get("house") if "house" in item else None,
                                existing.house if existing else None)
        check_dup_in_batch(house, seen_houses, f"{label} house {house} duplicated in submitted data.")

        item_type = get_type(
            item.get("type"),
            existing_value=(existing.type if existing else None),
            provided="type" in item,
        )

        if model_field in item:
            equipment_model = get_equipment_model(item.get(model_field), category)
        elif existing:
            equipment_model = getattr(existing, model_field)
        else:
            request_fail("No equipment model.")

        exclude_id = existing.id if existing else None
        if model_class.objects.filter(serialNumber=serial_number).exclude(id=exclude_id).exists():
            request_fail(f"{label} serialNumber already exists in the system.")

        extra = {}
        if model_class is ProfileSilonic:
            use_app = item.get("useApp", bool(existing and existing.useApp and item_type == TypeChoices.SMARTLINK))
            if not isinstance(use_app, bool) or (use_app and item_type != TypeChoices.SMARTLINK):
                request_fail("Weight Scale app use requires SmartLink and a boolean useApp value.")
            extra["useApp"] = use_app
        prepared.append((existing, item_type, equipment_model, house, serial_number, extra))

    keep_ids = [p[0].id for p in prepared if p[0]]
    model_class.objects.filter(nameFarm=farm_obj).exclude(id__in=keep_ids).delete()

    for existing, item_type, equipment_model, house, serial_number, extra in prepared:
        if existing:
            existing.type = item_type
            existing.house = house
            existing.serialNumber = serial_number
            setattr(existing, model_field, equipment_model)
            for key, value in extra.items():
                setattr(existing, key, value)
            existing.save()
        else:
            model_class.objects.create(
                nameFarm=farm_obj, type=item_type, house=house,
                serialNumber=serial_number, **{model_field: equipment_model}, **extra,
            )


# ---------------------------------------------------------------------------
# App users (username = name@farm, bound to an installed app-capable model)
# ---------------------------------------------------------------------------
def sync_userapps(farm_obj, items):
    """Upsert by id/username, delete rows not submitted."""
    seen_ids, seen_usernames = set(), set()
    prepared = []

    for item in items:
        validate_item(item, "userapp")
        user_id = to_int(item.get("id"), "userapp id")
        check_dup_in_batch(user_id, seen_ids, "userapp id duplicated in submitted data.")

        username = normalize_blank(item.get("username"))
        request_farm(username, "username is required.")
        check_dup_in_batch(username, seen_usernames, f"username '{username}' duplicated in submitted data.")

        existing = None
        if user_id is not None:
            existing = ProfileUserApp.objects.filter(id=user_id, nameFarm=farm_obj).first()
            if not existing:
                request_fail("UserApp id not found in this farm.")

        if existing is None or existing.username != username:
            validate_username_format(username)

        if ProfileUserApp.objects.filter(username=username).exclude(id=existing.id if existing else None).exists():
            request_fail(f"username '{username}' already exists in the system.")

        if "deviceModel" in item:
            device_model = get_equipment_model(item.get("deviceModel"), *ProfileUserApp.APP_EQUIPMENT_CATEGORIES)
        elif existing:
            device_model = existing.deviceModel
        else:
            request_fail("userapp deviceModel is required.")

        user_type = get_user_type(
            item.get("userType"),
            existing_value=(existing.userType if existing else None),
            provided="userType" in item,
        )
        user_email = normalize_blank(item.get("userEmail")) if "userEmail" in item \
            else (existing.userEmail if existing else None)

        is_dealer = item.get("isDealer", existing.isDealer if existing else False)
        if not isinstance(is_dealer, bool):
            request_fail("isDealer must be a boolean.")
        prepared.append((existing, username, device_model, user_type, user_email, is_dealer))

    users_by_model = defaultdict(list)
    for _, _, device_model, user_type, _, is_dealer in prepared:
        users_by_model[device_model].append((user_type, is_dealer))

    for model, users in users_by_model.items():
        dealer_count = sum(is_dealer for _, is_dealer in users)
        if dealer_count and farm_obj.user.account_type != WebUserType.DEALER:
            request_fail("Only Distributor accounts can add a Distributor app user.")
        if dealer_count > 1:
            request_fail(f"{model.name}: only one Distributor app user is allowed per model.")

        main_count = len(users) - dealer_count
        main_superusers = sum(user_type == ProfileUserApp.SUPERUSER and not is_dealer for user_type, is_dealer in users)
        if main_count > MAX_MAIN_USERS_PER_MODEL or main_superusers > 1:
            # Preserve legacy counts on their current model without allowing them to grow.
            previous_main = farm_obj.userapps.filter(deviceModel=model, isDealer=False)
            if main_count > MAX_MAIN_USERS_PER_MODEL and main_count > previous_main.count():
                request_fail(f"{model.name}: maximum {MAX_MAIN_USERS_PER_MODEL} main app users per model.")
            if main_superusers > 1 and main_superusers > previous_main.filter(userType=ProfileUserApp.SUPERUSER).count():
                request_fail(f"{model.name}: only one main app user can be a Superuser per model.")

    keep_ids = [p[0].id for p in prepared if p[0]]
    ProfileUserApp.objects.filter(nameFarm=farm_obj).exclude(id__in=keep_ids).delete()

    for existing, username, device_model, user_type, user_email, is_dealer in prepared:
        if existing:
            existing.username = username
            existing.deviceModel = device_model
            existing.userType = user_type
            existing.userEmail = user_email
            existing.isDealer = is_dealer
            existing.save()
        else:
            ProfileUserApp.objects.create(
                nameFarm=farm_obj, username=username, deviceModel=device_model,
                userType=user_type, userEmail=user_email, isDealer=is_dealer,
            )


# ---------------------------------------------------------------------------
# Whole-farm consistency (call after all syncs, inside the transaction)
# ---------------------------------------------------------------------------
def validate_farm_consistency(farm_obj):
    """
    - every house 1..numbOfHouse has at least one equipment row
    - no house outside 1..numbOfHouse
    - each app user's model belongs to a controller or an app-enabled SmartLink scale in this farm
    """
    num_houses = get_num_houses(farm_obj)

    houses = set()
    for _key, model_class, _field, _category, _label in EQUIPMENT_CONFIG:
        houses.update(model_class.objects.filter(nameFarm=farm_obj).values_list("house", flat=True))
    houses.update(ProfileDevice.objects.filter(nameFarm=farm_obj).values_list("house", flat=True))

    valid = {str(i) for i in range(1, num_houses + 1)}
    extra = sorted(houses - valid, key=lambda h: int(h) if h.isdigit() else 0)
    if extra:
        request_fail(f"House {', '.join(extra)} is outside numbOfHouse ({num_houses}).")
    missing = sorted(valid - houses, key=int)
    if missing:
        request_fail(f"House {', '.join(missing)} has no equipment. Every house needs at least 1 device.")

    app_model_ids = set(
        ProfileDevice.objects.filter(nameFarm=farm_obj).values_list("modelTemp_id", flat=True)
    )
    app_model_ids.update(ProfileSilonic.objects.filter(
        nameFarm=farm_obj, type=TypeChoices.SMARTLINK, useApp=True,
    ).values_list("modelSilonic_id", flat=True))
    for username, model_id in ProfileUserApp.objects.filter(nameFarm=farm_obj).values_list("username", "deviceModel_id"):
        if model_id not in app_model_ids:
            request_fail(f"User '{username}' must be bound to a controller or an app-enabled SmartLink Weight Scale in this farm.")


def sync_farm_children(farm_obj, body):
    """
    Sync every child table that is present in body (device/silonic/egg/alarm/userapp),
    then run validate_farm_consistency. Must be called inside transaction.atomic().
    """
    if "device" in body:
        sync_devices(farm_obj, get_list(body, "device"))
    for key, model_class, model_field, category, label in EQUIPMENT_CONFIG:
        if key in body:
            sync_serial_equipment(farm_obj, get_list(body, key), model_class, model_field, category, label)
    if "userapp" in body:
        sync_userapps(farm_obj, get_list(body, "userapp"))
    validate_farm_consistency(farm_obj)


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------
def on_farm_approved(farm):
    """
    Called inside the approve transaction right after the farm status becomes APPROVE.
    Stub for now: later this will push the farm data to another system.
    If it raises, the whole approval is rolled back.
    """
    return None
