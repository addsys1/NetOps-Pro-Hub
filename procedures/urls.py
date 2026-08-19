from django.urls import path
from .views import ProcedureListView, ProcedureDetailView, ProcedureGenerateView

app_name = 'procedures'

urlpatterns = [
    path('', ProcedureListView.as_view(), name='list'),
    path('<slug:slug>/', ProcedureDetailView.as_view(), name='detail'),
    path('<slug:slug>/generer/', ProcedureGenerateView.as_view(), name='generate'),
]
