from django.urls import path
from .views import DailyData

urlpatterns = [
    path('data/<int:id_sensor>/<int:days>', DailyData.as_view())
]