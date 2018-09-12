from django.conf.urls import url

from points.views import Ping, Connect, GetPoints, GetItems, PurchaseItem, GetInventory
from utils.auth import GetJWT

urlpatterns = [
    url('^$', Ping.as_view(), name='home'),
    url('^ping$', Ping.as_view(), name='ping'),
    url('^auth/?$', GetJWT.as_view(), name='auth'),
    url('^connect/(?P<userid>[0-9]+)/?$', Connect.as_view(), name='connect'),
    url('^getPoints/(?P<userid>[0-9]+)/?$', GetPoints.as_view(), name='get_points'),
    url('^getItems/(?P<userid>[0-9]+)/?$', GetItems.as_view(), name='get_items'),
    url('^purchaseItem/(?P<userid>[0-9]+)/(?P<itemid>[0-9]+)/?$', PurchaseItem.as_view(), name='purchase'),
    url('^getInventory/(?P<userid>[0-9]+)/?$', GetInventory.as_view(), name='get_inventory')
]