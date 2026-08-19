from django.urls import path
from .views import ConceptListView, ConceptDetailView

app_name = 'concepts'

urlpatterns = [
    path('', ConceptListView.as_view(), name='list'),
    path('<slug:slug>/', ConceptDetailView.as_view(), name='detail'),
]
