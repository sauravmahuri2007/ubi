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

    def get(self, request, *args, **kwargs):
        userid = kwargs.get('userid')
        uobj = UserProfile(userid=userid)
        d = {
            'inventory': uobj.items,
            'free_points': uobj.user.free_points,
            'purchased_points': uobj.user.purchased_points,
            'id': uobj.user.userid,
            'name': uobj.user.name,
            'purchased_list': uobj.items_purchased,
            'transactions': uobj.transactions,
            'next_free_points_eligible_datetime': uobj.user.free_points_eligible_dtm,
            'token': get_token(request)
        }
        return JsonResponse(d, status=200, safe=False, content_type='application/json')


class GetPoints(JWTAuthMixin, View):
    pass


class GetItems(JWTAuthMixin, View):

    def get(self, request, *args, **kwargs):
        userid = kwargs.get('userid')
        uobj = UserProfile(userid=userid)
        return JsonResponse({'purchased_items': uobj.items_purchased}, status=200, safe=False)


class PurchaseItem(JWTAuthMixin, View):
    """
    Purchase the items selected
    """
    def get(self, request, *args, **kwargs):
        userid = kwargs.get('userid')
        itemid = kwargs.get('itemid')
        uobj = UserProfile(userid=userid)
        try:
            trans_id = uobj.purchase(itemid=itemid)
        except InsufficientPoints as err:
            return JsonResponse({
                'message': err.message, 'extra_points': err.extra_points, 'status': 'error'}, status=500, safe=False)
        except CanNotBePurchased as err:
            return JsonResponse({'message': err.message, 'status': 'error'}, status=500, safe=False)
        return JsonResponse({'message': 'Success', 'transactionid':  trans_id}, status=200, safe=False)


class GetInventory(JWTAuthMixin, View):
    pass