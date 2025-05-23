import torch
import torch.nn as nn
import torchvision.transforms.functional as TF

# Implementation from scracth of UNET network
class Conv2Layer(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Conv2Layer, self).__init__()
        self.conv = nn.Sequential (
            nn.Conv2d(in_channels, out_channels, kernel_size=3 ,stride=1 ,padding=1,bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels, out_channels, kernel_size=3 ,stride=1 ,padding=1,bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        return self.conv(x)
    
class UNET(nn.Module):
    def __init__(self, in_channels=3, out_channels=1, features=[64, 128, 256, 512]): #binary output for 2 class segmentation
        super(UNET,self).__init__()
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Down part
        for feature in features:
            self.downs.append(Conv2Layer(in_channels, feature))
            in_channels=feature

        # Up part
        for feature in reversed(features):
            self.ups.append(nn.ConvTranspose2d(feature*2,feature, kernel_size=2, stride=2))
            self.ups.append(Conv2Layer(feature*2,feature))
            in_channels=feature

        self.bottleneck = Conv2Layer(features[-1], features[-1]*2)
        self.final_conv = nn.Conv2d(features[0], out_channels,kernel_size=1)

    def forward(self,x): #forward propagation
        skip_connections=[]
        for down in self.downs:
            x=down(x)
            skip_connections.append(x)
            x= self.pool(x)
        x=self.bottleneck(x)
        skip_connections=skip_connections[::-1] #reverse the list
        
        for idx in range (0, len(self.ups),2):
            x=self.ups[idx](x)
            skip_connection=skip_connections[idx//2]
            if x.shape != skip_connection.shape:
                x = TF.resize(x, size=skip_connection.shape[2:]) #heigh and width matching before concatenation
            concat_skip=torch.cat((skip_connection,x),dim=1)
            x=self.ups[idx+1](concat_skip)
        return self.final_conv(x)
    
    def train(self,x): #backward propagation, needs a loader, model, optimizer, loss function, scaler
        pass

def test():
    x=torch.randn((3,1,160,160))
    model = UNET(in_channels=1, out_channels=1)
    preds = model(x)
    print(preds.shape)
    print(x.shape)
    assert preds.shape==x.shape

if __name__=='__main__':
    test()