from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
import uuid
import pytz
from datetime import timedelta
from django.utils import timezone
import random
import secrets
import string
from django.conf import settings
from django.core.exceptions import ValidationError

class ModelCountryChoices(models.TextChoices):
    AF = 'Afghanistan', 'Afghanistan'
    AX = 'Åland Islands', 'Åland Islands'
    AL = 'Albania', 'Albania'
    DZ = 'Algeria', 'Algeria'
    AS = 'American Samoa', 'American Samoa'
    AD = 'AndorrA', 'AndorrA'
    AO = 'Angola', 'Angola'
    AI = 'Anguilla', 'Anguilla'
    AQ = 'Antarctica', 'Antarctica'
    AG = 'Antigua and Barbuda', 'Antigua and Barbuda'
    AR = 'Argentina', 'Argentina'
    AM = 'Armenia', 'Armenia'
    AW = 'Aruba', 'Aruba'
    AU = 'Australia', 'Australia'
    AT = 'Austria', 'Austria'
    AZ = 'Azerbaijan', 'Azerbaijan'
    BS = 'Bahamas', 'Bahamas'
    BH = 'Bahrain', 'Bahrain'
    BD = 'Bangladesh', 'Bangladesh'
    BB = 'Barbados', 'Barbados'
    BY = 'Belarus', 'Belarus'
    BE = 'Belgium', 'Belgium'
    BZ = 'Belize', 'Belize'
    BJ = 'Benin', 'Benin'
    BM = 'Bermuda', 'Bermuda'
    BT = 'Bhutan', 'Bhutan'
    BO = 'Bolivia', 'Bolivia'
    BA = 'Bosnia and Herzegovina', 'Bosnia and Herzegovina'
    BW = 'Botswana', 'Botswana'
    BV = 'Bouvet Island', 'Bouvet Island'
    BR = 'Brazil', 'Brazil'
    IO = 'British Indian Ocean Territory', 'British Indian Ocean Territory'
    BN = 'Brunei Darussalam', 'Brunei Darussalam'
    BG = 'Bulgaria', 'Bulgaria'
    BF = 'Burkina Faso', 'Burkina Faso'
    BI = 'Burundi', 'Burundi'
    KH = 'Cambodia', 'Cambodia'
    CM = 'Cameroon', 'Cameroon'
    CA = 'Canada', 'Canada'
    CV = 'Cape Verde', 'Cape Verde'
    KY = 'Cayman Islands', 'Cayman Islands'
    CF = 'Central African Republic', 'Central African Republic'
    TD = 'Chad', 'Chad'
    CL = 'Chile','Chile'
    CN = 'China', 'China'
    CX = 'Christmas Island', 'Christmas Island'
    CC = 'Cocos (Keeling) Islands', 'Cocos (Keeling) Islands',
    CO = 'Colombia', 'Colombia'
    KM = 'Comoros', 'Comoros'
    CG = 'Congo', 'Congo'
    CD = 'Congo, The Democratic Republic of the', 'Congo, The Democratic Republic of the'
    CK = 'Cook Islands', 'Cook Islands'
    CR = 'Costa Rica', 'Costa Rica'
    CI = 'Cote D\'Ivoire', 'Cote D\'Ivoire'
    HR = 'Croatia', 'Croatia'
    CU = 'Cuba', 'Cuba'
    CY = 'Cyprus', 'Cyprus'
    CZ = 'Czech Republic', 'Czech Republic'
    DK = 'Denmark', 'Denmark'
    DJ = 'Djibouti', 'Djibouti'
    DM = 'Dominica', 'Dominica'
    DO = 'Dominican Republic', 'Dominican Republic'
    EC = 'Ecuador', 'Ecuador'
    EG = 'Egypt', 'Egypt'
    SV = 'El Salvador', 'El Salvador'
    GQ = 'Equatorial Guinea', 'Equatorial Guinea'
    ER = 'Eritrea', 'Eritrea'
    EE = 'Estonia', 'Estonia'
    ET = 'Ethiopia', 'Ethiopia'
    FK = 'Falkland Islands (Malvinas)', 'Falkland Islands (Malvinas)'
    FO = 'Faroe Islands', 'Faroe Islands'
    FJ = 'Fiji', 'Fiji'
    FI = 'Finland', 'Finland'
    FR = 'France', 'France'
    GF = 'French Guiana', 'French Guiana'
    PF = 'French Polynesia', 'French Polynesia'
    TF = 'French Southern Territories', 'French Southern Territories'
    GA = 'Gabon', 'Gabon'
    GM = 'Gambia', 'Gambia'
    GE = 'Georgia', 'Georgia'
    DE = 'Germany', 'Germany'
    GH = 'Ghana', 'Ghana'
    GI = 'Gibraltar', 'Gibraltar'
    GR = 'Greece', 'Greece'
    GL = 'Greenland', 'Greenland'
    GD = 'Grenada', 'Grenada'
    GP = 'Guadeloupe', 'Guadeloupe'
    GU = 'Guam', 'Guam'
    GT = 'Guatemala', 'Guatemala'
    GG = 'Guernsey', 'Guernsey'
    GN = 'Guinea', 'Guinea'
    GW = 'Guinea-Bissau', 'Guinea-Bissau'
    GY = 'Guyana', 'Guyana'
    HT = 'Haiti', 'Haiti'
    HM = 'Heard Island and Mcdonald Islands', 'Heard Island and Mcdonald Islands'
    VA = 'Holy See (Vatican City State)', 'Holy See (Vatican City State)'
    HN = 'Honduras', 'Honduras'
    HK = 'Hong Kong', 'Hong Kong'
    HU = 'Hungary', 'Hungary'
    IS = 'Iceland', 'Iceland'
    IN = 'India', 'India'
    ID = 'Indonesia', 'Indonesia'
    IR = 'Iran, Islamic Republic Of', 'Iran, Islamic Republic Of'
    IQ = 'Iraq', 'Iraq'
    IE = 'Ireland', 'Ireland'
    IM = 'Isle of Man', 'Isle of Man'
    IL = 'Israel', 'Israel'
    IT = 'Italy', 'Italy'
    JM = 'Jamaica', 'Jamaica'
    JP = 'Japan', 'Japan'
    JE = 'Jersey', 'Jersey'
    JO = 'Jordan', 'Jordan'
    KZ = 'Kazakhstan', 'Kazakhstan'
    KE = 'Kenya', 'Kenya'
    KI = 'Kiribati', 'Kiribati'
    KP = 'Korea, Democratic People\'S Republic of', 'Korea, Democratic People\'S Republic of'
    KR = 'Korea, Republic of', 'Korea, Republic of'
    KW = 'Kuwait', 'Kuwait'
    KG = 'Kyrgyzstan', 'Kyrgyzstan'
    LA = 'Lao People\'S Democratic Republic', 'Lao People\'S Democratic Republic'
    LV = 'Latvia', 'Latvia'
    LB = 'Lebanon', 'Lebanon'
    LS = 'Lesotho', 'Lesotho'
    LR = 'Liberia', 'Liberia'
    LY = 'Libyan Arab Jamahiriya', 'Libyan Arab Jamahiriya'
    LI = 'Liechtenstein',  'Liechtenstein'
    LT = 'Lithuania', 'Lithuania'
    LU = 'Luxembourg', 'Luxembourg'
    MO = 'Macao', 'Macao'
    MK = 'Macedonia, The Former Yugoslav Republic of', 'Macedonia, The Former Yugoslav Republic of'
    MG = 'Madagascar', 'Madagascar'
    MW = 'Malawi', 'Malawi'
    MY = 'Malaysia', 'Malaysia'
    MV = 'Maldives', 'Maldives'
    ML = 'Mali', 'Mali'
    MT = 'Malta', 'Malta'
    MH = 'Marshall Islands', 'Marshall Islands'
    MQ = 'Martinique', 'Martinique'
    MR = 'Mauritania', 'Mauritania'
    MU = 'Mauritius', 'Mauritius'
    YT = 'Mayotte', 'Mayotte'
    MX = 'Mexico', 'Mexico'
    FM = 'Micronesia, Federated States of', 'Micronesia, Federated States of'
    MD = 'Moldova, Republic of', 'Moldova, Republic of'
    MC = 'Monaco', 'Monaco'
    MN = 'Mongolia', 'Mongolia'
    MS = 'Montserrat', 'Montserrat'
    MA = 'Morocco', 'Morocco'
    MZ = 'Mozambique', 'Mozambique'
    MM = 'Myanmar', 'Myanmar'
    NA = 'Namibia', 'Namibia'
    NR = 'Nauru', 'Nauru'
    NP = 'Nepal', 'Nepal'
    NL = 'Netherlands', 'Netherlands'
    AN = 'Netherlands Antilles', 'Netherlands Antilles'
    NC = 'New Caledonia', 'New Caledonia'
    NZ = 'New Zealand', 'New Zealand'
    NI = 'Nicaragua', 'Nicaragua'
    NE = 'Niger', 'Niger'
    NG = 'Nigeria', 'Nigeria'
    NU = 'Niue', 'Niue'
    NF = 'Norfolk Island', 'Norfolk Island'
    MP = 'Northern Mariana Islands', 'Northern Mariana Islands'
    NO = 'Norway', 'Norway'
    OM = 'Oman', 'Oman'
    PK = 'Pakistan', 'Pakistan'
    PW = 'Palau', 'Palau'
    PS = 'Palestinian Territory, Occupied', 'Palestinian Territory, Occupied'
    PA = 'Panama', 'Panama'
    PG = 'Papua New Guinea', 'Papua New Guinea'
    PY = 'Paraguay', 'Paraguay'
    PE = 'Peru', 'Peru'
    PH = 'Philippines', 'Philippines'
    PN = 'Pitcairn', 'Pitcairn'
    PL = 'Poland', 'Poland'
    PT = 'Portugal', 'Portugal'
    PR = 'Puerto Rico', 'Puerto Rico'
    QA = 'Qatar', 'Qatar'
    RE = 'Reunion', 'Reunion'
    RO = 'Romania', 'Romania'
    RU = 'Russian Federation', 'Russian Federation'
    RW = 'RWANDA', 'RWANDA'
    SH = 'Saint Helena', 'Saint Helena'
    KN = 'Saint Kitts and Nevis', 'Saint Kitts and Nevis'
    LC = 'Saint Lucia', 'Saint Lucia'
    PM = 'Saint Pierre and Miquelon', 'Saint Pierre and Miquelon'
    VC = 'Saint Vincent and the Grenadines', 'Saint Vincent and the Grenadines'
    WS = 'Samoa', 'Samoa'
    SM = 'San Marino', 'San Marino'
    ST = 'Sao Tome and Principe', 'Sao Tome and Principe'
    SA = 'Saudi Arabia', 'Saudi Arabia'
    SN = 'Senegal', 'Senegal'
    CS = 'Serbia and Montenegro', 'Serbia and Montenegro'
    SC = 'Seychelles', 'Seychelles'
    SL = 'Sierra Leone', 'Sierra Leone'
    SG = 'Singapore', 'Singapore'
    SK = 'Slovakia', 'Slovakia'
    SI = 'Slovenia', 'Slovenia'
    SB = 'Solomon Islands', 'Solomon Islands'
    SO = 'Somalia', 'Somalia'
    ZA = 'South Africa', 'South Africa'
    GS = 'South Georgia and the South Sandwich Islands', 'South Georgia and the South Sandwich Islands'
    ES = 'Spain', 'Spain'
    LK = 'Sri Lanka', 'Sri Lanka'
    SD = 'Sudan', 'Sudan'
    SR = 'Suriname', 'Suriname'
    SJ = 'Svalbard and Jan Mayen', 'Svalbard and Jan Mayen'
    SZ = 'Swaziland', 'Swaziland'
    SE = 'Sweden', 'Sweden'
    CH = 'Switzerland', 'Switzerland'
    SY = 'Syrian Arab Republic', 'Syrian Arab Republic'
    TW = 'Taiwan, Province of China', 'Taiwan, Province of China'
    TJ = 'Tajikistan', 'Tajikistan'
    TZ = 'Tanzania, United Republic of', 'Tanzania, United Republic of'
    TH = 'Thailand', 'Thailand'
    TL = 'Timor-Leste', 'Timor-Leste'
    TG = 'Togo', 'Togo'
    TK = 'Tokelau', 'Tokelau'
    TO = 'Tonga', 'Tonga'
    TT = 'Trinidad and Tobago', 'Trinidad and Tobago'
    TN = 'Tunisia', 'Tunisia'
    TR = 'Turkey', 'Turkey'
    TM = 'Turkmenistan', 'Turkmenistan'
    TC = 'Turks and Caicos Islands', 'Turks and Caicos Islands'
    TV = 'Tuvalu', 'Tuvalu'
    UG = 'Uganda', 'Uganda'
    UA = 'Ukraine', 'Ukraine'
    AE = 'United Arab Emirates', 'United Arab Emirates'
    GB = 'United Kingdom', 'United Kingdom'
    US = 'United States', 'United States'
    UM = 'United States Minor Outlying Islands', 'United States Minor Outlying Islands'
    UY = 'Uruguay', 'Uruguay'
    UZ = 'Uzbekistan', 'Uzbekistan'
    VU = 'Vanuatu', 'Vanuatu'
    VE = 'Venezuela', 'Venezuela'
    VN = 'Viet Nam', 'Viet Nam'
    VG = 'Virgin Islands, British', 'Virgin Islands, British'
    VI = 'Virgin Islands, U.S.', 'Virgin Islands, U.S.'
    WF = 'Wallis and Futuna', 'Wallis and Futuna'
    EH = 'Western Sahara', 'Western Sahara'
    YE = 'Yemen', 'Yemen'
    ZM = 'Zambia', 'Zambia'
    ZW = 'Zimbabwe', 'Zimbabwe'
    
