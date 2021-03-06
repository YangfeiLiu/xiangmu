import torch
import torch.nn as nn
import torch.nn.functional as F
from enhance.aspp import build_aspp
from enhance.msfe import build_MSFE
from decoder.decoder import build_decoder
from encoder import build_backbone


class DeepLab(nn.Module):
    def __init__(self, in_channels, backbone='resnest101', enhance='aspp', output_stride=16, num_classes=21, freeze_bn=False):
        super(DeepLab, self).__init__()
        BatchNorm = nn.BatchNorm2d
        self.backbone = build_backbone(in_channels, backbone, output_stride, BatchNorm)
        if enhance == 'aspp':
            self.enhance = build_aspp(backbone, output_stride, BatchNorm)
        elif enhance == 'msfe':
            self.enhance = build_MSFE(2048, 256)
        else:
            print("Not implement!")
            exit(0)
        self.decoder = build_decoder(num_classes, backbone, BatchNorm)

        self.freeze_bn = freeze_bn

    def forward(self, input):
        x, low_level_feat = self.backbone(input)
        x = self.enhance(x)
        x = self.decoder(x, low_level_feat)
        x = F.interpolate(x, size=input.size()[2:], mode='bilinear', align_corners=True)

        return x

    def freeze_bn(self):
        for m in self.modules():
            m.eval()

    def get_1x_lr_params(self):
        modules = [self.backbone]
        for i in range(len(modules)):
            for m in modules[i].named_modules():
                if self.freeze_bn:
                    if isinstance(m[1], nn.Conv2d):
                        for p in m[1].parameters():
                            if p.requires_grad:
                                yield p
                else:
                    if isinstance(m[1], nn.Conv2d) or isinstance(m[1], nn.BatchNorm2d):
                        for p in m[1].parameters():
                            if p.requires_grad:
                                yield p

    def get_10x_lr_params(self):
        modules = [self.aspp, self.decoder]
        for i in range(len(modules)):
            for m in modules[i].named_modules():
                if self.freeze_bn:
                    if isinstance(m[1], nn.Conv2d):
                        for p in m[1].parameters():
                            if p.requires_grad:
                                yield p
                else:
                    if isinstance(m[1], nn.Conv2d) or isinstance(m[1], nn.BatchNorm2d):
                        for p in m[1].parameters():
                            if p.requires_grad:
                                yield p


from utils import modelProperty
if __name__ == "__main__":
    model = DeepLab(in_channels=3, backbone='seresnet101', output_stride=16, enhance='msfe')
    # model.eval()
    # input = torch.rand(1, 3, 513, 513)
    # output = model(input)
    # print(output.size())
    modelProperty.count_params(model, input_size=512)

