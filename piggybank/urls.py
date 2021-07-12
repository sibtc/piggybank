from django.urls import include, path

import debug_toolbar
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from core import views

router = routers.SimpleRouter()

router.register(r"categories", views.CategoryModelViewSet, basename="category")
router.register(r"transactions", views.TransactionModelViewSet, basename="transaction")
router.register(r"currencies", views.CurrencyModelViewSet, basename="currency")

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("login/", obtain_auth_token, name="obtain-auth-token"),
    path("report/", views.TransactionReportAPIView.as_view(), name="report"),
    path("__debug__/", include(debug_toolbar.urls)),
] + router.urls