class ModelControllerChoices(models.TextChoices):
    CHICKATRON20 	 = 'CKTRON20', 'Chickatron 20'
    CHICKATRONLAYERS = 'CKLAYERS', 'Chickatron Layers'
    CHICKATRON13	 = 'CKTRON13', 'Chickatron 13'
    PIGATRON13		 = 'PIG13', 'Pigatron 13'
    T1200P		 	 = 'T1200+', 'Temp1200 Plus'
    RTRON 			 = 'T2004-PK', 'R-Tron'
    RTRON207		 = 'RTROn207', 'R-Tron 207'
    RTRON313		 = 'RTROn313', 'R-Tron 313'
    RTRON612		 = 'RTRON612', 'R-Tron 612'
    RTRON612P		 = 'RT612P', 'R-Tron 612 Pig'
    RTRON620		 = 'RTRON620', 'R-Tron 620'
    PTRON620P		 = 'RT620P', 'R-Tron 620 Pig'
    TP54S 			 = 'TP54S', 'TP54S'
    TP80 			 = 'TP80', 'TP80'
    PUNO207 		 = 'PUNOS207', 'Punos 207'
    PUNO515 		 = 'PUNOS515', 'Punos 515'
    SILONIC_XI       = 'SILO-XI', 'SILONIC-XI'
    EGG_C12          = 'EGG-C12', 'EGG-C12'
    OTHER            = 'OTHER', 'OTHER'

