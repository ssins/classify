from functools import reduce
import torch
import torch.optim as optim
from torchvision import datasets, transforms
from fastai.vision.models.wrn import *
from config import *
from my_net import *


def train(model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.cross_entropy(output, target)
        loss.backward()
        optimizer.step()
        if (batch_idx + 1) % 200 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                       100. * batch_idx / len(train_loader), loss.item()))


def test(model, device, test_loader, top_x=1):
    model.eval()
    test_loss = 0
    correct = 0
    topx_correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.cross_entropy(output, target, reduction='sum').item()  # 将一批的损失相加
            pred = output.max(1, keepdim=True)[1]  # 找到概率最大的下标
            topx = output.topk(top_x, dim=1)[1]
            target = target.view_as(pred)
            correct += pred.eq(target).sum().item()
            topx_correct += list(
                filter(lambda x: reduce(lambda l, m: l or m, list(map(lambda t: x[top_x] == t, x[0:top_x]))),
                       torch.cat([topx, target.view(-1, 1)], dim=1))).__len__()

    test_loss /= len(test_loader.dataset)
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%), Top-{}: {}/{} ({:.2f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset), top_x, topx_correct,
        len(test_loader.dataset), 100. * topx_correct / len(test_loader.dataset)))


def run(model, device, images):
    model.eval()
    with torch.no_grad():
        output = model(images.to(device))
        # pred = output.max(1, keepdim=True)[1]  # 找到概率最大的下标
        pred = output.to('cpu').topk(2, dim=1)[1]
    return pred


def load_date():
    trainset = datasets.CIFAR10('data_cufar10', train=True, download=True,
                                transform=transforms.Compose([
                                    transforms.ToTensor(),
                                    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
                                ]))

    train_loader = torch.utils.data.DataLoader(
        trainset, batch_size=BATCH_SIZE, shuffle=True
    )

    testset = datasets.CIFAR10('data_cufar10', train=False,
                               transform=transforms.Compose([
                                   transforms.ToTensor(),
                                   transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
                               ]))
    test_loader = torch.utils.data.DataLoader(
        testset, batch_size=BATCH_SIZE, shuffle=True
    )
    return train_loader, test_loader


def main():
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    train_loader, test_loader = load_date()
    classes = ('plane', 'car', 'bird', 'cat',
               'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

    # model = myNet()
    # model = myResNet.myResNet(10)
    model = wrn_22()
    if torch.cuda.device_count() > 1:
        model = nn.DataParallel(model)
    model.to(DEVICE)
    optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
    if IS_LOAD_MODEL:
        model.load_state_dict(torch.load(PATH))
    for epoch in range(1, EPOCHS + 1):
        train(model, DEVICE, train_loader, optimizer, epoch)
        test(model, DEVICE, test_loader, top_x=3)
        torch.save(model.state_dict(), PATH)
        print('-----model saved:%s' % PATH)

    dataiter = iter(test_loader)
    images, labels = dataiter.next()
    pred = run(model, DEVICE, images)
    # pred = pred.resize(pred.size(0)).to('cpu')
    for j in range(BATCH_SIZE):
        print(classes[pred[j, 0]], ',', classes[pred[j, 1]], '(', classes[labels[j]], ')')
    # ToPILImage(((images[j] + 1) / 2).resize((100, 100)))
