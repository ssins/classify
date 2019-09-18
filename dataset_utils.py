from database import mysql, SQL
from torch.utils.data import Dataset, dataset
from torchvision import datasets, transforms
import random
import os
import sys
from config import IMG_EXTENSIONS, PATH


class ds(Dataset):
    def __init__(self, ds, root_path='', transform=None, target_transform=None):
        self.data = ds
        self.root_path = root_path
        self.transform = transform
        self.target_transform = target_transform
        self.id_to_idx = None

    def __getitem__(self, index):
        #path = os.path.join(self.root_path, self.data[index]['PATH'])
        path = self.root_path + self.data[index]['path']
        img = self.__pil_loader(path)
        target = self.data[index]['label_id'] - 102
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
        result = mysql.find('data_set', name=self.name)
        if result:
            self.id = result[0]['id']
            self.root_path = result[0]['root_path']
            self.valied = True
            self.class_to_idx, self.idx_to_class = self._get_classes()

    def load(self, limit=None):
        if not self.valied:
            return -1
        sql = SQL().Select('image').Where(data_set_id=self.id)
        sql.sql = sql.sql + "and label_id is not null "
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
            result = mysql.find(
                'model', id=id, data_set_id=self.id, name=name)
            if result:
                return result[0]
            return None
        sql = SQL().Select('model').Where(data_set_id=self.id, name=name)\
            .OrderBy(id='DESC').Limit(1).sql
        result = mysql.query(sql)
        if (result is not None) and (len(result) > 0):
            return result[0]
        return None

    def save_model(self, name, path, gpu_counts=None, is_half=None):
        if not self.valied:
            return False
        cols = {
            'name': name,
            'path': path,
            'data_set_id': self.id,
            'gpu_count': gpu_counts,
            'is_half': is_half
        }
        sql = SQL().Insert('model').Values(**cols).sql
        return mysql.run(sql)

    def _add_data_set(self, name, root_path=None):
        result = mysql.find('data_set', name=name)
        if result is False:
            sql = SQL().Insert('data_set').Values(name=name, root_path=root_path).sql
            return mysql.run(sql)
        return False

    def _add_data_set_from_folder(self, name, root_path=None):
        result = mysql.find('data_set', name=name)
        if result is False:
            sql = SQL().Insert('data_set').Values(name=name, root_path=root_path).sql
            if not mysql.run(sql):
                return False
            if root_path is None:
                return False
            return self._add_data_set_from_folder(name, root_path)
        data_set_id = result[0]['id']
        root = root_path if root_path is not None else result[0]['root_path']
        sql = SQL().Update('data_set').Set(
            root_path=root).Where(id=data_set_id).sql
        mysql.run(sql)
        classes, _ = self.__find_classes(root)
        tmp = mysql.is_print_log
        mysql.is_print_log = False
        count, classes_count = self._add_labels(classes, name)
        class_to_idx, idx_to_class = self._get_classes(data_set_id=data_set_id)
        if tmp:
            print('>>add {} labels done, total({})'.format(count, classes_count))
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
            if tmp:
                print('>>insert {} imgs done'.format(count))
        mysql.is_print_log = tmp
        return True

    def _add_labels(self, labels, data_set_name=None):
        if data_set_name is None:
            data_set_name = self.name
        result_ds = mysql.find('data_set', name=data_set_name)
        count = 0
        if result_ds:
            data_set_id = result_ds[0]['id']
            result_lb_list = mysql.find(
                'label', data_set_id=data_set_id)
            label_value_list = [x['value']
                                for x in result_lb_list] if result_lb_list else []
            start_idx = 0
            if result_lb_list:
                start_idx = len(result_lb_list)
            for label in labels:
                if label not in label_value_list:
                    sql = SQL().Insert('label').Values(
                        data_set_id=data_set_id, value=label, idx=(start_idx+count)).sql
                    if mysql.run(sql):
                        count += 1
        return count, start_idx + count

    def _add_img(self, data_set_name, path, idx=None):
        result = mysql.find('data_set', name=data_set_name)
        if result:
            data_set_id = result[0]['id']
            exist = mysql.find('label', data_set_id=data_set_id, idx=idx)
            if exist:
                sql = SQL().Insert('image').Values(
                    path=path, data_set_id=data_set_id, label_id=idx).sql
                return mysql.run(sql)
        return False

    def _get_classes(self, data_set_id=None):
        id = self.id if data_set_id is None else data_set_id
        sql = SQL().Select('label', ['idx', 'value']).Where(
            data_set_id=id).sql
        result = mysql.query(sql)
        idx_to_class = {}
        class_to_idx = {}
        if result is not None:
            for label in result:
                idx_to_class[label['idx']] = label['value']
            for (idx, cla) in idx_to_class.items():
                class_to_idx[cla] = idx
        return class_to_idx, idx_to_class

    def _re_init(self, confirm_name):
        if confirm_name != self.name:
            return False
        if not self.valied:
            return False
        sql = SQL().Delete('label').Where(data_set_id=self.id).sql
        mysql.run(sql)
        sql = SQL().Delete('image').Where(data_set_id=self.id).sql
        mysql.run(sql)
        sql = SQL().Delete('model').Where(data_set_id=self.id).sql
        mysql.run(sql)
        return True

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
    # if data._re_init('fruit'):
    #     data._add_data_set_from_folder('fruit', 'data/FRUIT/Training/')
    # else:
    #     print('f')
    data.load()
    data.shuffle()
    train,test=data.split(0.5)
    # print(r)
    # r= Dataset()._add_img('test','apple/3.jpg')
    # print(r)
    # test_set = datasets.ImageFolder(root='data/FRUIT/Test/', transform=transforms.Compose([
    #     transforms.ToTensor(),
    #     transforms.Normalize(
    #         (0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    # ]))
    print(len(train))
    print(train[663][1])
