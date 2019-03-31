import torch
import torchvision
import torchvision.transforms as transforms


def load_data(images_path):
    transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    dataset = torchvision.datasets.ImageFolder(images_path, transform)
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=1,
                                              shuffle=True)

    return iter(data_loader)
