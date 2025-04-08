"""
This file detects the forgery using ELA and a pre-trained model (#2 of the workflow).
To run the test, set absolute path of the image in the image_path variable
at line 88 and run the file.
We need PyTorch for the model. The file also depends on
lib/ImageModels.py and lib/model/model_im1.pth.

Run the file using the command:
> python test_image.py
"""
import torch
import numpy as np
from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance
from PIL.ExifTags import TAGS
import os
from lib.ImageModels import IMDModel


def findMetadata(img_path):
    img = Image.open(img_path)
    flag = 0
    try:
        info = img._getexif()
        for (tag, value) in info.items():
            if "Software" == TAGS.get(tag, tag):  # checking for software traces
                print("Found Software Traces...")
                print("Software Signature: ", value)
                flag = 1
        if flag == 0:
            print("No Softare Signature Found. Seems like real image...")

    except Exception as e:
        print('Failed to load metadata', e)


def ELA(img_path):
    DIR = "temp/"
    TEMP = DIR + "temp.jpg"
    original = Image.open(img_path)

    if original.mode != 'RGB':
        original = original.convert('RGB')

    if (os.path.isdir(DIR) == False):
        os.mkdir(DIR)
    original.save(TEMP, quality=90)
    temporary = Image.open(TEMP)
    diff = ImageChops.difference(original, temporary)

    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    SCALE = 255.0/max_diff

    diff = ImageEnhance.Brightness(diff).enhance(SCALE)

    # d = diff.load()
    # WIDTH, HEIGHT = diff.size
    # for x in range(WIDTH):
    #     for y in range(HEIGHT):
    #         d[x, y] = tuple(k * SCALE for k in d[x, y])

    diff.save(DIR + "ela_img.jpg")


def infer(img_path, model, device):
    print("Performing Level 1 analysis...")
    findMetadata(img_path=img_path)

    print("Performing Level 2 analysis...")
    ELA(img_path=img_path)

    img = Image.open("temp/ela_img.jpg")
    img = img.resize((128, 128))
    img = np.array(img, dtype=np.float32).transpose(2, 0, 1) / 255.0
    img = np.expand_dims(img, axis=0)

    out = model(torch.from_numpy(img).to(device=device))
    print(out.detach().cpu().numpy())
    print(torch.max(out, dim=1))
    print(torch.max(out, dim=1)[1])
    y_pred = torch.max(out, dim=1)[1]

    print("Prediction:", end=' ')
    print("Authentic" if y_pred else "Tampared")  # auth -> 1 and tp -> 0
    return 1 if y_pred else 0


if __name__ == '__main__':
    # Load the image
    # image_path = r'C:/Work/id-match/source_files/passport/images/2.png'
    # image_path = r'C:/Work/id-match/source_files/id_cards/5.jpg'
    image_path = r'C:/Work/id-match/source_files/id_cards/7.png'
    # image_path = r'C:/Work/id-match/source_files/id_cards/8.jpg'
    image = Image.open(image_path)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model_path = 'lib/model/model_im1.pth'
    model = torch.load(model_path, map_location=device)

    level_1_analysis = infer(model=model, img_path=image_path, device=device)
