import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
from torch.utils.data import DataLoader


class Images(torch.utils.data.Dataset):
    def __init__(self, paths, size):
        self.paths = paths
        self.transform = T.Compose([
            T.ToTensor(),
            T.Resize(size, interpolation=T.InterpolationMode.BICUBIC, antialias=True),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def __getitem__(self, i):
        return self.transform(Image.open(self.paths[i]).convert("RGB"))

    def __len__(self):
        return len(self.paths)


def boq():
    model = torch.hub.load("amaralibey/bag-of-queries", "get_trained_boq",
                           backbone_name="dinov2", output_dim=12288)
    return lambda x: model(x)[0], model, (322, 322), 48


def megaloc():
    model = torch.hub.load("gmberton/MegaLoc", "get_trained_model")
    return model, model, (518, 518), 24


METHODS = {"boq": boq, "megaloc": megaloc}


class Method:
    def __init__(self, name, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.forward, model, self.size, self.batch_size = METHODS[name]()
        self.device = device
        model.to(device).eval()

    @torch.no_grad()
    def __call__(self, paths, num_workers=8):
        loader = DataLoader(Images(paths, self.size), batch_size=self.batch_size,
                            num_workers=num_workers)
        return np.concatenate([self.forward(x.to(self.device)).cpu().numpy() for x in loader])
