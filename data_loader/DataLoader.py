import os
import torch
from torch.utils.data import Dataset
from pathlib import Path

from torch.utils.data import DataLoader
import cv2

from torchvision.transforms import Resize, RandomHorizontalFlip, RandomVerticalFlip
import matplotlib.pyplot as plt
import h5py
import numpy as np
import matplotlib.pyplot as plt
import torch.nn.functional as F

class GaoFen2(Dataset):
    def __init__(self, dir, transforms=None) -> None:
        f = h5py.File(str(dir), 'r+')
        self.hr = torch.tensor(f['gt'][()], dtype=torch.float32)
        self.mslr = torch.tensor(f['ms'][()], dtype=torch.float32)
        self.pan = torch.tensor(f['pan'][()], dtype=torch.float32)
        self.transforms = transforms

        # precomputed
        self.pan_mean = torch.tensor([250.0172]).view(1, 1, 1, 1)
        self.pan_std = torch.tensor([80.2501]).view(1, 1, 1, 1)

        self.mslr_mean = torch.tensor(
            [449.9449, 308.7544, 238.3702, 220.3061]).view(1, 4, 1, 1)
        self.mslr_std = torch.tensor(
            [70.8778, 63.7980, 71.3171, 66.8198]).view(1, 4, 1, 1)

    def __len__(self):
        return self.mslr.shape[0]

    def __getitem__(self, index):

        pan = self.pan[index]
        mslr = self.mslr[index]
        hr = self.hr[index]

        if self.transforms:
            for transform, prob in self.transforms:
                if torch.randn(1) < prob:
                    pan = transform(pan)
                    mslr = transform(mslr)
                    hr = transform(hr)

        return (pan, mslr, hr)


"""if __name__ == "__main__":
    batch_size = 1
    shuffle = True

    dir_tr = Path(f'F:/Data/GaoFen-2/train/train_gf2-001.h5')
    dir_val = Path(f'F:/Data/GaoFen-2/val/valid_gf2.h5')
    # dir_test = Path(f'F:/Data/GaoFen-2/train/train_gf2-001.h5')

    tr_dataset = GaoFen2(
        dir_tr, transforms=[(RandomHorizontalFlip(1), 0.3), (RandomVerticalFlip(1), 0.3)])
    train_loader = DataLoader(
        dataset=tr_dataset, batch_size=batch_size, shuffle=shuffle)

    val_dataset = GaoFen2(
        dir_val)
    validation_loader = DataLoader(
        dataset=val_dataset, batch_size=batch_size, shuffle=shuffle)

    '''# train shapes
    pan, mslr, hr = next(iter(train_loader))
    print(pan.shape, mslr.shape, hr.shape)

    # validation shapes
    pan, mslr, hr = next(iter(validation_loader))
    print(pan.shape, mslr.shape, hr.shape)'''

    channel_sum = 0
    channel_sum_of_squares = 0
    total_samples = 0
    # Iterate over the DataLoader
    print('Length of Dataloader: ', len(tr_dataset))
    for pan, mslr, mshr in tr_dataset:
        # Assuming your data is a tensor
        # Compute the channel-wise mean and mean of squares
        channel_sum += torch.mean(pan, dim=(1, 2))
        channel_sum_of_squares += torch.mean(pan ** 2, dim=(1, 2))

        total_samples += 1

    # Compute the mean and standard deviation for each channel
    mean = channel_sum / total_samples
    std = torch.sqrt((channel_sum_of_squares / total_samples) - mean ** 2)

    print('mean: ', mean, ' std: ', std)
"""


