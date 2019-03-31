from django.urls import path
from .views import DailyData, plot, state

urlpatterns = [
    path('data/<int:id_sensor>/<int:days>', DailyData.as_view()),
    path('plot/<int:id_sensor>/<int:days>/<pltype>', plot),
    path('state', state)
]