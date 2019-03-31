from django.urls import path
from .views import DailyData, plot, Simple

urlpatterns = [
    path('data/<int:id_sensor>/<int:days>', DailyData.as_view()),
    path('plot/<int:id_sensor>/<int:days>/<pltype>', plot),
    path('simple', Simple.as_view())
]