class GaoFen2panformer(Dataset):
    def __init__(self, dir, transforms=None) -> None:
        self.dir = dir
        self.transforms = transforms

        # precomputed
        self.pan_mean = torch.tensor([255.2780]).view(1, 1, 1, 1)
        self.pan_std = torch.tensor([119.8152]).view(1, 1, 1, 1)

        self.mslr_mean = torch.tensor(
            [385.9424, 268.0104, 218.5947, 259.1452]).view(1, 4, 1, 1)
        self.mslr_std = torch.tensor(
            [134.2627, 110.1456, 117.1064, 113.4461]).view(1, 4, 1, 1)

    def __len__(self):
        dt_len = len([name for name in os.listdir(self.dir/'LR')])
        print('dataset len: ',  dt_len)
        return dt_len

    def __getitem__(self, index):

        pan = torch.tensor(
            np.load(self.dir/'PAN'/f'{index:04d}.npy', allow_pickle=True).astype('float32'))
        mslr = torch.tensor(
            np.load(self.dir/'LR'/f'{index:04d}.npy', allow_pickle=True).astype('float32'))
        hr = torch.tensor(
            np.load(self.dir/'HR'/f'{index:04d}.npy', allow_pickle=True).astype('float32'))

        if self.transforms:
            for transform, prob in self.transforms:
                if torch.randn(1) < prob:
                    pan = transform(pan)
                    mslr = transform(mslr)
                    hr = transform(hr)

        return (pan, mslr, hr)  # (None, None, None) #


class Sev2Mod(Dataset):
    def __init__(self, dir, transforms=None) -> None:
        self.dir = dir
        self.transforms = transforms

        # precomputed
        self.pan_mean = torch.tensor([23.2821]).view(1, 1, 1, 1)
        self.pan_std = torch.tensor([12.0762]).view(1, 1, 1, 1)

        self.mslr_mean = torch.tensor(
            [23.1248, 27.3095]).view(1, 2, 1, 1)
        self.mslr_std = torch.tensor(
            [12.4016, 14.5950]).view(1, 2, 1, 1)

    def __len__(self):
        return len([name for name in os.listdir(self.dir/'LR')])

    def __getitem__(self, index):

        try:
            pan = torch.tensor(
                np.load(self.dir/'PAN'/f'{index:04d}_x3.npy', allow_pickle=True))
            mslr = torch.tensor(
                np.load(self.dir/'LR'/f'{index:04d}_x12.npy', allow_pickle=True))
            hr = torch.tensor(
                np.load(self.dir/'HR'/f'{index:04d}_x12.npy', allow_pickle=True))
            if self.transforms:
                for transform, prob in self.transforms:
                    if torch.randn(1) < prob:
                        pan = transform(pan)
                        mslr = transform(mslr)
                        hr = transform(hr)

            return (pan, mslr, hr)
        except:
            return None


if __name__ == "__main__":
    batch_size = 8
    task = 'x12'

    dir_tr = Path(f'/media/nick/INTENSO/Data/SEV2MOD_X12/train/')
    dir_val = Path(f'/media/nick/INTENSO/Data/SEV2MOD_X12/val/')
    dir_test = Path(f'/media/nick/INTENSO/Data/SEV2MOD_X12/test/')

    # Load training dataset
    tr_dataset = Sev2Mod(dir_tr)
    train_loader = DataLoader(
        dataset=tr_dataset, batch_size=batch_size, shuffle=True)

    '''# Load validation dataset
    val_dataset = Sev2Mod(dir_val, task)
    validation_loader = DataLoader(
        dataset=val_dataset, batch_size=batch_size, shuffle=False)

    # Load test dataset
    test_dataset = Sev2Mod(dir_test, task)
    test_loader = DataLoader(
        dataset=test_dataset, batch_size=batch_size, shuffle=False)'''

    channel_sum_mslr = 0
    channel_sum_of_squares_mslr = 0

    channel_sum_pan = 0
    channel_sum_of_squares_pan = 0

    total_samples = 0
    # Iterate over the DataLoader
    print('Length of Dataloader: ', len(train_loader))
    for pan, mslr, mshr in train_loader:
        # Assuming your data is a tensor
        # Compute the channel-wise mean and mean of squares
        channel_sum_mslr += torch.mean(mslr, dim=(0, 2, 3))
        channel_sum_of_squares_mslr += torch.mean(mslr ** 2, dim=(0, 2, 3))

        channel_sum_pan += torch.mean(pan, dim=(0, 2, 3))
        channel_sum_of_squares_pan += torch.mean(pan ** 2, dim=(0, 2, 3))

        total_samples += 1

    # Compute the mean and standard deviation for each channel
    mean_mslr = channel_sum_mslr / total_samples
    std_mslr = torch.sqrt(
        (channel_sum_of_squares_mslr / total_samples) - mean_mslr ** 2)

    # Compute the mean and standard deviation for each channel
    mean_pan = channel_sum_pan / total_samples
    std_pan = torch.sqrt((channel_sum_of_squares_pan /
                         total_samples) - mean_pan ** 2)

    print('mean_mslr: ', mean_mslr, ' std_mslr: ', std_mslr)
    print('mean_pan: ', mean_pan, ' std_pan: ', std_pan)


