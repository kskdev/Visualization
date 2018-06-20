# coding:utf-8

import collections

import numpy as np
import chainer
from chainer import cuda

import chainer.functions as F
import chainer.links as L

xp = cuda.cupy if cuda.available else np
"""
    VGGNet
    - It takes (224, 224, 3) sized image as imput
"""


# class VGG16(chainer.Chain):
class VGG16(chainer.link.Chain):
    def __init__(self, class_num):
        super(VGG16, self).__init__()
        with self.init_scope():
            self.conv1_1 = L.Convolution2D(3, 64, 3, stride=1, pad=1)
            self.conv1_2 = L.Convolution2D(64, 64, 3, stride=1, pad=1)

            self.conv2_1 = L.Convolution2D(64, 128, 3, stride=1, pad=1)
            self.conv2_2 = L.Convolution2D(128, 128, 3, stride=1, pad=1)

            self.conv3_1 = L.Convolution2D(128, 256, 3, stride=1, pad=1)
            self.conv3_2 = L.Convolution2D(256, 256, 3, stride=1, pad=1)
            self.conv3_3 = L.Convolution2D(256, 256, 3, stride=1, pad=1)

            self.conv4_1 = L.Convolution2D(256, 512, 3, stride=1, pad=1)
            self.conv4_2 = L.Convolution2D(512, 512, 3, stride=1, pad=1)
            self.conv4_3 = L.Convolution2D(512, 512, 3, stride=1, pad=1)

            self.conv5_1 = L.Convolution2D(512, 512, 3, stride=1, pad=1)
            self.conv5_2 = L.Convolution2D(512, 512, 3, stride=1, pad=1)
            self.conv5_3 = L.Convolution2D(512, 512, 3, stride=1, pad=1)

            # ===== Label Predictor
            self.fc6 = L.Linear(512 * 7 * 7, 4096)
            self.fc7 = L.Linear(4096, 4096)
            self.fc8 = L.Linear(4096, class_num)

            self.size = 224
            self.functions = collections.OrderedDict([
                ('conv1_1', [self.conv1_1, F.relu]),
                ('conv1_2', [self.conv1_2, F.relu]),
                ('pool1', [_max_pooling_2d]),
                ('conv2_1', [self.conv2_1, F.relu]),
                ('conv2_2', [self.conv2_2, F.relu]),
                ('pool2', [_max_pooling_2d]),
                ('conv3_1', [self.conv3_1, F.relu]),
                ('conv3_2', [self.conv3_2, F.relu]),
                ('conv3_3', [self.conv3_3, F.relu]),
                ('pool3', [_max_pooling_2d]),
                ('conv4_1', [self.conv4_1, F.relu]),
                ('conv4_2', [self.conv4_2, F.relu]),
                ('conv4_3', [self.conv4_3, F.relu]),
                ('pool4', [_max_pooling_2d]),
                ('conv5_1', [self.conv5_1, F.relu]),
                ('conv5_2', [self.conv5_2, F.relu]),
                ('conv5_3', [self.conv5_3, F.relu]),
                ('pool5', [_max_pooling_2d]),
                ('fc6', [self.fc6, F.relu, F.dropout]),
                ('fc7', [self.fc7, F.relu, F.dropout]),
                ('fc8', [self.fc8]),
                ('prob', [F.softmax]),
            ])

    def __call__(self, x, layers=['prob']):
        h = x
        activations = {'input': x}
        target_layers = set(layers)
        for key, funcs in self.functions.items():
            if len(target_layers) == 0:
                break
            for func in funcs:
                h = func(h)
            if key in target_layers:
                activations[key] = h
                target_layers.remove(key)
        return activations

    def extract(self, x, layers=['fc7']):
        x = chainer.Variable(self.xp.asarray(x))
        return self(x, layers=layers)


def _max_pooling_2d(x):
    return F.max_pooling_2d(x, ksize=2)
