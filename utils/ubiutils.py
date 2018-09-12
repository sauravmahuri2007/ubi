from django.utils.timezone import now

from config.ubiconf import FREE_POINTS_ELIGIBILITY
from datetime import timedelta


def next_eligible_datetime():
    """
    Calculate a datetime which is current datetime + FREE_POINTS_ELIGIBILITY minutes
    :return: datetime object
    """
    next_eligible_dtm = now() + timedelta(minutes=FREE_POINTS_ELIGIBILITY)
    return next_eligible_dtm

