from database import mysql, SQL
from torch.utils.data import Dataset, dataset
from torchvision import datasets, transforms
import random
import os
import sys
from config import IMG_EXTENSIONS


class ds(Dataset):
    def __init__(self, ds, root_path='', transform=None, target_transform=None):
        self.data = ds
        self.root_path = root_path
        self.transform = transform
        self.target_transform = target_transform

    def __getitem__(self, index):
        #path = os.path.join(self.root_path, self.data[index]['PATH'])
        path = self.root_path + self.data[index]['PATH']
        img = self.__pil_loader(path)
        target = self.data[index]['LABEL_IDX']
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


class myDataset():
    def __init__(self, name=None):
        self.name = name
        self.data = []
        self.data_count = 0
        self.root_path = ''
        self.train_data_set = None
        self.test_data_set = None
        self.id = -1
        self.valied = False
        exist, result = mysql.exist('data_set', name=self.name)
        if exist:
            self.id = result[0]['ID']
            self.root_path = result[0]['ROOT_PATH']
            self.valied = True

    def load(self, limit=None):
        if not self.valied:
            return -1
        sql = SQL().Select('image').Where(data_set_id=self.id)
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

    def split(self, train=0.8, shuffle=True, transform=None):
        if not self.valied:
            return None, None
        if shuffle:
            self.shuffle()
        train = 0 if train < 0 else train
        train = 1 if train > 1 else train
        train_count = int(self.data_count * train)
        train_ds = self.data[:train_count]
        test_ds = self.data[train_count:]
        self.train_data_set = ds(
            train_ds, self.root_path, transform=transform)
        if len(test_ds) > 0:
            self.test_data_set = ds(
                test_ds, self.root_path, transform=transform)
        return self.train_data_set, self.test_data_set

    def get_model(self, name=None, id=None):
        if not self.valied:
            return False
        if id is not None:
            exist, result = mysql.exist(
                'model', id=id, data_set_id=self.id, name=name)
            if exist:
                return result[0]
            return None
        sql = SQL().Select('model').Where(data_set_id=self.id, name=name)\
            .OrderBy(id='DESC').Limit(1).sql
        result = mysql.query(sql)
        if (result is not None) and (len(result) > 0):
            return result[0]
        return None

    def save_model(self, name, path, gpu_counts=None, is_half=None, md5=None):
        if not self.valied:
            return False
        cols = {
            'name': name,
            'path': path,
            'data_set_id': self.id,
            'gpu_counts': gpu_counts,
            'is_half': is_half,
            'md5': md5
        }
        sql = SQL().Insert('model').Values(**cols).sql
        return mysql.run(sql)

    def _add_data_set(self, name, root_path=None):
        exist, result = mysql.exist('data_set', name=name)
        if exist is False:
            sql = SQL().Insert('data_set').Values(name=name, root_path=root_path).sql
            return mysql.run(sql)
        return False

    def _add_data_set_from_folder(self, name, root_path=None):
        exist, result = mysql.exist('data_set', name=name)
        if exist is False:
            sql = SQL().Insert('data_set').Values(name=name, root_path=root_path).sql
            if not mysql.run(sql):
                return False
            if root_path is None:
                return False
            return self._add_data_set_from_folder(name, root_path)
        root = root_path if root_path is not None else result[0]['ROOT_PATH']
        sql = SQL().Update('data_set').Set(
            root_path=root).Where(id=result[0]['ID']).sql
        mysql.run(sql)
        classes, class_to_idx = self.__find_classes(root)

        tmp = mysql.is_print_log
        mysql.is_print_log = False

        self._edit_labels(name, **class_to_idx)
        if tmp:
            print('>>update labels done')
        count = 0
        for label in classes:
            pre_path = os.path.join(root, label)
            files = self.__find_files(pre_path)
            for f in files:
                path = '/%s/%s' % (label, f)
                if self.__is_img_file(path):
                    self._add_img(name, path, class_to_idx[label])
                    count += 1
                    if tmp and count % 1000 == 0:
                        print('>>insert {} imgs'.format(count))
        mysql.is_print_log = tmp
        return True

    def _edit_labels(self, __data_set_name, **labels):
        exist, result_ds = mysql.exist('data_set', name=__data_set_name)
        if exist:
            data_set_id = result_ds[0]['ID']
            for (value, idx) in labels.items():
                exist, result_lb = mysql.exist(
                    'label', data_set_id=result_ds[0]['ID'], value=value)
                if exist:
                    sql = SQL().Update('label').Set(
                        idx=idx).Where(id=result_lb[0]['ID']).sql
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
                sql = SQL().Insert('image').Values(
                    path=path, data_set_id=data_set_id, label_idx=idx).sql
                return mysql.run(sql)
        return False

    def __find_classes(self, dir):
        if sys.version_info >= (3, 5):
            classes = [d.name for d in os.scandir(dir) if d.is_dir()]
        else:
            classes = [d for d in os.listdir(
                dir) if os.path.isdir(os.path.join(dir, d))]
        classes.sort()
        class_to_idx = {classes[i]: i for i in range(len(classes))}
        return classes, class_to_idx

    def __find_files(self, dir):
        if sys.version_info >= (3, 5):
            files = [d.name for d in os.scandir(dir) if d.is_file()]
        else:
            files = [d for d in os.listdir(
                dir) if os.path.isfile(os.path.join(dir, d))]
        return files

    def __is_img_file(self, filename):
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in IMG_EXTENSIONS)


if __name__ == "__main__":
    data = myDataset('fruit')
    data.load()
    data.shuffle()
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    train_data_set, test_data_set = data.split(0.8, True, transform)
    print(len(train_data_set))
    print(train_data_set[434])
    print(len(test_data_set))
    # data._add_data_set_from_folder('test', 'data/FRUIT/Training/')
    # # data.load()
    # print(data.get_model())
    # print(data.data)
    # # data.shuffle()
    # data.split(0.5)
    # r = Dataset()._add_labels('test',lb1=0,lb2=1)
    # r= Dataset()._add_img('test','apple/3.jpg',4)
    # print(r)
    # r= Dataset()._add_img('test','apple/3.jpg')
    # print(r)
    # test_set = datasets.ImageFolder(root='data/FRUIT/Test/', transform=transforms.Compose([
    #     transforms.ToTensor(),
    #     transforms.Normalize(
    #         (0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    # ]))
    # print(len(test_set))
    # print(test_set[663][1])
