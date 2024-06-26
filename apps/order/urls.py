from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PlaceOrderView, ClientOrderHistoryView, PartnerOrderHistoryView, PartnerPlaceOrderView, \
    OrderStatisticsView, IncomingOrdersView

router = DefaultRouter()
router.register(
    r"client-order-history", ClientOrderHistoryView, basename="client-order-history"
)
urlpatterns = [
    path("place-order/", PlaceOrderView.as_view(), name="place-order"),
    path("partner-place-order/", PartnerPlaceOrderView.as_view(), name="partner-place-order"),
    path("statistics/<int:establishment_id>/", OrderStatisticsView.as_view(), name='order-statistics'),
    path("orders/<int:establishment_id>/", IncomingOrdersView.as_view(), name='incoming-orders'),
    path("<int:establishment_id>/partner-order-history/", PartnerOrderHistoryView.as_view(),
         name="partner-order-history"),
    path("", include(router.urls)),
]