class ModelAlarmChoices(models.TextChoices):
    ALARM04          = 'ALARM-04', 'Alarm-04'
    ALARM05          = 'ALARM-05', 'Alarm-05'

class ModelEggChoices(models.TextChoices):
    EGGAI1          = 'EGG-AI1', 'Egg-Ai1'
    EGGC12          = 'EGG-C12', 'Egg-C12'

class ModelSilonicChoices(models.TextChoices):
    SILOXI          = 'SILONIC-XI', 'Silonic-Xi'
    SILOX           = 'SILONIC-X', 'Silonic-X'

class StatusChoices(models.TextChoices):
    PENDING          = 'PENDING', 'Pending'
    REJECT           = 'REJECT', 'Reject'
    APPROVE          = 'APPROVE', 'Approve'
    EDIT             = 'EDIT', 'Edit'

class TypeChoices(models.TextChoices):
    SMARTLINK        = 'SMARTLINK', 'SmartLink'
    TEMPVIEW         = 'TEMPVIEW', 'TempView/FarmNet'

class EquipmentCategory(models.TextChoices):
    CONTROLLER      = 'CONTROLLER', 'Controller'
    ALARM           = 'ALARM', 'Alarm'
    EGG             = 'EGG', 'Egg'
    SILONIC         = 'SILONIC', 'Silonic'


