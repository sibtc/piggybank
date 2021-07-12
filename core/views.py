from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_xml.renderers import XMLRenderer

from core.models import Category, Currency, Transaction
from core.permissions import AllowListPermission, IsAdminOrReadOnly
from core.reports import transaction_report
from core.serializers import (
    CategorySerializer,
    CurrencySerializer,
    ReadTransactionSerializer,
    ReportEntrySerializer,
    ReportParamsSerializer,
    WriteTransactionSerializer,
)


class CurrencyModelViewSet(ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    pagination_class = None
    renderer_classes = [JSONRenderer, XMLRenderer]


class CategoryModelViewSet(ModelViewSet):
    permission_classes = (DjangoModelPermissions | AllowListPermission,)
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class TransactionModelViewSet(ModelViewSet):
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ("description",)
    ordering_fields = ("amount", "date")
    filterset_fields = ("currency__code",)

    def get_queryset(self):
        return Transaction.objects.select_related("currency", "category", "user").filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadTransactionSerializer
        return WriteTransactionSerializer


class TransactionReportAPIView(APIView):
    def get(self, request):
        params_serializer = ReportParamsSerializer(data=request.GET, context={"request": request})
        params_serializer.is_valid(raise_exception=True)
        params = params_serializer.save()
        data = transaction_report(params)
        serializer = ReportEntrySerializer(instance=data, many=True)
        return Response(data=serializer.data)
