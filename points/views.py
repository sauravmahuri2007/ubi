from django.db.models import ObjectDoesNotExist
from django.views.generic import View
from django.http.response import JsonResponse

from .apps import UserProfile
from ubiexceptions.generic import CanNotBePurchased, InsufficientPoints
from utils.auth import BasicAuthMixin, JWTAuthMixin, get_token

# Create your views here.

class Ping(View):

    def get(self, request):
        return JsonResponse('Pong!', status=200, safe=False)


class Connect(BasicAuthMixin, View):
    """
    Established the connection using Basic Auth.
    Returns complete user profile with a JsonWebToken which can be used for further API call
    """

    def get(self, request, *args, **kwargs):
        userid = kwargs.get('userid')
        try:
            uobj = UserProfile(userid=userid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 404, 'error': 'DoesNotExist'}, status=404, safe=False)
        d = {
            'inventory': uobj.items,
            'free_points': uobj.user.free_points,
            'purchased_points': uobj.user.purchased_points,
            'userid': uobj.user.userid,
            'name': uobj.user.name,
            'purchased_list': uobj.items_purchased,
            'transactions': uobj.transactions,
            'next_free_points_eligible_datetime': uobj.user.free_points_eligible_dtm,
            'token': get_token(request)
        }
        return JsonResponse(d, status=200, safe=False, content_type='application/json')


class GetPoints(JWTAuthMixin, View):
    """
    Returns the points (Free, Purchased) points available to the User.
    """

    def get(self, request, *args, **kwargs):
        userid = kwargs.get('userid')
        try:
            uobj = UserProfile(userid=userid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 404, 'error': 'DoesNotExist'}, status=404, safe=False)
        return JsonResponse({
            'userid': userid,
            'free_points': uobj.user.free_points,
            'purchased_points': uobj.user.purchased_points}, status=200, safe=False)


class GetItems(JWTAuthMixin, View):
    """
    Returns the list of transaction which is having items being purchased by the User.
    """

    def get(self, request, *args, **kwargs):
        userid = kwargs.get('userid')
        try:
            uobj = UserProfile(userid=userid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 404, 'error': 'DoesNotExist'}, status=404, safe=False)
        return JsonResponse({
            'userid': userid,
            'purchased_items': uobj.items_purchased}, status=200, safe=False)


class PurchaseItem(JWTAuthMixin, View):
    """
    Purchase the selected items.
    """

    def get(self, request, *args, **kwargs):
        userid = kwargs.get('userid')
        itemid = kwargs.get('itemid')
        try:
            uobj = UserProfile(userid=userid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 404, 'error': 'DoesNotExist'}, status=404, safe=False)
        try:
            trans_id = uobj.purchase(itemid=itemid)
        except InsufficientPoints as err:
            return JsonResponse({
                'userid': userid,
                'message': err.message, 'extra_points': err.extra_points, 'status': 'error'}, status=500, safe=False)
        except CanNotBePurchased as err:
            return JsonResponse({
                'userid': userid, 'message': err.message, 'status': 'error'}, status=500, safe=False)
        return JsonResponse({'userid': userid,
                             'message': 'Success', 'transactionid':  trans_id}, status=200, safe=False)


class GetInventory(JWTAuthMixin, View):
    """
    Returns the list of items which can be purchased by the User based on the available points.
    """

    def get(self, request, *args, **kwargs):
        userid = kwargs.get('userid')
        uobj = UserProfile(userid=userid)
        inventory = {
            'userid': userid,
            'inventory': uobj.items
        }
        return JsonResponse(inventory, status=200, safe=False, content_type='application/json')