import os
import numpy as np
import matplotlib.pyplot as plt

from .constants import *
from .vineyard_renderer_utils import Vineyard
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


prefix = os.path.dirname(os.path.realpath(__file__))

leaf_positions = np.load(os.path.join(prefix, LEAF_POSITIONS_PATH))
num_leaves = leaf_positions.shape[1]


def draw_vineyard(dry_vines, ill_vines, path, leaf_positions=leaf_positions):
    filtered_leaf_positions = np.array([
        leaf_positions[i][np.random.choice(num_leaves, num_leaves // 2)] if not dry_vines[i % 10]
        else leaf_positions[i]
        for i in range(leaf_positions.shape[0])
    ])
    vy = Vineyard(filtered_leaf_positions, dry_vines, ill_vines)
    for i in range(1):
        vy.update()
    vy.fig.autofmt_xdate()
    canvas = FigureCanvas(vy.fig)
    return canvas
    # plt.savefig(path, bbox_inches='tight', pad_inches=0)


# Usage example
# image will be saved to path
# array consists of 10 ints or bools (1/True for normal plants, 0/False for dry plants)
# draw_vineyard([0, 1, 1, 1, 1, 1, 1, 1, 1, 0], 'plot.png')