import pytz
from dateutil import parser
import re
from datetime import datetime, date, timedelta
from typing import Literal
from django.db import models
from .models import *
import requests
from django.conf import settings

def ConvertLocalTimeStringtoUTCWithoutOffset(date_time: str | datetime | None) -> str | None:
	if date_time == None:
		return None
	else:
		if isinstance(date_time, str):
			date_time = parser.parse(date_time)
			utc_datetime = f"{date_time.year}-{date_time.month:02d}-{date_time.day:02d}T{date_time.hour:02d}:{date_time.minute:02d}:{date_time.second:02d}.000Z"
			return utc_datetime
		elif isinstance(date_time, datetime):
			utc_datetime = f"{date_time.year}-{date_time.month:02d}-{date_time.day:02d}T{date_time.hour:02d}:{date_time.minute:02d}:{date_time.second:02d}.000Z"
			return utc_datetime
		else:
			return None


def ConvertUTCToTimestamp(date_time: datetime) -> int:
	if date_time == None:
		return None
	else:
		if type(date_time) == str:
			date_time = parser.parse(date_time)
		if date_time.tzinfo == None:
			date_time = pytz.timezone("Asia/Bangkok").localize(date_time)
		utc_offset = date_time.utcoffset() or timedelta(0)
		offset_hours = int(utc_offset.total_seconds() / 3600)
		new_datetime = date_time + timedelta(hours=offset_hours)
		return int(new_datetime.timestamp())