class EquipmentModel(models.Model):
    category     = models.CharField("ประเภทเครื่อง", max_length=20, choices=EquipmentCategory.choices, db_index=True)
    code         = models.CharField("รหัสรุ่น", max_length=50)
    name         = models.CharField("ชื่อรุ่น", max_length=100)

    class Meta:
        db_table = "equipment_model"
        constraints = [models.UniqueConstraint(fields=["category", "code"], name="uniq_equipment_category_code")]
        ordering = ["category", "name"]

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"


class ModelIpAddress(models.Model):
    model = models.ForeignKey( EquipmentModel, on_delete=models.CASCADE, verbose_name='Model/รุ่น')
    ipAddress = models.CharField("หมายเลข IP Controller", max_length=100)

    def __str__(self):
        return self.ipAddress

class EquipmentCategoryGuardMixin:
    equipment_field = "equipmentModel"   # override ใน subclass ถ้าชื่อ field ต่างกัน
    expected_category = None

    def clean(self):
        model_instance = getattr(self, self.equipment_field, None)
        if model_instance and model_instance.category != self.expected_category:
            raise ValidationError({self.equipment_field: f"ต้องเลือกรุ่นเครื่องประเภท {self.expected_category} เท่านั้น"})

class RefreshToken(models.Model):
    jti             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='refresh_tokens')
    created_at      = models.DateTimeField(auto_now_add=True)
    expires_at      = models.DateTimeField()
    revoked         = models.BooleanField(default=False)

    def is_valid(self):
        return not self.revoked and self.expires_at > timezone.now()


