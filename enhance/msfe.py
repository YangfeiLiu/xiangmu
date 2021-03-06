import torch.nn as nn
import torch.nn.functional as F
import torch


class MSFE(nn.Module):
    def __init__(self, in_channel, out_channel):
        super(MSFE, self).__init__()
        dilation = [1, 5, 9, 13]
        self.dilate1 = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=3, dilation=dilation[0], padding=dilation[0]),
            nn.BatchNorm2d(out_channel)
        )
        self.dilate2 = nn.Sequential(
            nn.Conv2d(out_channel, out_channel, kernel_size=3, dilation=dilation[1], padding=dilation[1]),
            nn.BatchNorm2d(out_channel)
        )
        self.dilate3 = nn.Sequential(
            nn.Conv2d(out_channel, out_channel, kernel_size=3, dilation=dilation[2], padding=dilation[2]),
            nn.BatchNorm2d(out_channel)
        )
        self.dilate4 = nn.Sequential(
            nn.Conv2d(out_channel, out_channel, kernel_size=3, dilation=dilation[3], padding=dilation[3]),
            nn.BatchNorm2d(out_channel)
        )
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.conv_pool = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channel)
        )
        self.conv1 = nn.Conv2d(in_channel + out_channel * 5, 256, 1)
        self.bn1 = nn.BatchNorm2d(256)
        self.relu = nn.ReLU(inplace=True)
        # self.dropout = nn.Dropout(0.5)
        self._init_weight()
    
    def _init_weight(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                torch.nn.init.kaiming_normal_(m.weight)
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
                    
    def forward(self, x):
        dilate1_out = F.relu(self.dilate1(x))
        dilate2_out = F.relu(self.dilate2(dilate1_out))
        dilate3_out = F.relu(self.dilate3(dilate2_out))
        dilate4_out = F.relu(self.dilate4(dilate3_out))
        pool_out = self.conv_pool(F.interpolate(self.pool(x), size=(x.size(2), x.size(3)), mode='bilinear', align_corners=True))

        out = torch.cat([x, dilate1_out, dilate2_out, dilate3_out, dilate4_out, pool_out], dim=1)
        # out = torch.cat([x, dilate1_out, dilate2_out, dilate3_out, dilate4_out], dim=1)
        out = self.relu(self.bn1(self.conv1(out)))
        return out


def build_MSFE(in_channel, out_channel):
    return MSFE(in_channel, out_channel)
