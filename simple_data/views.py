from rest_framework.views import APIView
from .serializers import SensorSerializer
from .models import Sensor
from .nn.vineyard_renderer.vineyard_renderer import *
from .nn.disease_detector.disease_detector import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from django.http import HttpResponse
from datetime import datetime, timezone, timedelta


def check_url(*, days, id_sensor):
    if days < 1 or days > 90:
        raise NotFound(detail='maximum period = 90days, minimum = 1day', code=404)
    if id_sensor < 0 or id_sensor > 9:
        raise NotFound(detail='numbers of sensors from 0 to 9, included', code=404)


class DailyData(APIView):
    def get(self, request, days, id_sensor):
        check_url(days=days, id_sensor=id_sensor)
        d = datetime.now() - timedelta(days=days)
        dd = Sensor.objects.filter(
            date__gte=d, date__lte=datetime.now(), sensor_id__exact=id_sensor).all()
        serializer = SensorSerializer(dd, many=True)
        responce = Response(serializer.data)
        return responce


@api_view(['Get'])
def plot(request, id_sensor, days, pltype):
    check_url(days=days, id_sensor=id_sensor)
    if pltype != 'moist' and pltype != 'temp':
        raise NotFound(detail='only \'moist\' and \'temp\' are available', code=404)

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter

    fig = Figure()
    ax = fig.add_subplot(111)
    x = []
    y1 = []
    y2 = []
    now = datetime.now()
    for el in Sensor.objects.filter(
            date__gte=now - timedelta(days=days), date__lte=now, sensor_id__exact=id_sensor):
        x.append(el.date)
        if pltype == 'moist':
            y1.append(el.vw_30cm)
            y2.append(el.vw_60cm)
        else:
            y1.append(el.t_30cm)
            y2.append(el.t_60cm)
    ax.plot_date(x, y1, 'r-')
    ax.plot_date(x, y2, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/jpg')
    canvas.print_jpg(response)
    return response


@api_view(['Get'])
def state(self):
    T_period = timedelta(days=30)
    M_period = timedelta(hours=12)
    now = datetime.now()
    T_MIN = 5
    T_MAX_30_DAYS = 480
    M_MAX = 0.3
    M_MIN = 0.2
    sum_T = [0 for _ in range(10)]
    ct = 0
    sum_M = [0 for _ in range(10)]
    cm = 0
    sensors = [True for _ in range(10)]
    is_ok = True
    bad = set()
    d = now - T_period
    dd = now - M_period
    for el in Sensor.objects.filter(date__lte=now, date__gte=d):
        if sensors[el.sensor_id]:
            if el.t_60cm < T_MIN:
                sensors[el.sensor_id] = False
                is_ok = False
                bad.add(el.sensor_id+1)
            sum_T[el.sensor_id] += el.t_60cm
            ct += 1

    for el in Sensor.objects.filter(date__lte=now, date__gte=dd):
        if sensors[el.sensor_id]:
            if el.vw_30cm > M_MAX:
                sensors[el.sensor_id] = False
                is_ok = False
                bad.add(el.sensor_id+1)
            sum_M[el.sensor_id] += el.vw_30cm
            cm += 1

    for i in range(10):
        if sum_T[i]/(ct/10) > T_MAX_30_DAYS:
            sensors[i] = False
            is_ok = False
            bad.add(i+1)
        if sum_M[i]/(cm/10) < M_MIN:
            sensors[i] = False
            is_ok = False
            bad.add(i+1)

    if is_ok:
        state_description = "Все хорошо!"
    else:
        if len(bad) == 1:
            state_description = "Неблагоприятные условия на участке " + str(bad[0])
        else:
            state_description = "Неблагоприятные условия на участках " + ', '.join(map(str, sorted(bad)))
    return Response({"state_description": state_description, "is_ok": is_ok,
                     "sensors": sensors})


@api_view(['Get'])
def plot_state():
    M_period = timedelta(hours=12)
    now = datetime.now()
    M_MAX = 0.3
    M_MIN = 0.2
    sum_M = [0 for _ in range(10)]
    cm = 0
    sensors = [True for _ in range(10)]
    dd = now - M_period
    for el in Sensor.objects.filter(date__lte=now, date__gte=dd):
        if sensors[el.sensor_id]:
            if el.vw_30cm > M_MAX:
                sensors[el.sensor_id] = False
            sum_M[el.sensor_id] += el.vw_30cm
            cm += 1
    for i in range(10):
        if sum_M[i] / (cm / 10) < M_MIN:
            sensors[i] = False

    health_states = [get_sensor_health_state(i) for i in range(10)]

    canvas = draw_vineyard(sensors, health_states, 'plot.png')
    response = HttpResponse(content_type='image/jpg')
    canvas.print_jpg(response)
    return response