def generate_key():
    chars = string.ascii_letters + string.digits
    while True:
        key = "".join(secrets.choice(chars) for _ in range(20))
        if not AccessKey.objects.filter(key=key).exists():
            return key
def key_expire():
    return timezone.now() + timedelta(days=1)

class AccessKey(models.Model):
    user            = models.CharField("User", max_length=50, blank=True, null=True)
    sale            = models.CharField("Sale", max_length=50, blank=True, null=True)
    key             = models.CharField("AccessKey", max_length=20, unique=True, default=generate_key)
    is_used         = models.BooleanField(default=False)
    created_at      = models.DateTimeField("Create Date", auto_now_add=True)
    used_at         = models.DateTimeField("Used Date", blank=True, null=True)
    expired_at      = models.DateTimeField("Expire Date", default=key_expire)

    class Meta:
        db_table = "access_keys"

    def __str__(self):
        return self.key


class ProfileUser(models.Model):
    username        = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name      = models.CharField(max_length=50, null=True, blank=True)
    last_name       = models.CharField(max_length=50, null=True, blank=True)
    country	        = models.CharField("Country/ประเทศ", max_length=50, choices=ModelCountryChoices.choices, default=ModelCountryChoices.TH)
    mobile 		    = models.CharField("Phone/เบอร์โทรศัพท์", max_length=50, null=True, blank=True)
    token           = models.UUIDField("Access Token", max_length=100, default=uuid.uuid1)
    date_created    = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.username:
            self.first_name = self.username.first_name
            self.last_name = self.username.last_name
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_created']
        db_table = 'ProfileUser'

    def __str__(self):
        return self.username.username