def ConvertLocalTimeStringtoUTC(date_time: str | datetime | None) -> datetime | None:
	if date_time == None:
		return None
	else:
		if isinstance(date_time, str):
			try:
				date_time = parser.parse(date_time)
			except ValueError:
				return None
			utc_datetime = date_time.astimezone(pytz.utc).replace(microsecond=(date_time.microsecond // 1000) * 1000)
			return utc_datetime
		elif isinstance(date_time, datetime):
			utc_datetime = date_time.astimezone(pytz.utc).replace(microsecond=(date_time.microsecond // 1000) * 1000)
			return utc_datetime
		else:
			return None


def ConvertLocalTimeStringtoUTCWithTZ(date_time: str | datetime | None) -> datetime | None:
	if date_time == None:
		return None
	else:
		local = pytz.timezone("Asia/Bangkok")
		if isinstance(date_time, str):
			date_time = parser.parse(date_time)
			local_datetime = local.localize(date_time, is_dst=None)
			utc_datetime = local_datetime.astimezone(pytz.utc)
			utc_datetime_str = utc_datetime.strftime("%Y-%m-%dT%H:%M:%S")
			return datetime.strptime(utc_datetime_str, "%Y-%m-%dT%H:%M:%S")
		elif isinstance(date_time, datetime):
			local_datetime = local.localize(date_time, is_dst=None)
			utc_datetime = local_datetime.astimezone(pytz.utc)
			utc_datetime_str = utc_datetime.strftime("%Y-%m-%dT%H:%M:%S")
			return datetime.strptime(utc_datetime_str, "%Y-%m-%dT%H:%M:%S")
		else:
			return None


def ConvertUTCTimeStringtoLocalStr(date_time: str | datetime | None) -> str | None:
	if date_time == None:
		return None
	if type(date_time) is str:
		date_time = parser.parse(date_time)
	return str(date_time)


def DateStrToDateObject(date_str: str | date | None) -> date | None:
	"""
	****************************************************************************
	*	Description:
	*		Convert datetime string to datetime object
	*		Support format: yyyy-mm-dd, dd-mm-yyyy, dd/mm/yyyy
	*	Arguments:
	*		date_str: datetime string
	*	Returns:
	*		datetime object or None if error
	*		yyyy-mm-dd
	*	History:
	*		2025-10-10			Add support dd/mm/yyyy
	****************************************************************************
	"""
	if date_str == None:
		return None
	try:
		date_str = str(date_str)
		if date_str.find('/') != -1:
			date_str = date_str.replace('/', '-')
			date_time = parser.parse(date_str, dayfirst=True)
		else:
			date_time = parser.parse(date_str)
		return date_time.date()
	except ValueError:
		return None


def DateTimeStrToDateTimeObject(date_str: str | datetime | None) -> datetime | None:
	"""
	****************************************************************************
	*	Description:
	*		Convert datetime string to datetime object
	*		Support format: yyyy-mm-dd, dd-mm-yyyy, dd/mm/yyyy
	*	Arguments:
	*		date_str: datetime string
	*	Returns:
	*		datetime object or None if error
	*		yyyy-mm-dd HH:MM:SS
	*	History:
	*		2025-10-10			Add support dd/mm/yyyy
	****************************************************************************
	"""
	if date_str == None:
		return
	try:
		date_str = str(date_str)
		if date_str.find('/') != -1:
			date_str = date_str.replace('/', '-')
			date_time = parser.parse(date_str, dayfirst=True)
		else:
			date_time = parser.parse(date_str)
		return date_time
	except ValueError:
		return None


def GetDays(date1: date | str | None, date2: date | str | None, _type: Literal['int', 'str'] = 'int') -> int | str:
	if isinstance(date1, str):
		date1 = DateStrToDateObject(date1)
	if isinstance(date2, str):
		date2 = DateStrToDateObject(date2)
	if date1 == None or date2 == None:
		return 0 if _type == 'int' else '0'
	else:
		delta = date2 - date1
		return delta.days if _type == 'int' else str(delta.days)


def GetWeeks(date1: date | str | None, date2: date | str | None, _type: Literal['int', 'str'] = 'int') -> int | str:
	if isinstance(date1, str):
		date1 = DateStrToDateObject(date1)
	if isinstance(date2, str):
		date2 = DateStrToDateObject(date2)
	if date1 == None or date2 == None:
		return 0 if _type == 'int' else '0'
	else:
		delta = date2 - date1
		return (delta.days // 7) if _type == 'int' else str(delta.days // 7)


def isfloat(num: str | None) -> bool:
	if num == None:
		return False
	try:
		float(num)
		return True
	except ValueError:
		return False


def isnum(num: str | None) -> bool:
	if num == None:
		return False
	try:
		int(num)
		return True
	except ValueError:
		return False


def clamp(n: str | None, min_value: int, max_value: int, default: int) -> int:
	if n == None or isnum(n) == False:
		return default
	else:
		return max(min(int(n), max_value), min_value)


def CheckEmailValidate(text: str | None) -> bool:
	if text is None:
		return False
	pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
	return re.match(pattern, text) is not None

def CheckPasswordValidate(text: str | None) -> bool:
	if text is None:
		return False
	pattern = r"^[A-Za-z0-9!@#$%^&*()\-_+=?.,]+$"
	return re.match(pattern, text) is not None


def CheckMACValidate(text: str | None) -> bool:
	if text == None:
		return False
	else:
		pattern = r'^(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})$'
		flag = re.match(pattern, text) != None  # Returns <re.Match object; ...> or None
		return flag


def CheckIPValidate(text: str | None) -> bool:
	if text == None:
		return False
	else:
		pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
		flag = re.match(pattern, text) != None  # Returns <re.Match object; ...> or None
		return flag


def CheckRequirementAddress(text: str | None) -> bool:
	"""
	 3x0	->	 3x00000
	 4x0	->	 4x00000
	50x0	->	50x00000
	51x0	->	51x00000
	52x0	->	52x00000
	53x0	->	53x00000
	54x0	->	54x00000
	"""
	if text == None:
		return False
	pattern = r'^[3-4]x[0-9]{1,5}$|^5[0-4]x[0-9]{1,5}$'
	flag = re.match(pattern, text) != None  # Returns <re.Match object; ...> or None
	return flag



def ToInt(num: str | int | float | None, default=0) -> int:
	if num is None:
		return default
	try:
		return int(num)
	except ValueError:
		return default


def ToFloat(num: str | float | None, default=0.0) -> float:
	if num is None:
		return default
	try:
		return float(num)
	except ValueError:
		return default


def isnumberic(num: str | None) -> bool:
	if num is None:
		return False
	return isfloat(num) or isnum(num)


def isnumbericlist(lst: list | None) -> bool:
	if lst is None:
		return False
	for num in lst:
		if isnumberic(num) == False:
			return False
	return True


def IsNumbericInDict(keys: list, dic: dict | None) -> bool:
	if dic is None:
		return False
	for key in keys:
		if key not in dic:
			return False
		if isnumberic(dic[key]) == False:
			return False
	return True

def GetModelMapping(model: str) -> type[models.Model] | None:
	model_mapping: dict[str, type[models.Model]] = {
		'0': ApiHome,
		'1': ApiParaSetTarget,
		'2': ApiParaSetFan,
		'3': ApiParaSetFanManual,
		'4': ApiParaSetTempTreatment,
		'5': ApiParaSetHumidTreatment,
		'6': ApiParaSetNh3Treatment,
		'7': ApiParaSetCo2Treatment,
		'8': ApiParaSetSpeedFan,
		'9': ApiParaSetSpeedFanSetup,
		'10': ApiParaSetCoolingPump,
		'11': ApiParaSetSpray,
		'12': ApiParaSetFanConfig,
		'13': ApiParaSetCoolingConfig,
		'14': ApiParaSetHeater,
		'15': ApiParaSetLight,
		'16': ApiParaSetFeed,
		'17': ApiParaSetAlarm,
		'18': ApiParaSetAirInletVent,
		'19': ApiParaSetAirInletSpeedFan,
		'20': ApiParaSetAirInletSetup,
		'21': ApiParaSetSystem,
		'22': ApiParaSetOutput,
	}
	return model_mapping.get(model, None)

def ValueToTimeStr(value: int) -> str:
	if value is None:
		return '00:00'
	hour = value // 60
	minute = value % 60
	return f'{hour:02d}:{minute:02d}'


def generateData(data: list[dict], houses: list[str] = []) -> list[dict]:
	uniqueHouses = list(set([e['house'] for e in data]))				# Get unique house values from data
	tofillhouse = [h for h in houses if h not in uniqueHouses]			# Houses that are not in uniqueHouses
	fillData = [{'house': f'{h}', 'data': []} for h in tofillhouse]		# Create fillData for missing houses
	newData = []
	for house in uniqueHouses:
		_data = {'house': house}
		arr = []
		datas = [e for e in data if e['house'] == house]				# Filter data for the current house
		for e in datas:
			e_copy = e.copy()
			del e_copy['house']
			arr.append(e_copy)
		_data['data'] = arr[::-1]										# Reverse the list
		newData.append(_data)
	newData.extend(fillData)											# Add fillData to newData
	newData.sort(key=lambda x: int(x['house']))
	return newData

def verify_captcha(token, remote_ip=None):
	response = requests.post(
		"https://challenges.cloudflare.com/turnstile/v0/siteverify",
		data={
			"secret": settings.TURNSTILE_SECRET_KEY,
			"response": token,
			"remoteip": remote_ip,
		},
		timeout=5,
	)
	result = response.json()

	if not result.get("success"):
		error_codes = result.get("error-codes", [])
		return False, f"verify ไม่ผ่าน: {', '.join(error_codes) or 'token ไม่ถูกต้อง'}"

	return True, None
# def verify_captcha(token, remote_ip=None):
#     response = requests.post(
#         "https://www.google.com/recaptcha/api/siteverify",
#         data={
#             "secret": settings.RECAPTCHA_SECRET_KEY,
#             "response": token,
#             "remoteip": remote_ip,
#         },
#         timeout=5,
#     )
#     result = response.json()

#     if not result.get("success"):
#         error_codes = result.get("error-codes", [])
#         return False, f"verify ไม่ผ่าน: {', '.join(error_codes) or 'token ไม่ถูกต้อง'}"

#     return True, None

