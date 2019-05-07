from database import mysql, SQL
from torch.utils.data import dataset
from torchvision import transforms
import random
import os


class Dataset():
    def __init__(self, name=None):
        self.name = name
        self.data = []
        self.data_count = 0
        self.root_path = ''
        self.train_data_set = None
        self.test_data_set = None
        self.name_id = -1

    def load(self, limit=None):
        sql = SQL().Select('data_set').Where(name=self.name).Limit(1).sql
        result = mysql.query(sql)
        try:
            self.name_id = result[0]['ID']
            self.root_path = result[0]['ROOT_PATH']
        except:
            return -1
        sql = SQL().Select('image').Where(data_set_id=self.name_id)
        sql.sql = sql.sql + "and label_idx is not null "
        if limit is not None:
            sql = sql.Limit(limit)
        sql = sql.sql
        result = mysql.query(sql)
        if result is None:
            return -1
        self.data = list(result)
        self.data_count = len(self.data)
        return len(self.data)

    def shuffle(self):
        random.shuffle(self.data)

    def split(self, train=0.8, shuffle=True, transforms=None):
        if shuffle:
            self.shuffle()
        train = 0 if train < 0 else train
        train = 1 if train > 1 else train
        train_count = int(self.data_count * train)
        train_ds = self.data[:train_count]
        test_ds = self.data[train_count:]
        self.train_data_set = __Dataset(
            train_ds, self.root_path, self.transform, transforms)
        if len(test_ds) > 0:
            self.test_data_set = __Dataset(
                test_ds, self.root_path, self.transform, transforms)
        return self.train_data_set, self.test_data_set

    def _add_data_set(self, name, root_path):
        exist, result = mysql.exist('data_set', name=name)
        if exist is False:
            sql = SQL().Insert('data_set').Values(name=name, root_path=root_path).sql
            return mysql.run(sql)
        return False

    def _edit_labels(self, __data_set_name, **labels):
        exist, result_ds = mysql.exist('data_set', name=__data_set_name)
        if exist:
            data_set_id = result_ds[0]['ID']
            for (value, idx) in labels.items():
                exist, result_lb = mysql.exist(
                    'label', data_set_id=result_ds[0]['ID'], value=value)
                if exist:
                    sql = SQL().Update('label').Set(idx=idx).Where(id=result_lb[0]['ID']).sql
                    mysql.run(sql)
                else:
                    sql = SQL().Insert('label').Values(
                    data_set_id=data_set_id, value=value, idx=idx).sql
                    mysql.run(sql)
            return True
        return False

    def _add_img(self, data_set_name, path, idx=None):
        exist, result = mysql.exist('data_set', name=data_set_name)
        if exist:
            data_set_id = result[0]['ID']
            exist, _ = mysql.exist('label', data_set_id=data_set_id, idx=idx)
            if exist:
                sql = SQL().Insert('image').Values(path=path, data_set_id=data_set_id, label_idx=idx).sql
                return mysql.run(sql)
        return False

# todo 测试
class __Dataset(Dataset):
    def __init__(self, ds, root_path='', transform=None, target_transform=None):
        self.data = ds
        self.root_path = root_path
        self.transform = transform
        self.target_transform = target_transform

    def __getitem__(self, index):
        path = os.path.join(self.root_path, data[index]['PATH'])
        img = self.__pil_loader(path)
        target = data[index]['LABEL_IDX']
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return img, target

    def __len__(self):
        return len(self.data)

    def __pil_loader(self, path):
        from PIL import Image
        with open(path, 'rb') as f:
            img = Image.open(f)
            img = img.convert('RGB')
            return img


if __name__ == "__main__":
    data = Dataset('test')
    data.load()
    print(data.data)
    # # data.shuffle()
    # data.split(0.5)
    # r = Dataset()._add_labels('test',lb1=0,lb2=1)
    # r= Dataset()._add_img('test','apple/3.jpg',4)
    # print(r)
    # r= Dataset()._add_img('test','apple/3.jpg')
    # print(r)