class ProfileFarm(models.Model):
    TIMEZONE_CHOICES = zip(pytz.all_timezones, pytz.all_timezones)
    status          = models.CharField("Status/สถานะ", max_length=50, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    nameFarm 	    = models.CharField("Name Farm/ชื่อฟาร์มแบบย่อ", max_length=100, unique=True)
    numbOfHouse     = models.CharField("Number of House/จำนวนโรงเรือน", max_length=10, default='1')
    ip_address      = models.CharField("หมายเลข IP Controller", max_length=100, default='159.65.6.83:8001')
    ip_manage       = models.CharField("หมายเลข IP Management", max_length=100, default='152.42.174.114:8000')
    companyName     = models.CharField("Company Name/ชื่อฟาร์ม", max_length=100, null=True, blank=True)
    address1        = models.CharField("Address Line1/ที่อยู่1", max_length=100, null=True, blank=True)
    address2        = models.CharField("Address Line2/ที่อยู่2", max_length=100, null=True, blank=True)
    townCity        = models.CharField("Town/City/อำเภอ/เขต", max_length=50, null=True, blank=True)
    province        = models.CharField("Province/จังหวัด", max_length=50, null=True, blank=True)
    country	        = models.CharField("Country/ประเทศ", max_length=50, choices=ModelCountryChoices.choices, default=ModelCountryChoices.TH)
    postcode        = models.CharField("Postcode/รหัสไปรษณีย์", max_length=50, null=True, blank=True)
    contact         = models.CharField("Contact Person/ผู้ติดต่อ", max_length=50, null=True, blank=True)
    mobile          = models.CharField("Phone/เบอร์โทรศัพท์", max_length=50, null=True, blank=True)
    emailFarm       = models.EmailField("Email/อีเมล", max_length=50, null=True, blank=True)
    saleName        = models.CharField("Sale Name/ชื่อตัวแทนจำหน่าย", max_length=50, null=True, blank=True)
    saleContract    = models.JSONField("Sale Contract/ช่องทางติดต่อตัวแทนจำหน่าย", null=True, blank=True)
    poNumber        = models.CharField("PO Number/หมายเลขใบสั่งซื้อ", max_length=50, null=True, blank=True)
    timezone        = models.CharField("Time Zone", max_length=50, choices=TIMEZONE_CHOICES, default='Asia/Bangkok')
    date_created    = models.DateTimeField(auto_now_add=True)
    date_edit       = models.DateTimeField("Edit time", null=True, blank=True)
    user            = models.ForeignKey(ProfileUser, on_delete=models.CASCADE, related_name="farms", verbose_name="เจ้าของฟาร์ม")
    note            = models.CharField("Note/หมายเหตุ", max_length=500, null=True, blank=True)

    def __str__(self):
        return f'{self.nameFarm}'


class ProfileUserApp(EquipmentCategoryGuardMixin, models.Model):
    equipment_field   = "deviceModel"
    expected_category = EquipmentCategory.CONTROLLER

    USER            = 'User'
    SUPERUSER       = 'Superuser'
    USER_CHOICES    = [(USER,'User'),(SUPERUSER,'Superuser'),]
    nameFarm        = models.ForeignKey(ProfileFarm, on_delete=models.CASCADE, related_name="userapps", verbose_name='ชื่อฟาร์มแบบย่อ')
    deviceModel     = models.ForeignKey(EquipmentModel, on_delete=models.PROTECT, related_name="userapps", limit_choices_to={"category": EquipmentCategory.CONTROLLER}, verbose_name='รุ่นเครื่อง')
    username        = models.CharField("Username/ชื่อผู้ใช้งาน", max_length=50, unique=True)
    userType        = models.CharField("User type/ระดับของผู้ใช้", max_length=20, choices=USER_CHOICES, default=USER)
    userEmail       = models.EmailField("Email/อีเมล", max_length=50, null=True, blank=True)
    date_created    = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nameFarm}'

class ProfileDevice(EquipmentCategoryGuardMixin, models.Model):
    equipment_field   = "modelTemp"
    expected_category = EquipmentCategory.CONTROLLER

    type          = models.CharField("ประเภทการเชื่อมต่อ", max_length=20, choices=TypeChoices, default=TypeChoices.SMARTLINK)
    modelTemp     = models.ForeignKey(EquipmentModel, on_delete=models.PROTECT, related_name="devices",limit_choices_to={"category": EquipmentCategory.CONTROLLER},verbose_name='รุ่นเครื่อง')
    nameFarm      = models.ForeignKey('ProfileFarm', on_delete=models.CASCADE, related_name="devices", verbose_name='ชื่อฟาร์มแบบย่อ')
    house         = models.CharField('หมายเลขโรงเรือน', max_length=10, blank=False, default='1')
    controllerSN  = models.CharField('รหัสคอนโทรลเลอร์', max_length=50, blank=True, null=True, unique=True)
    smartlinkSN   = models.CharField('รหัสสมาร์ทลิงค์', max_length=50, blank=True, null=True, unique=True)

    class Meta:
        ordering = ["modelTemp__name"]
        constraints = [
            models.UniqueConstraint(fields=["nameFarm", "house"], name="uniq_device_per_farm_house"),
        ]

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nameFarm}'


