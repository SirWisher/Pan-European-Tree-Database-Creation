import os
import torch
import loading as ld
import numpy as np
from torchvision import transforms

def indexing(lab,x):
    array = np.zeros((x, 34))

    for i in range(x): 
        for label in lab[i]:
            index = int(label) - 1  # Subtract 1 from the label to get the corresponding index
            array[i, index] = 1

    return array.astype(float)

def custom_collate(batch):
    if isinstance(batch[0], torch.Tensor):
        # If the batch element is a tensor, return the stacked tensor
        return torch.stack(batch)
    elif isinstance(batch[0], list):
        # If the batch element is a list, recursively call the collate function on each nested element
        return [custom_collate(samples) for samples in zip(*batch)]
    else:
        # For other types, return the batch as is
        return batch

class ImageDataset(torch.utils.data.Dataset):
    def __init__(self, img_fid3, annotations_file, img_dir, method = 'Pad'):
        self.img_labels = annotations_file
        self.img_dir = img_dir
        self.img_fid3 = img_fid3
        self.num_files = len(img_fid3)
        self.method = method

    def __len__(self):
        return self.num_files
    
    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, 'Sample_Point_Fid3_'+str(self.img_fid3[idx]))
        timeseries = np.array(ld.load_timeseries(img_path, self.method))
        labels = np.expand_dims(np.array(self.img_labels[idx]).astype(int), axis=0)
        transform =  transforms.ToTensor()
        timeseries = torch.from_numpy(timeseries)
        labels = transform(labels)
        sample = {'timeseries': timeseries, 'labels': labels[0]}

        return sample
