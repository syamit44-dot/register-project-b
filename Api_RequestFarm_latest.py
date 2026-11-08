# Reconstructed from the latest version developed in this chat.
# Note: imports/model names are preserved from the conversation context where available.

from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response


class RequestFarmFail(Exception):
    def __init__(self, detail, http_status=status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.http_status = http_status
        super().__init__(str(detail))


def requset_fail(message, http_status=status.HTTP_400_BAD_REQUEST):
    raise RequestFarmFail({"message": "error", "detail": message}, http_status=http_status)


def request_farm(value, message):
    if not value:
        requset_fail(message)


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
        requset_fail(f"Invalid {label}.")
    if isinstance(value, float) and not value.is_integer():
        requset_fail(f"Invalid {label}.")
    try:
        return int(value)
    except (TypeError, ValueError):
        requset_fail(f"Invalid {label}.")


def get_list(body, key):
    value = body.get(key, [])
    if not isinstance(value, list):
        requset_fail(f"'{key}' must be a list.")
    return value


def validate_item(item, label):
    if not isinstance(item, dict):
        requset_fail(f"Invalid {label} data.")


def get_type(raw_value, existing_value=None, provided=True):
    if not provided:
        value = existing_value or TypeChoices.SMARTLINK
    else:
        value = normalize_blank(raw_value) or (existing_value or TypeChoices.SMARTLINK)
    if value not in TypeChoices.values:
        requset_fail("Invalid type. Must be one of: " + ", ".join(TypeChoices.values))
    return value


def get_user_type(raw_value, existing_value=None, provided=True):
    valid_values = [c[0] for c in ProfileUserApp.USER_CHOICES]
    if not provided:
        value = existing_value or ProfileUserApp.USER
    else:
        value = normalize_blank(raw_value) or (existing_value or ProfileUserApp.USER)
    if value not in valid_values:
        requset_fail("Invalid userType. Must be one of: " + ", ".join(valid_values))
    return value


def get_equipment_model(model_id, category):
    model_id = to_int(model_id, "equipment model id")
    if not model_id:
        requset_fail("No equipment model.")
    try:
        return EquipmentModel.objects.get(id=model_id, category=category)
    except EquipmentModel.DoesNotExist:
        requset_fail("Invalid equipment model.")


def check_dup_in_batch(value, seen_set, message):
    if value is None:
        return
    if value in seen_set:
        requset_fail(message)
    seen_set.add(value)


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
    elif device_type == TypeChoices.SMARTLINK:
        request_farm(smartlink_sn, "smartlinkSN is required for SmartLink type.")

    if "house" in device:
        house = normalize_blank(device.get("house")) or "1"
    else:
        house = (existing.house if existing else None) or "1"

    return device_type, controller_sn, smartlink_sn, house


def _clean_serial_payload(item, existing, label):
    validate_item(item, label)
    if "serialNumber" in item:
        serial_number = normalize_blank(item.get("serialNumber"))
    else:
        serial_number = existing.serialNumber if existing else None
    request_farm(serial_number, f"{label} serialNumber is required.")

    item_type = get_type(
        item.get("type"),
        existing_value=(existing.type if existing else None),
        provided="type" in item,
    )

    if "house" in item:
        house = normalize_blank(item.get("house")) or "1"
    else:
        house = (existing.house if existing else None) or "1"

    return serial_number, item_type, house


EQUIPMENT_CONFIG = (
    ("silonic", ProfileSilonic, "modelSilonic", EquipmentCategory.SILONIC, "Silonic"),
    ("egg", ProfileEgg, "modelEgg", EquipmentCategory.EGG, "Egg"),
    ("alarm", ProfileAlarm, "modelAlarm", EquipmentCategory.ALARM, "Alarm"),
)


def build_serial_equipment_batch(items, model_class, model_field, category, label, farm_obj):
    """Build bulk-create objects with validation for serial/equipment model."""
    objects = []
    seen_serials = set()

    for item in items:
        serial_number, item_type, house = _clean_serial_payload(item, None, label)
        check_dup_in_batch(serial_number, seen_serials, f"{label} serialNumber duplicated in submitted data.")

        model_id = item.get(model_field)
        equipment_model = get_equipment_model(model_id, category)

        if model_class.objects.filter(serialNumber=serial_number).exists():
            requset_fail(f"{label} serialNumber already exists in the system.")

        objects.append(
            model_class(
                nameFarm=farm_obj,
                type=item_type,
                **{model_field: equipment_model},
                house=house,
                serialNumber=serial_number,
            )
        )

    return objects


def upsert_serial_equipment(
    items,
    model_class,
    model_field,
    category,
    label,
    farm_obj,
    seen_serials=None,
):
    """Update/create serial equipment and return IDs kept in submitted sync data."""
    seen_serials = seen_serials if seen_serials is not None else set()
    seen_ids = set()
    kept_ids = []

    for item in items:
        validate_item(item, label)

        raw_id = item.get("id")
        item_id = to_int(raw_id, f"{label} id")
        if item_id is not None:
            check_dup_in_batch(item_id, seen_ids, f"{label} id duplicated in submitted data.")

        serial_number = normalize_blank(item.get("serialNumber"))
        request_farm(serial_number, f"{label} serialNumber is required.")
        check_dup_in_batch(
            serial_number,
            seen_serials,
            f"{label} serialNumber duplicated in submitted data.",
        )

        existing = None
        if item_id is not None:
            existing = model_class.objects.filter(id=item_id, nameFarm=farm_obj).first()
            if not existing:
                requset_fail(f"{label} id not found in this farm.")
        else:
            existing = model_class.objects.filter(
                serialNumber=serial_number,
                nameFarm=farm_obj,
            ).first()

        if existing:
            conflicting = model_class.objects.filter(
                serialNumber=serial_number
            ).exclude(id=existing.id).exists()
            if conflicting:
                requset_fail(f"{label} serialNumber already exists in the system.")

            item_type = get_type(
                item.get("type"),
                existing_value=existing.type,
                provided="type" in item,
            )

            if "house" in item:
                house = normalize_blank(item.get("house")) or "1"
            else:
                house = existing.house or "1"

            model_id = item.get(model_field) if model_field in item else None
            equipment_model = (
                get_equipment_model(model_id, category)
                if model_field in item
                else getattr(existing, model_field)
            )

            existing.serialNumber = serial_number
            existing.type = item_type
            existing.house = house
            setattr(existing, model_field, equipment_model)
            existing.save()
            kept_ids.append(existing.id)
        else:
            if model_class.objects.filter(serialNumber=serial_number).exists():
                requset_fail(f"{label} serialNumber already exists in the system.")

            model_id = item.get(model_field)
            equipment_model = get_equipment_model(model_id, category)
            item_type = get_type(item.get("type"), provided="type" in item)
            house = normalize_blank(item.get("house")) or "1"

            new_obj = model_class.objects.create(
                nameFarm=farm_obj,
                serialNumber=serial_number,
                type=item_type,
                house=house,
                **{model_field: equipment_model},
            )
            kept_ids.append(new_obj.id)

    return kept_ids


@api_view(["POST", "GET"])
def Api_RequestFarm(request, cmd):
    access_token = get_bearer_token(request)
    if not access_token:
        return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

    payload = jwt_decode(access_token)
    if not payload:
        return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

    if payload.get("type") != "access":
        return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

    uid = payload.get("uid")
    if not uid:
        return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

    user = ProfileUser.objects.filter(username__id=uid).first()
    if not user:
        return Response(data=TempNetResponseMsg.NO_USER, status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        if cmd == "create":
            try:
                with transaction.atomic():
                    body = request.data
                    if not isinstance(body, dict):
                        requset_fail("Data not object.")

                    farm_data = body.get("farm", {})
                    if not isinstance(farm_data, dict):
                        requset_fail("'farm' must be an object.")

                    devices = get_list(body, "device")
                    silonics = get_list(body, "silonic")
                    eggs = get_list(body, "egg")
                    alarms = get_list(body, "alarm")
                    users = get_list(body, "userapp")

                    name_farm = normalize_blank(farm_data.get("nameFarm"))
                    request_farm(name_farm, "No farm name.")

                    if ProfileFarm.objects.filter(nameFarm=name_farm).exists():
                        requset_fail("Farm name already exists in the system.")

                    farm_serializer = ProfileFarmSerializer(data=farm_data)
                    farm_serializer.is_valid(raise_exception=True)
                    farm_obj = farm_serializer.save(user=user, status=StatusChoices.PENDING)

                    devices_create = []
                    users_create = []

                    seen_controller_sn = set()
                    seen_smartlink_sn = set()
                    seen_usernames = set()
                    seen_houses = set()

                    # ---- Device ----
                    for device in devices:
                        device_type, controller_sn, smartlink_sn, house = clean_device_payload(device)
                        check_dup_in_batch(house, seen_houses, "house duplicated in submitted data.")
                        check_dup_in_batch(
                            controller_sn,
                            seen_controller_sn,
                            "controllerSN duplicated in submitted data.",
                        )
                        check_dup_in_batch(
                            smartlink_sn,
                            seen_smartlink_sn,
                            "smartlinkSN duplicated in submitted data.",
                        )

                        model_temp = get_equipment_model(
                            device.get("modelTemp"),
                            EquipmentCategory.CONTROLLER,
                        )

                        if ProfileDevice.objects.filter(controllerSN=controller_sn).exists():
                            requset_fail("controllerSN already exists in the system.")
                        if smartlink_sn and ProfileDevice.objects.filter(smartlinkSN=smartlink_sn).exists():
                            requset_fail("smartlinkSN already exists in the system.")

                        devices_create.append(
                            ProfileDevice(
                                nameFarm=farm_obj,
                                type=device_type,
                                modelTemp=model_temp,
                                house=house,
                                controllerSN=controller_sn,
                                smartlinkSN=smartlink_sn,
                            )
                        )

                    # ---- Serial equipment ----
                    silonics_create = build_serial_equipment_batch(
                        silonics,
                        ProfileSilonic,
                        "modelSilonic",
                        EquipmentCategory.SILONIC,
                        "Silonic",
                        farm_obj,
                    )
                    eggs_create = build_serial_equipment_batch(
                        eggs,
                        ProfileEgg,
                        "modelEgg",
                        EquipmentCategory.EGG,
                        "Egg",
                        farm_obj,
                    )
                    alarms_create = build_serial_equipment_batch(
                        alarms,
                        ProfileAlarm,
                        "modelAlarm",
                        EquipmentCategory.ALARM,
                        "Alarm",
                        farm_obj,
                    )

                    # ---- UserApp ----
                    for item in users:
                        validate_item(item, "userapp")
                        username = normalize_blank(item.get("username"))
                        request_farm(username, "username is required.")
                        check_dup_in_batch(username, seen_usernames, "username duplicated in submitted data.")

                        user_type = get_user_type(item.get("userType"), provided="userType" in item)
                        user_email = normalize_blank(item.get("userEmail"))

                        if ProfileUserApp.objects.filter(username=username).exists():
                            requset_fail("username already exists in the system.")

                        users_create.append(
                            ProfileUserApp(
                                nameFarm=farm_obj,
                                username=username,
                                userType=user_type,
                                userEmail=user_email,
                            )
                        )

                    if devices_create:
                        ProfileDevice.objects.bulk_create(devices_create)
                    if silonics_create:
                        ProfileSilonic.objects.bulk_create(silonics_create)
                    if eggs_create:
                        ProfileEgg.objects.bulk_create(eggs_create)
                    if alarms_create:
                        ProfileAlarm.objects.bulk_create(alarms_create)
                    if users_create:
                        ProfileUserApp.objects.bulk_create(users_create)

                return Response(
                    {"message": "ok", "farm_id": farm_obj.id},
                    status=status.HTTP_201_CREATED,
                )

            except RequestFarmFail as e:
                return Response(e.detail, status=e.http_status)
            except serializers.ValidationError as e:
                return Response(
                    {"message": "error", "detail": e.detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except IntegrityError:
                logger.exception("Api_RequestFarm integrity error")
                return Response(
                    {"message": "error", "detail": "Data already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception:
                logger.exception("Api_RequestFarm unexpected error")
                return Response(
                    {"message": "error", "detail": "Internal server error."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        elif cmd == "update":
            try:
                with transaction.atomic():
                    body = request.data
                    if not isinstance(body, dict):
                        requset_fail("Data not object.")

                    farm_data = body.get("farm", {})
                    if not isinstance(farm_data, dict):
                        requset_fail("'farm' must be an object.")

                    sync_device = "device" in body
                    sync_silonic = "silonic" in body
                    sync_egg = "egg" in body
                    sync_alarm = "alarm" in body
                    sync_userapp = "userapp" in body

                    devices = get_list(body, "device") if sync_device else []
                    silonics = get_list(body, "silonic") if sync_silonic else []
                    eggs = get_list(body, "egg") if sync_egg else []
                    alarms = get_list(body, "alarm") if sync_alarm else []
                    users = get_list(body, "userapp") if sync_userapp else []

                    farm_id = to_int(farm_data.get("id"), "farm id")
                    if not farm_id:
                        requset_fail("No farm id.")

                    farm_obj = ProfileFarm.objects.filter(id=farm_id, user=user).first()
                    if not farm_obj:
                        requset_fail(
                            "Farm not found.",
                            http_status=status.HTTP_404_NOT_FOUND,
                        )

                    if "nameFarm" in farm_data and normalize_blank(farm_data.get("nameFarm")):
                        requested_name = normalize_blank(farm_data.get("nameFarm"))
                        if ProfileFarm.objects.filter(
                            nameFarm=requested_name
                        ).exclude(id=farm_obj.id).exists():
                            requset_fail("Farm name already exists in the system.")

                    farm_data = farm_data.copy()
                    farm_data.pop("id", None)
                    farm_data.pop("nameFarm", None)

                    farm_serializer = ProfileFarmSerializer(
                        farm_obj,
                        data=farm_data,
                        partial=True,
                    )
                    farm_serializer.is_valid(raise_exception=True)
                    farm_obj = farm_serializer.save(
                        status=StatusChoices.EDIT,
                        date_edit=timezone.now(),
                    )

                    # ---- Device sync ----
                    if sync_device:
                        seen_controller_sn = set()
                        seen_smartlink_sn = set()
                        seen_device_ids = set()
                        seen_houses = set()
                        kept_device_ids = []

                        for device in devices:
                            validate_item(device, "device")
                            device_id = to_int(device.get("id"), "device id")
                            if device_id is not None:
                                check_dup_in_batch(
                                    device_id,
                                    seen_device_ids,
                                    "device id duplicated in submitted data.",
                                )

                            existing = None
                            if device_id is not None:
                                existing = ProfileDevice.objects.filter(
                                    id=device_id,
                                    nameFarm=farm_obj,
                                ).first()
                                if not existing:
                                    requset_fail("Device id not found in this farm.")

                            device_type, controller_sn, smartlink_sn, house = clean_device_payload(
                                device,
                                existing=existing,
                            )
                            check_dup_in_batch(house, seen_houses, "house duplicated in submitted data.")
                            check_dup_in_batch(
                                controller_sn,
                                seen_controller_sn,
                                "controllerSN duplicated in submitted data.",
                            )
                            check_dup_in_batch(
                                smartlink_sn,
                                seen_smartlink_sn,
                                "smartlinkSN duplicated in submitted data.",
                            )

                            model_temp = (
                                get_equipment_model(device.get("modelTemp"), EquipmentCategory.CONTROLLER)
                                if "modelTemp" in device
                                else (existing.modelTemp if existing else None)
                            )
                            if model_temp is None:
                                requset_fail("No equipment model.")

                            qs_controller = ProfileDevice.objects.filter(controllerSN=controller_sn).exclude(
                                id=existing.id if existing else None
                            )
                            if qs_controller.exists():
                                requset_fail("controllerSN already exists in the system.")

                            if smartlink_sn:
                                qs_smartlink = ProfileDevice.objects.filter(
                                    smartlinkSN=smartlink_sn
                                ).exclude(id=existing.id if existing else None)
                                if qs_smartlink.exists():
                                    requset_fail("smartlinkSN already exists in the system.")

                            if existing:
                                existing.type = device_type
                                existing.modelTemp = model_temp
                                existing.house = house
                                existing.controllerSN = controller_sn
                                existing.smartlinkSN = smartlink_sn
                                existing.save()
                                kept_device_ids.append(existing.id)
                            else:
                                new_device = ProfileDevice.objects.create(
                                    nameFarm=farm_obj,
                                    type=device_type,
                                    modelTemp=model_temp,
                                    house=house,
                                    controllerSN=controller_sn,
                                    smartlinkSN=smartlink_sn,
                                )
                                kept_device_ids.append(new_device.id)

                        ProfileDevice.objects.filter(nameFarm=farm_obj).exclude(
                            id__in=kept_device_ids
                        ).delete()

                    # ---- Serial equipment sync ----
                    if sync_silonic:
                        kept_silonic_ids = upsert_serial_equipment(
                            silonics,
                            ProfileSilonic,
                            "modelSilonic",
                            EquipmentCategory.SILONIC,
                            "Silonic",
                            farm_obj,
                        )
                        ProfileSilonic.objects.filter(nameFarm=farm_obj).exclude(
                            id__in=kept_silonic_ids
                        ).delete()

                    if sync_egg:
                        kept_egg_ids = upsert_serial_equipment(
                            eggs,
                            ProfileEgg,
                            "modelEgg",
                            EquipmentCategory.EGG,
                            "Egg",
                            farm_obj,
                        )
                        ProfileEgg.objects.filter(nameFarm=farm_obj).exclude(
                            id__in=kept_egg_ids
                        ).delete()

                    if sync_alarm:
                        kept_alarm_ids = upsert_serial_equipment(
                            alarms,
                            ProfileAlarm,
                            "modelAlarm",
                            EquipmentCategory.ALARM,
                            "Alarm",
                            farm_obj,
                        )
                        ProfileAlarm.objects.filter(nameFarm=farm_obj).exclude(
                            id__in=kept_alarm_ids
                        ).delete()

                    # ---- UserApp sync ----
                    if sync_userapp:
                        seen_usernames = set()
                        seen_user_ids = set()
                        kept_user_ids = []

                        for item in users:
                            validate_item(item, "userapp")
                            user_id = to_int(item.get("id"), "userapp id")
                            if user_id is not None:
                                check_dup_in_batch(
                                    user_id,
                                    seen_user_ids,
                                    "userapp id duplicated in submitted data.",
                                )

                            username = normalize_blank(item.get("username"))
                            request_farm(username, "username is required.")
                            check_dup_in_batch(
                                username,
                                seen_usernames,
                                "username duplicated in submitted data.",
                            )

                            existing = None
                            if user_id is not None:
                                existing = ProfileUserApp.objects.filter(
                                    id=user_id,
                                    nameFarm=farm_obj,
                                ).first()
                                if not existing:
                                    requset_fail("UserApp id not found in this farm.")
                            else:
                                existing = ProfileUserApp.objects.filter(
                                    username=username,
                                    nameFarm=farm_obj,
                                ).first()

                            if existing:
                                if ProfileUserApp.objects.filter(
                                    username=username
                                ).exclude(id=existing.id).exists():
                                    requset_fail("username already exists in the system.")

                                user_type = get_user_type(
                                    item.get("userType"),
                                    existing_value=existing.userType,
                                    provided="userType" in item,
                                )
                                user_email = (
                                    normalize_blank(item.get("userEmail"))
                                    if "userEmail" in item
                                    else existing.userEmail
                                )

                                existing.username = username
                                existing.userType = user_type
                                existing.userEmail = user_email
                                existing.save()
                                kept_user_ids.append(existing.id)
                            else:
                                if ProfileUserApp.objects.filter(username=username).exists():
                                    requset_fail("username already exists in the system.")

                                user_type = get_user_type(item.get("userType"), provided="userType" in item)
                                user_email = normalize_blank(item.get("userEmail"))

                                new_user = ProfileUserApp.objects.create(
                                    nameFarm=farm_obj,
                                    username=username,
                                    userType=user_type,
                                    userEmail=user_email,
                                )
                                kept_user_ids.append(new_user.id)

                        ProfileUserApp.objects.filter(nameFarm=farm_obj).exclude(
                            id__in=kept_user_ids
                        ).delete()

                return Response(
                    {"message": "ok", "farm_id": farm_obj.id},
                    status=status.HTTP_200_OK,
                )

            except RequestFarmFail as e:
                return Response(e.detail, status=e.http_status)
            except serializers.ValidationError as e:
                return Response(
                    {"message": "error", "detail": e.detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except IntegrityError:
                logger.exception("Api_RequestFarm integrity error")
                return Response(
                    {"message": "error", "detail": "Data already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception:
                logger.exception("Api_RequestFarm unexpected error")
                return Response(
                    {"message": "error", "detail": "Internal server error."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"message": "error", "detail": "Unknow cmd"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"message": "error", "detail": "Method not allowed for this cmd"},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )
