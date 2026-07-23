from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
import uuid
import pytz
from utilities import generate_otp

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
    CHICKATRON20N    = 'CKTRON-N', 'Chickatron 20 New'
    CHICKATRONLAYERS = 'CKTRON_L', 'Chickatron Layers'
    CHICKATRONBREEDERS= 'CKTRON_B', 'Chickatron Breeders'
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
    TP82 			 = 'TP82', 'TP82'
    PUNO207 		 = 'PUNOS207', 'Punos 207'
    PUNO515 		 = 'PUNOS515', 'Punos 515'
    SILONICX         = 'SILO-X', 'Silonic X'
    SILONICXI        = 'SILO-XI', 'Silonic XI'
    OTHER            = 'OTHER', 'Other'

class CloudType(models.TextChoices):
    SMARTLINK 	 = 'SMART_LINK', 'SmartLink'
    TEMPVIEW     = 'TEMP_VIEW', 'TempView'
    SILONICXI    = 'SILONIC', 'Silonic XI'

class ProfileFarm(models.Model):
    TIMEZONE_CHOICES = zip(pytz.all_timezones, pytz.all_timezones)
    nameFarm 	= models.CharField("Name Farm/ชื่อฟาร์มแบบย่อ", max_length=100, null=True, blank=True)
    numbOfHouse = models.CharField("Number of House/จำนวนโรงเรือน", max_length=10, default='1')
    cloudType   = models.CharField("ประเภทในการขึ้นอิเทอร์เน็ต", max_length=20, choices=CloudType.choices, default=CloudType.SMARTLINK)
    modelTemp   = models.CharField("รุ่นเครื่อง", max_length=20, choices=ModelControllerChoices.choices, default=ModelControllerChoices.CHICKATRON20)
    ip_address  = models.CharField("หมายเลข IP Controller", max_length=100, default='68.183.231.70:8001')
    ip_manage   = models.CharField("หมายเลข IP Management", max_length=100, default='152.42.174.114:8000')
    ws_address  = models.CharField('WebSocket Address', max_length=100, null=True, blank=True)
    companyName = models.CharField("Company Name/ชื่อฟาร์ม", max_length=100, null=True, blank=True)
    address1    = models.CharField("Address Line1/ที่อยู่1", max_length=100, null=True, blank=True)
    address2    = models.CharField("Address Line1/ที่อยู่", max_length=100, null=True, blank=True)
    townCity    = models.CharField("Town/City/อำเภอ/เขต", max_length=50, null=True, blank=True)
    province    = models.CharField("Province/จังหวัด", max_length=50, null=True, blank=True)
    country	    = models.CharField("Country/ประเทศ", max_length=50, choices=ModelCountryChoices.choices, default=ModelCountryChoices.TH)
    postcode    = models.CharField("Postcode/รหัสไปรษณีย์", max_length=50, null=True, blank=True)
    contact		= models.CharField("Contact Person/ผู้ติดต่อ", max_length=50, null=True, blank=True)
    mobile 		= models.CharField("Phone/เบอร์โทรศัพท์", max_length=50, null=True, blank=True)
    emailFarm   = models.EmailField("Email/อีเมล", max_length=50, null=True, blank=True)
    timezone    = models.CharField("Time Zone",max_length=50, choices=TIMEZONE_CHOICES, default='Asia/Bangkok')
    date_created = models.DateTimeField(auto_now_add=True)
    token       = models.CharField("Access Token", max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.nameFarm} | {self.modelTemp}'

class ProfileUser(models.Model):
    username        = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name      = models.CharField(max_length=50, null=True, blank=True)
    last_name       = models.CharField(max_length=50, null=True, blank=True)
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

class ProfileUserApp(models.Model):
    USER            = 'User'
    SUPERUSER       = 'Superuser'
    USER_CHOICES    = [(USER,'User'),(SUPERUSER,'Superuser'),]
    nameFarm        = models.ForeignKey(ProfileFarm, on_delete=models.CASCADE, verbose_name='ชื่อฟาร์มแบบย่อ')
    username        = models.CharField("Username/ชื่อผู้ใช้งาน", max_length=50, null=True, blank=True)
    userType        = models.CharField("User type/ระดับของผู้ใช้", max_length=20, choices=USER_CHOICES, default=USER)
    userEmail       = models.EmailField("Email/อีเมล", max_length=50, null=True, blank=True)
    date_created    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username.username

class ProfileSmartLink(models.Model):
    nameFarm		= models.ForeignKey(ProfileFarm, on_delete=models.CASCADE, verbose_name='ชื่อฟาร์มแบบย่อ')
    house           = models.CharField('หมายเลขโรงเรื่อง', max_length=10, blank=False, default='1')
    serialNumber    = models.CharField('รหัสเครื่อง', max_length=50, blank=False, null=False)
    # alarm04         = models.BooleanField('ALARM04', default=False)
    # alarm05         = models.BooleanField('ALARM05', default=False) 
    # aimc            = models.BooleanField('AIMC-2', default=False)
    # dim             = models.BooleanField('DIM-T', default=False)
    # tunnelInlet     = models.BooleanField('Tunnel Door Air Inlet', default=False)
    # sideInlet     = models.BooleanField('Side Wall Air Inlet', default=False)

    def __str__(self):
        return f'{self.nameFarm}'

class ProfileSilonic(models.Model):
    nameFarm		= models.ForeignKey(ProfileFarm, on_delete=models.CASCADE, verbose_name='ชื่อฟาร์มแบบย่อ')
    house           = models.CharField('หมายเลขโรงเรื่อง', max_length=10, blank=False, default='1')
    serialNumber    = models.CharField('รหัสเครื่อง', max_length=50, blank=False, null=False)

    def __str__(self):
        return f'{self.nameFarm}'
    
class ProfileTempView(models.Model):
    nameFarm		= models.ForeignKey(ProfileFarm, on_delete=models.CASCADE, verbose_name='ชื่อฟาร์มแบบย่อ')
    house           = models.CharField('หมายเลขโรงเรื่อง', max_length=10, blank=False, default='1')

    def __str__(self):
        return f'{self.nameFarm}'

class OTP(models.Model):
    email           = models.EmailField('Email', max_length=10, blank=False, null=False)
    otpNumber       = models.CharField('OTP', max_length=6, default=generate_otp)
    date_created    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email}' f'{self.otpNumber}'