class ProfileAlarm(EquipmentCategoryGuardMixin, models.Model):
    equipment_field   = "modelAlarm"
    expected_category = EquipmentCategory.ALARM

    type          = models.CharField("ประเภทการเชื่อมต่อ", max_length=20, choices=TypeChoices, default=TypeChoices.SMARTLINK)
    modelAlarm    = models.ForeignKey(EquipmentModel, on_delete=models.PROTECT, related_name="alarms", limit_choices_to={"category": EquipmentCategory.ALARM}, verbose_name='รุ่นเครื่อง')
    nameFarm      = models.ForeignKey('ProfileFarm', on_delete=models.CASCADE, related_name="alarms", verbose_name='ชื่อฟาร์มแบบย่อ')
    house         = models.CharField('หมายเลขโรงเรือน', max_length=10, blank=False, default='1')
    serialNumber  = models.CharField('รหัสเครื่อง', max_length=50, blank=True, null=True, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["nameFarm", "house"], name="uniq_alarm_per_farm_house"),
        ]

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nameFarm}'


class ProfileEgg(EquipmentCategoryGuardMixin, models.Model):
    equipment_field   = "modelEgg"
    expected_category = EquipmentCategory.EGG

    type          = models.CharField("ประเภทการเชื่อมต่อ", max_length=20, choices=TypeChoices, default=TypeChoices.SMARTLINK)
    modelEgg      = models.ForeignKey(EquipmentModel, on_delete=models.PROTECT, related_name="eggs", limit_choices_to={"category": EquipmentCategory.EGG}, verbose_name='รุ่นเครื่อง')
    nameFarm      = models.ForeignKey('ProfileFarm', on_delete=models.CASCADE, related_name="eggs", verbose_name='ชื่อฟาร์มแบบย่อ')
    house         = models.CharField('หมายเลขโรงเรือน', max_length=10, blank=False, default='1')
    serialNumber  = models.CharField('รหัสเครื่อง', max_length=50, blank=True, null=True, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["nameFarm", "house"], name="uniq_egg_per_farm_house"),
        ]

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nameFarm}'


class ProfileSilonic(EquipmentCategoryGuardMixin, models.Model):
    equipment_field   = "modelSilonic"
    expected_category = EquipmentCategory.SILONIC

    type          = models.CharField("ประเภทการเชื่อมต่อ", max_length=20, choices=TypeChoices, default=TypeChoices.SMARTLINK)
    modelSilonic  = models.ForeignKey( EquipmentModel, on_delete=models.PROTECT, related_name="silonics", limit_choices_to={"category": EquipmentCategory.SILONIC}, verbose_name='รุ่นเครื่อง')
    nameFarm      = models.ForeignKey('ProfileFarm', on_delete=models.CASCADE, related_name="silonics", verbose_name='ชื่อฟาร์มแบบย่อ')
    house         = models.CharField('หมายเลขโรงเรือน', max_length=10, blank=False, default='1')
    serialNumber  = models.CharField('รหัสเครื่อง', max_length=50, blank=True, null=True, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["nameFarm", "house"], name="uniq_silonic_per_farm_house"),
        ]

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)       

    def __str__(self):
        return f'{self.nameFarm}'


def generate_otp_code():
    return f"{random.randint(0, 999999):06d}"
def default_expiry_at():
    return timezone.now() + timedelta(minutes=3)
def default_resend_at():
    return timezone.now() + timedelta(seconds=30)
def default_delete_at():
    return timezone.now() + timedelta(minutes=5)


class OTP(models.Model):
    email           = models.CharField('Email', max_length=100)
    code            = models.CharField('OTP', max_length=6, default=generate_otp_code)
    attempt_count   = models.PositiveSmallIntegerField(default=0)
    expires_at      = models.DateTimeField('Expires At', default=default_expiry_at)
    resend_at       = models.DateTimeField('Resend At', default=default_resend_at)
    delete_at       = models.DateTimeField('Delete At', default=default_delete_at)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"OTP for {self.email} - Expires at: {self.expires_at}"
