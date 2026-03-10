import torch
import torchvision
from torch import nn, optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
# from ResNet import resnet50  # 从自定义的ResNet.py文件中导入resnet50这个函数
from torchvision.models import resnet50
import numpy as np
import matplotlib.pyplot as plt
from torch.autograd import Variable
 
# -------------------------------------------------- #
#（0）参数设置
# -------------------------------------------------- #

batch_size = 32  # 每个step训练32张图片
epochs = 10  # 共训练10次
if torch.cuda.is_available():  # 如果有GPU就用，没有就用CPU
    device = torch.device('cuda')
else:
    device = torch.device('cpu')
 

    
# -------------------------------------------------- #
#（1）构造数据集
# -------------------------------------------------- #
# 训练集的数据预处理
transform_train = transforms.Compose([
    # 数据增强，随机裁剪224*224大小
    transforms.RandomResizedCrop((224,224)),
    # 数据增强，随机水平翻转
    transforms.RandomHorizontalFlip(),
    # 数据变成tensor类型，像素值归一化，调整维度[h,w,c]==>[c,h,w]

    #transforms.RandomCrop(50),
    
    #transforms.ColorJitter(brightness=0.5, contrast=0.5, hue=0.5),##############################

    transforms.ToTensor(),
    # 对每个通道的像素进行标准化，给出每个通道的均值和方差
    transforms.Normalize([0.5,0.5,0.5], [0.5,0.5,0.5])])

# 验证集的数据预处理
transform_val = transforms.Compose([
    # 将输入图像大小调整为224*224
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5,0.5,0.5], [0.5,0.5,0.5])])
 
# 读取训练集并预处理
train_dataset = datasets.ImageFolder('E:\\Desktop\\深度学习+\\道路图像集\\裂缝混凝土桥梁甲板，墙壁和人行道\\Walls\\train',transform = transform_train)  # 训练集的预处理方法
 
# 读取验证集并预处理
val_dataset = datasets.ImageFolder('E:\\Desktop\\深度学习+\\道路图像集\\裂缝混凝土桥梁甲板，墙壁和人行道\\Walls\\test',  # 验证集图片所在的文件夹
                                     transform = transform_val)  # 验证集的预处理方法

# 查看训练集和验证集的图片数量
train_num = len(train_dataset)
val_num = len(val_dataset)
print('train_num:', train_num, 'val_num:', val_num)   # 453, 112
 
# 查看图像类别及其对应的索引
class_dict = train_dataset.class_to_idx
print(class_dict)  # {'Bananaquit': 0, 'Black Skimmer': 1, 'Black Throated Bushtiti': 2, 'Cockatoo': 3}
# 将类别名称保存在列表中
class_names = list(class_dict.keys())
 
# 构造训练集
train_loader = DataLoader(dataset=train_dataset,  # 接收训练集
                          batch_size=batch_size,  # 训练时每个step处理32张图
                          shuffle=True,           # 打乱每个batch
                          num_workers=0)          # 加载数据时的线程数量，windows环境下只能=0
 
# 构造验证集
val_loader = DataLoader(dataset=val_dataset,
                        batch_size=batch_size,
                        shuffle=False,
                        num_workers=0)

modellr = 1e-4


# 实例化模型并且移动到GPU
criterion = nn.CrossEntropyLoss()
model = torchvision.models.resnet18(weights = torchvision.models.ResNet18_Weights.DEFAULT)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 100)
model.to(device)
# 选择简单暴力的Adam优化器，学习率调低
optimizer = optim.Adam(model.parameters(), lr=modellr)
 
def adjust_learning_rate(optimizer, epoch):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    modellrnew = modellr * (0.1 ** (epoch // 50))
    print("lr:", modellrnew)
    for param_group in optimizer.param_groups:
        param_group['lr'] = modellrnew


# 定义训练过程
 
def train(model, device, train_loader, optimizer, epoch):
    model.train()
    sum_loss = 0
    total_num = len(train_loader.dataset)
    print(total_num, len(train_loader))
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = Variable(data).to(device), Variable(target).to(device)
        output = model(data)
        loss = criterion(output, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print_loss = loss.data.item()
        sum_loss += print_loss
        if (batch_idx + 1) % 50 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, (batch_idx + 1) * len(data), len(train_loader.dataset),
                       100. * (batch_idx + 1) / len(train_loader), loss.item()))
    ave_loss = sum_loss / len(train_loader)
    print('epoch:{},loss:{}'.format(epoch, ave_loss))

def val(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    total_num = len(test_loader.dataset)
    print(total_num, len(test_loader))
    with torch.no_grad():
        for data, target in test_loader:
            data, target = Variable(data).to(device), Variable(target).to(device)
            output = model(data)
            loss = criterion(output, target)
            _, pred = torch.max(output.data, 1)
            correct += torch.sum(pred == target)
            print_loss = loss.data.item()
            test_loss += print_loss
        correct = correct.data.item()
        acc = correct / total_num
        avgloss = test_loss / len(test_loader)
        print('\nVal set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
            avgloss, correct, len(test_loader.dataset), 100 * acc))
 
 
# 训练
for epoch in range(1, epochs + 1):
    adjust_learning_rate(optimizer, epoch)
    train(model, device, train_loader, optimizer, epoch)
    val(model, device, val_loader)
    torch.save(model, 'model_Walls{}.pth'.format(epoch))