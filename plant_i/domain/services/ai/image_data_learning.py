import os
import torch
from torch.utils.data import DataLoader, Dataset
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import torch.optim as optim

class PCBDataSet(Dataset):
    def __init__(self, directory, transform=None):
        self.directory = directory
        self.transform = transform
        self.labels = {'good': 0, 'type1': 1, 'type2': 2, 'type3': 3, 'type4': 4, 'type5': 5, 'type6': 6}
        self.images = []
        self.image_labels = []

        # 불량 유형별로 디렉토리를 순회하며 이미지 파일과 레이블을 수집
        for label in self.labels:
            dir_path = os.path.join(self.directory, label)
            if os.path.isdir(dir_path):
                for file in os.listdir(dir_path):
                    if file.endswith(('.png', '.jpg', '.jpeg')):
                        self.images.append(os.path.join(dir_path, file))
                        self.image_labels.append(self.labels[label])
    
    def __len__(self):
        # 데이터셋의 총 이미지 수 반환
        return len(self.images)
    
    def __getitem__(self, idx):
        # 인덱스에 해당하는 이미지를 로드하고, 전처리 수행
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB') # RGB 형식으로 이미지 변환
        if self.transform:
            image = self.transform(image)
        label = self.image_labels[idx]
        return image, label
    

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 32 * 32, 512)
        self.fc2 = nn.Linear(512, 2)
        
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 64 * 32 * 32)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class ImageDataLearningService():
    model = SimpleCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    def __init__(self):
        pass

    def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=25):
        for epoch in range(num_epochs):
            model.train()
            running_loss = 0.0
            for images, labels in train_loader:
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
            print(f'Epoch {epoch+1}, Loss: {running_loss/len(train_loader)}')
        
            # 검증 과정
            model.eval()
            val_loss = 0.0
            correct = 0
            total = 0
            with torch.no_grad():
                for images, labels in val_loader:
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    val_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
            print(f'Validation Loss: {val_loss/len(val_loader)}, Accuracy: {100 * correct / total}%')


    
 