from rest_framework import serializers
from .models import Sensor


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ('vw_30cm', 'vw_60cm', 't_30cm', 't_60cm', 'sensor_id', 'date')
