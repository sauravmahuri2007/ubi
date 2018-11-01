from datetime import timedelta

from .models import User, Item, Transaction
from config import ubiconf
from ubiexceptions.generic import InsufficientPoints, CanNotBePurchased
from utils.ubiutils import next_eligible_datetime

from django.apps import AppConfig
from django.db import transaction, models
from django.utils.timezone import now


class PointsConfig(AppConfig):
    name = 'points'


def make_payment(user):
    """
    Implement the payment logic here. Returning True always as of now.
    """
    return True


class UserProfile(object):

    def __init__(self, userid):
        self.user = User.objects.get(userid=userid)
        self.update_free_points()
        self.total_points = self.user.free_points + self.user.purchased_points
        self.items_purchased = self.get_purchased_items(
            status=ubiconf.TRANS_SUCCESS_STATUS, itemid__type__in=ubiconf.CANBEPURCHASED)
        self.transactions = self.get_transactions()
        self.items = self.get_items(
            is_available=True,
            points__lte=self.total_points,
            type__in=ubiconf.CANBEPURCHASED
        )

    def get_purchased_items(self, **kwargs):
        return list(Transaction.objects.filter(userid=self.user, **kwargs).values())

    def get_transactions(self, **kwargs):
        return list(Transaction.objects.filter(userid=self.user, **kwargs).values())

    def get_items(self, **kwargs):
        return list(Item.objects.filter(**kwargs).values())

    def get_purchase_points(self, fp, pp, item_points):
        """
        Based on the points user has and the price of the item, calculates the updated free points and purchased points
        :param fp: user's free_points
        :param pp: user's purchased_points
        :param item_points: total number of points an item costs
        :return: how many free and purchased points used along with new updated user's free point and purchased points
        """
        if fp >= item_points:
            use_fp = item_points
            new_fp = fp - item_points
            use_pp = 0
            new_pp = pp
        else:
            use_fp = fp
            new_fp = 0
            use_pp = item_points - use_fp
            new_pp = pp - use_pp
        return use_fp, use_pp, new_fp, new_pp

    def purchase_item(self, item):
        if item.points > self.total_points:
            raise InsufficientPoints(ubiconf.EXCEPTION_STR['INSUFFICIENTPOINTS'], item.points - self.total_points)
        use_free_points, use_purchase_points, new_free_points, new_purchase_points = self.get_purchase_points(
            self.user.free_points, self.user.purchased_points, item.points
        )
        with transaction.atomic():
            # create an entry in Transaction for the purchase
            trans = Transaction.objects.create(userid=self.user, itemid=item, status=ubiconf.TRANS_SUCCESS_STATUS,
                free_points_used=use_free_points, purchased_points_used=use_purchase_points)
            # Update user points after the purchase
            self.user.free_points = new_free_points
            self.user.purchased_points = new_purchase_points
            self.user.save()
            return trans.transactionid

    def purchase_points(self, item):
        if make_payment(self.user):
            with transaction.atomic():
                # create an entry in Transaction for the purchase
                trans = Transaction.objects.create(userid=self.user, itemid=item, status=ubiconf.TRANS_SUCCESS_STATUS,
                    )
                # Update user points after the purchase
                self.user.purchased_points += item.points
                self.user.save()
                return trans.transactionid

    def purchase(self, itemid):
        """
        Calls appropriate method to purchase items or points
        :param itemid: item unique id
        :return: True if transaction is successful. False or appropriate exceptions otherwise.
        """
        item = Item.objects.get(itemid=itemid)
        if item.type in ubiconf.CANBEPURCHASED:
            if item.type == 'PURCHASE_POINTS':
                return self.purchase_points(item)
            elif item.type == 'PURCHASE_ITEMS':
                return self.purchase_item(item)
        raise CanNotBePurchased(ubiconf.EXCEPTION_STR['CANTPURCHASE'])

    def update_free_points(self):
        """
        For current User calculate and update the free points he/she is eligible based on the time span passed.
        """
        # User's free_points is already reached max limit.
        if self.user.free_points >= ubiconf.MAX_FREE_POINTS_ALLOWED:
            return False

        try:
            free_item = Item.objects.get(type=ubiconf.FREE_ITEM_TYPE, points=ubiconf.FREE_ITEM_POINTS_VALUE)
        except models.ObjectDoesNotExist:
            print('No Free Item Found! Make sure there exists only one Item of Type = "{0}" having points = {1}'.format(
                ubiconf.FREE_ITEM_TYPE, ubiconf.FREE_ITEM_POINTS_VALUE))
            return False
        except Exception as err:
            print('Something went wrong! Error = {0}'.format(err))

        seconds_passed = ( now() > self.user.free_points_eligible_dtm and
                           (now() - self.user.free_points_eligible_dtm).seconds ) or 0
        point_units = seconds_passed // (60 * ubiconf.FREE_POINTS_ELIGIBILITY)

        # User is not eligible for any free points yet
        if not point_units:
            return False

        with transaction.atomic():

            # Update User's free_points considering it won't cross max free points allowed.
            if self.user.free_points + (point_units * free_item.points) > ubiconf.MAX_FREE_POINTS_ALLOWED:
                # A hypothetical case where we need to calculate what should be the number of actual items
                # purchased so that user would have reached the maximum points in one transaction.
                point_units = (ubiconf.MAX_FREE_POINTS_ALLOWED - self.user.free_points) // free_item.points
                self.user.free_points = ubiconf.MAX_FREE_POINTS_ALLOWED
                self.user.free_points_eligible_dtm = next_eligible_datetime()
            else:
                extra_seconds_passed = seconds_passed % (60 * ubiconf.FREE_POINTS_ELIGIBILITY)
                next_eligible_in_seconds = (60 * ubiconf.FREE_POINTS_ELIGIBILITY) - extra_seconds_passed
                self.user.free_points += (point_units * free_item.points)
                self.user.free_points_eligible_dtm = self.user.free_points_eligible_dtm + timedelta(
                    seconds=next_eligible_in_seconds)

            # create a single transaction for free items purchased of quantity 'point_units'
            Transaction.objects.create(
                userid=self.user, itemid=free_item, status=ubiconf.TRANS_SUCCESS_STATUS, quantity=point_units)

            self.user.save()