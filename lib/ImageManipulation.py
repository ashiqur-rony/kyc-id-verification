"""
Image Manipulation Detection Model
Trained on the Image Tampering Detection Dataset: https://www.kaggle.com/code/ghumkumar/image-manipulation-detection-model
@author: Ashiqur Rahman
"""
from torch import nn
import torch.nn.functional as F


class ImageTamperingDetection(nn.Module):

    def __init__(self):
        """
        Initializes the layers of the CNN model.
        Input images are expected to be 256x256 RGB (3 channels).
        Output is a single logit value for binary classification.
        """

        super().__init__()

        # Convolutional Layer 1
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, stride=1, padding=1)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)  # Output: 16 x 128 x 128

        # Convolutional Layer 2
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)  # Output: 32 x 64 x 64

        # Convolutional Layer 3
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)  # Output: 64 x 32 x 32

        # Convolutional Layer 4
        self.conv4 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1)
        self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)  # Output: 128 x 16 x 16

        # Flatten the output for the fully connected layers
        self.flattened_size = 128 * 16 * 16  # 32768

        # Fully Connected Layer 1
        self.fc1 = nn.Linear(in_features=self.flattened_size, out_features=512)

        # Dropout layer
        self.dropout = nn.Dropout(p=0.5)

        # Fully Connected Layer 2 (Output Layer)
        self.fc2 = nn.Linear(in_features=512, out_features=1)  # Output 1 logit

    def forward(self, x):
        """
        Defines the forward pass of the model.
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, 3, 256, 256)
        Returns:
            torch.Tensor: Output tensor of shape (batch_size, 1) containing logits.
        """
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = self.pool3(F.relu(self.conv3(x)))
        x = self.pool4(F.relu(self.conv4(x)))

        x = x.view(-1, self.flattened_size)  # Flatten

        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)  # Output logits
        return x
