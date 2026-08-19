from django.urls import path
from .views import DocListView, DocDetailView

app_name = 'docs'

urlpatterns = [
    path('', DocListView.as_view(), name='list'),
    path('<slug:slug>/', DocDetailView.as_view(), name='detail'),
]
