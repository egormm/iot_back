import os
import torch

from .disease_detector_utils import load_data
from .constants import *
from .model import Net
# from disease_detector_utils import load_data
# from constants import *
# from model import Net


prefix = os.path.dirname(os.path.realpath(__file__))

# Load model
net = Net()
net.load_state_dict(torch.load(os.path.join(prefix, MODEL_PATH)))

# Preload images
data_loader = load_data(os.path.join(prefix, IMAGES_PATH))


def get_diseases(sensor_id, net=net, data_loader=data_loader, verbose=False):
    net.eval()

    images, labels = data_loader.next()
    with torch.no_grad():
        outputs = net(images)
    _, predicted = torch.max(outputs.data, 1)

    if verbose:
        correct = (predicted == labels).sum()
        print('Prediction accuracy:', correct.item() / (labels.size(0) + EPS))

    diseases = set()
    for lbl in predicted:
        if lbl.item() in DICTIONARY and DICTIONARY[lbl.item()]:
            diseases.add(DICTIONARY[lbl.item()])
    return list(diseases)


def get_sensor_health_state(sensor_id, binary_only=True):
    if binary_only:
        return len(get_diseases(sensor_id)) == 0
    diseases = get_diseases(sensor_id)
    if len(diseases) == 0:
        state_description = 'Растения здоровы.'
    elif len(diseases) == 1:
        state_description = 'Обнаружена болезнь %s.' % diseases[0]
    else:
        state_description = 'Обнарежны болезни ' + ', '.join(diseases) + '.'
    return {
        'state': len(diseases) == 0,
        'state_description': state_description
    }