class WV3(Dataset):
    def __init__(self, dir, transforms=None) -> None:
        f = h5py.File(str(dir), 'r+')
        self.hr = torch.tensor(f['gt'][()][:,:8, :, :], dtype=torch.float32)
        self.mslr = torch.tensor(f['ms'][()][:,:8, :, :], dtype=torch.float32)
        self.pan = torch.tensor(f['pan'][()][:,:, :, :], dtype=torch.float32)
        self.transforms = transforms

        # precomputed
        self.pan_mean = torch.tensor([400.1155]).view(1, 1, 1, 1)
        self.pan_std = torch.tensor([231.4912]).view(1, 1, 1, 1)

        self.mslr_mean = torch.tensor([274.7202, 321.7943, 407.2370, 350.4585, 286.0128, 335.0426, 433.5523, 317.5977]).view(1, 8, 1, 1) 
        self.mslr_std = torch.tensor([76.1222, 125.6397, 205.9311, 221.6230, 210.6218, 182.3110, 224.2404, 163.7575]).view(1, 8, 1, 1) 

    def __len__(self):
        return self.mslr.shape[0]

    def __getitem__(self, index):

        pan = self.pan[index]
        mslr = self.mslr[index]
        hr = self.hr[index]

        if self.transforms:
            for transform, prob in self.transforms:
                if torch.randn(1) < prob:
                    pan = transform(pan)
                    mslr = transform(mslr)
                    hr = transform(hr)

        return (pan, mslr, hr)


"""if __name__ == "__main__":
    batch_size = 1
    shuffle = True

    dir_tr = Path(f'F:/Data/WorldView3/train/train_wv3-001.h5')
    dir_val = Path(f'F:/Data/WorldView3/val/valid_wv3.h5')
    # dir_test = Path(f'F:/Data/GaoFen-2/train/train_gf2-001.h5')

    tr_dataset = GaoFen2(
        dir_tr, transforms=[(RandomHorizontalFlip(1), 0.3), (RandomVerticalFlip(1), 0.3)])
    train_loader = DataLoader(
        dataset=tr_dataset, batch_size=batch_size, shuffle=shuffle)

    val_dataset = GaoFen2(
        dir_val)
    validation_loader = DataLoader(
        dataset=val_dataset, batch_size=batch_size, shuffle=shuffle)

    '''# train shapes
    pan, mslr, hr = next(iter(train_loader))
    print(pan.shape, mslr.shape, hr.shape)

    # validation shapes
    pan, mslr, hr = next(iter(validation_loader))
    print(pan.shape, mslr.shape, hr.shape)'''

    channel_sum = 0
    channel_sum_of_squares = 0
    total_samples = 0
    # Iterate over the DataLoader
    print('Length of Dataloader: ', len(tr_dataset))
    for pan, mslr, mshr in tr_dataset:
        # Assuming your data is a tensor
        # Compute the channel-wise mean and mean of squares
        channel_sum += torch.mean(mslr, dim=(1, 2))
        channel_sum_of_squares += torch.mean(mslr ** 2, dim=(1, 2))

        total_samples += 1

    # Compute the mean and standard deviation for each channel
    mean = channel_sum / total_samples
    std = torch.sqrt((channel_sum_of_squares / total_samples) - mean ** 2)

    print('mean: ', mean, ' std: ', std)"""
