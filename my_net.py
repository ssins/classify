import torch.nn.functional as F
from torch import nn


class resBlock(nn.Module):
    def __init__(self, in_channel, out_channel, stride=1, shortcut=None):
        super().__init__()
        self.left = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, 3, stride, 1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.ReLU(True),
            nn.Conv2d(out_channel, out_channel, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channel)
        )
        self.right = shortcut

    def forward(self, x):
        out = self.left(x)
        res = x if self.right is None else self.right(x)
        out += res
        return F.relu(out)


class myResNet(nn.Module):
    def __init__(self, classify_num):
        super(myResNet, self).__init__()
        self.pre = nn.Sequential(
            nn.Conv2d(1, 64, 7, 2, 3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(3, 2, 1)
        )
        self.layer1 = self.make_layer(64, 128, 3)
        self.layer2 = self.make_layer(128, 256, 4, stride=2)
        self.layer3 = self.make_layer(256, 512, 6, stride=2)
        self.layer4 = self.make_layer(512, 512, 3, stride=2)
        self.fc = nn.Linear(512, classify_num)

    def forward(self, x):
        out = self.pre(x)
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = F.avg_pool2d(out, 7)
        out = out.view(out.size(0), -1)
        out = self.fc(out)
        return F.log_softmax(out, dim=1)

    def make_layer(self, in_channel, out_channel, block_num, stride=1):
        shortcut = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, 1, stride=stride, bias=False),
            nn.BatchNorm2d(out_channel)
        )
        layers = []
        layers.append(resBlock(in_channel, out_channel, stride, shortcut))
        for i in range(1, block_num):
            layers.append((resBlock(out_channel, out_channel)))
        return nn.Sequential(*layers)
