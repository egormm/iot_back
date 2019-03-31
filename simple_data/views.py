from rest_framework.views import APIView
from .serializers import SensorSerializer
from .models import Sensor
from django.utils import timezone
from rest_framework.response import Response


class DailyData(APIView):
    def get(self, request, days, id_sensor):
        d = timezone.now() - timezone.timedelta(days=days)
        dd = Sensor.objects.filter(
                date__gte=d, date__lte=timezone.now(), sensor_id__exact=id_sensor).all()
        serializer = SensorSerializer(dd, many=True)
        return Response(serializer.data)
