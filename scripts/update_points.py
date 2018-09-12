"""
A python script which is responsible for updating the user's free points.
This can also be schedule to run as a cron job
"""

import multiprocessing
import os
import sys

# append the project's base directory to system path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ubi.settings')

import django

django.setup()

from config import ubiconf
from points.models import User, Transaction, Item
from utils.ubiutils import next_eligible_datetime

from django.db import connections, transaction, models
from django.utils.timezone import now

connections.close_all()


def update_free_points(users, item):
    for user in users:
        Transaction.objects.create(userid=user, itemid=item, status=ubiconf.TRANS_SUCCESS_STATUS)
        if user.free_points + item.points > ubiconf.MAX_FREE_POINTS_ALLOWED:
            user.free_points = ubiconf.MAX_FREE_POINTS_ALLOWED
        else:
            user.free_points += item.points
        user.free_points_eligible_dtm = next_eligible_datetime()
        user.save()


def update_users():
    try:
        free_item = Item.objects.get(type=ubiconf.FREE_ITEM_TYPE, points=ubiconf.FREE_ITEM_POINTS_VALUE)
    except models.ObjectDoesNotExist:
        return 'Free Item Not Found! Make sure there exists only one Item of Type = "{0}" having points = {1}'.format(
            ubiconf.FREE_ITEM_TYPE, ubiconf.FREE_ITEM_POINTS_VALUE
        )
    else:
        return 'Something went wrong! Make sure there exists only one Item of Type = "{0}" having points = {1}'.format(
            ubiconf.FREE_ITEM_TYPE, ubiconf.FREE_ITEM_POINTS_VALUE
        )
    eligible_users = User.objects.filter(
        free_points__lt=ubiconf.MAX_FREE_POINTS_ALLOWED,
        free_points_eligible_dtm__lte=now())
    if eligible_users:
        ln = len(eligible_users)
        # diving the queryset into 4 chunks to enable parallelism.
        list_of_chunks = [eligible_users[(x * ln) // 4:((x + 1) * ln) // 4] for x in range(4)]
        pool = multiprocessing.Pool(processes=4)
        [pool.apply_async(update_free_points, [chunk, free_item]) for chunk in list_of_chunks]
        pool.close()
        pool.join()
        return '{0} users have been successfully awarded with free points'.format(ln)
    return 'No users are eligible for free points'


if __name__ == '__main__':
    if ubiconf.ENABLE_FREE_POINT_SYSTEM:
        print(update_users())
    else:
        print('Free Point System is disabled!')


