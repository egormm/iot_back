from rest_framework.views import APIView
from .serializers import SensorSerializer
from .models import Sensor
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import Http404

class DailyData(APIView):
    def get(self, request, days, id_sensor):
        d = timezone.now() - timezone.timedelta(days=days)
        dd = Sensor.objects.filter(
            date__gte=d, date__lte=timezone.now(), sensor_id__exact=id_sensor).all()
        serializer = SensorSerializer(dd, many=True)
        return Response(serializer.data)


@api_view(['Get'])
def plot(request, id_sensor, days, pltype):
    from rest_framework.exceptions import NotFound
    if pltype != 'moist' and pltype != 'temp':
        raise NotFound(detail='only \'moist\' and \'temp\' are available', code=404)
    from django.http import HttpResponse
    import datetime

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter

    fig = Figure()
    ax = fig.add_subplot(111)
    x1 = []
    y1 = []
    y2 = []
    now = datetime.datetime.now()
    for el in Sensor.objects.filter(
            date__gte=now - datetime.timedelta(days=days), date__lte=now, sensor_id__exact=id_sensor):
        x1.append(el.date)
        if pltype == 'moist':
            y1.append(el.vw_30cm)
            y2.append(el.vw_60cm)
        else:
            y1.append(el.t_30cm)
            y2.append(el.t_60cm)
    ax.plot_date(x1, y1, 'r-')
    ax.plot_date(x1, y2, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/jpg')
    canvas.print_jpg(response)
    return response
