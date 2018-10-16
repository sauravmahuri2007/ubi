# A list of item types which can be purchased
CANBEPURCHASED = [
    'PURCHASE_POINTS',
    'PURCHASE_ITEMS'
]

TRANS_SUCCESS_STATUS = 'SUCCESS'

EXCEPTION_STR = {
    'INSUFFICIENTPOINTS': 'Insufficient Points',
    'CANTPURCHASE': 'Selected Item Can Not Be Purchased'
}

ENABLE_FREE_POINT_SYSTEM = True  # Global setting to turn ON/OFF the free point system
FREE_POINTS_ELIGIBILITY = 3 * 60  # 3 hours in minutes
MAX_FREE_POINTS_ALLOWED = 200  # The maximum points limit can be given as free
FREE_ITEM_TYPE = 'FREE_POINTS'  # Make sure to create one and only one item of this type which can be given as free
FREE_ITEM_POINTS_VALUE = 50  # The points which will be given for free for one transaction when eligible

UBI_BASIC_AUTH = {
    'username': 'UBI_BASIC_USER',
    'password': 'UBI_BASIC_AUTH'
}

JWT_EXPIRY_TIME = 60 * 60 * 24  # 24 Hours in seconds
JWT_SECRET = 'N3v3RExp0s^T[-]IsSecret'
JWT_ALGORITHM = 'HS256'