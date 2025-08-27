from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet

router = DefaultRouter()
router.register('', TransactionViewSet, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path
from transactions.views import transactions_page, categories_page

urlpatterns += [
    path("transactions-page/", transactions_page, name="transactions_page"),
    path("categories-page/", categories_page, name="categories_page"),
]

from django.urls import path
from .views import transactions_page, categories_page

urlpatterns = [
    path("transactions-page/", transactions_page, name="transactions_page"),
    path("categories-page/", categories_page, name="categories_page"),
]
