from functools import reduce
import torch
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import dataset, DataLoader
from fastai.vision.models.wrn import *

from config import *
from my_net import *
import time
from dataset_utils import myDataset


class NetFun:
    def __init__(self, data_set_name):
        self.data_set_name = data_set_name
        self.model_weidth = None
        self.data = myDataset(self.data_set_name)
        self.class_to_idx, self.idx_to_class = self.data.class_to_idx, self.data.idx_to_class
        self.train_loader, self.test_loader = None, None
        self.model = None
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.default_epochs = DEFAULT_EPOCHS
        self.batch_size = DEFAULT_BATCH_SIZE
        self.use_half = False
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        self.optimizer = None
        self.__pre_net()

    def load_model(self, model_name=None, model_id=None):
        self.model_weidth = self.data.get_model(name=model_name, id=model_id)
        if self.model_weidth:
            try:
                self.use_half = (bool)(self.model_weidth['IS_HALF'])
                self.__pre_net()
                self.model.load_state_dict(
                    torch.load(self.model_weidth['PATH']))
            except:
                return False
            return True
        return False

    def load_data_set(self, batch_size=None, train_percent=0.8, transform=None):
        if not batch_size:
            self.batch_size = batch_size
        if transform:
            self.transform = transform
        return self.__load_data_from_database(train_percent)

    # todo test fun
    def train(self, epoch=None,sava_path=None):
        if not epoch:
            epoch = self.default_epochs
        for epoch in range(1, self.epochs + 1):
            self.__train(epoch)
            self.__test(top_x=3)
            if sava_path:
                if self.__save_model(save_path):
                    print('-----model saved:%s' % PATH)

    def classify(self, images=None):
        if images is None:
            time_start = time.time()
            data_iter = iter(self.test_loader)
            images, labels = data_iter.next()
            pred = self.__run(images)
            time_end = time.time()
            return pred, labels, time_end - time_start
        else:
            time_start = time.time()
            imgs = [self.pil_loader(path) for path in images]
            imgs = torch.stack(imgs, 0)
            pred = self.__run(imgs)
            time_end = time.time()
            return pred, time_end - time_start
    
    def __save_path(self,save_path):
        if torch.save(self.model.state_dict(), save_path):
            return self.data.save_model(self.model_weidth['NAME'],save_path,self.model_weidth['GPU_COUNT'])
        return False

    def __pre_net(self):
        self.model = WideResNet(
            num_groups=3, N=3, num_classes=len(self.idx_to_class), k=6, drop_p=0.)
        self.model = self.model.to(self.device)
        if self.use_half:
            self.model = self.model.half()
        if self.model_weidth and torch.cuda.device_count() > 1 and self.model_weidth['GPU_COUNT'] > 1:
            self.model = nn.DataParallel(self.model)
        self.optimizer = optim.SGD(
            self.model.parameters(), lr=0.1, momentum=0.9)

    def __train(self, epoch):
        self.model.train()
        for batch_idx, (data, target) in enumerate(self.train_loader):
            if self.use_half:
                data = data.half()
            data, target = data.to(self.device), target.to(self.device)
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = F.cross_entropy(output, target)
            loss.backward()
            self.optimizer.step()
            if (batch_idx + 1) % 200 == 0:
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    epoch, batch_idx *
                    len(data), len(self.train_loader.dataset),
                    100. * batch_idx / len(self.train_loader), loss.item()))

    def __test(self, top_x=1):
        self.model.eval()
        test_loss = 0
        correct = 0
        topx_correct = 0
        with torch.no_grad():
            for data, target in self.test_loader:
                if self.use_half:
                    data = data.half()
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                test_loss += F.cross_entropy(output,
                                             target, reduction='sum').item()
                pred = output.max(1, keepdim=True)[1]  # 找到概率最大的下标
                topx = output.topk(top_x, dim=1)[1]
                target = target.view_as(pred)
                correct += pred.eq(target).sum().item()
                topx_correct += list(
                    filter(lambda x: reduce(lambda l, m: l or m, list(map(lambda t: x[top_x] == t, x[0:top_x]))),
                           torch.cat([topx, target.view(-1, 1)], dim=1))).__len__()
        test_loss /= len(self.test_loader.dataset)
        print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%), Top-{}: {}/{} ({:.2f}%)\n'.format(
            test_loss, correct, len(self.test_loader.dataset),
            100. * correct /
            len(self.test_loader.dataset), top_x, topx_correct,
            len(self.test_loader.dataset), 100. * topx_correct / len(self.test_loader.dataset)))

    def __run(self, images):
        self.model.eval()
        with torch.no_grad():
            if self.use_half:
                images = images.half()
            output = self.model(images.to(self.device))
            # pred = output.max(1, keepdim=True)[1]
            if self.use_half:
                output = output.float()
            pred = output.to('cpu').topk(2, dim=1)[1]
        return pred

    def __load_data_from_database(self, train_percent):
        if self.data.valied:
            self.data.load()
            train_set, test_set = self.data.split(
                train_percent, True, self.transform)
            self.train_loader = torch.utils.data.DataLoader(
                train_set, batch_size=self.batch_size, shuffle=True)
            self.test_loader = torch.utils.data.DataLoader(
                test_set, batch_size=self.batch_size, shuffle=True)
            return True
        return False

    # def __load_data(self):
    #     train_set = datasets.ImageFolder(root=self.train_path,
    #                                      transform=self.transform)
    #     train_loader = torch.utils.data.DataLoader(
    #         train_set, batch_size=self.batch_size, shuffle=True)
    #     test_set = datasets.ImageFolder(root=self.test_path,
    #                                     transform=self.transform)
    #     test_loader = torch.utils.data.DataLoader(
    #         test_set, batch_size=self.batch_size, shuffle=True)
    #     return train_loader, test_loader, train_set.class_to_idx

    def pil_loader(self, path):
        from PIL import Image
        with open(path, 'rb') as f:
            img = Image.open(f)
            img = img.convert('RGB')
            if self.transform is not None:
                img = self.transform(img)
            return img


# if __name__ == "__main__":
#     test = [0, ]
#     if test:
#         print('f1')
#     print('t')
