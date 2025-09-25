import cv2
import itertools
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import random
from PIL import Image

from itertools import groupby
from skimage import io
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# Based on https://www.kaggle.com/code/alejopaullier/how-to-create-a-coco-dataset
def create_coco_format_json(data_frame, classes, filepaths):
    """
    This function creates a COCO dataset.
    :param data_frame: pandas dataframe with an "id" column.
    :param classes: list of strings where each string is a class.
    :param filepaths: a list of strings containing all images paths
    :return dataset_coco_format: COCO dataset (JSON).
    """
    images = []
    annotations = []
    categories = []
    count = 0

    categories.append(
        { 
            "id": "0",
            "name": "background"
        }
    )

    # Creates a categories list, i.e: [{'id': 0, 'name': 'a'}, {'id': 1, 'name': 'b'}, {'id': 2, 'name': 'c'}] 
    for idx, class_ in enumerate(classes):
        categories.append(
            { 
                "id": str(idx+1),
                "name": class_
            }
        )
    
    # Iterate over image filepaths
    for filepath in tqdm(filepaths):
        file_name = filepath.split("/")[-1]
        file_id = file_name.split('.')[0]
        image = Image.open(filepath)
        width, height = image.size

        ids = data_frame.index[data_frame['filename'] == file_name].tolist()

        for bbi in ids:
            bb = data_frame.iloc[bbi]
            
            # Adding images which has annotations
            images.append(
                {
                    "id": count,
                    "width": width,
                    "height": height,
                    "file_name": file_name
                }
            )

            print(bb)
    
            seg = {
                'bbox': [str(bb["xmin"]), str(bb["xmax"]), str(bb["ymin"]), str(bb["ymax"])],
                'image_id': str(file_id), 
                'category_id':classes.index(data_frame.iloc[idx]['class']), 
            }
            annotations.append(seg)
            count +=1
    
    # Create the dataset
    dataset_coco_format = {
        "categories": categories,
        "images": images,
        "annotations": annotations,
    }

    print(dataset_coco_format)
    
    return dataset_coco_format

def sep():
    print("-"*100)

# Setting the paths.
DATASET_PATH = "./data/dataset/"
IMAGE_DIR = DATASET_PATH + "images/"
CSV_PATH = DATASET_PATH + "labels/annotations.csv"

# Creating a dataframe.
df = pd.read_csv(CSV_PATH, sep=',')
train, test = train_test_split(df, test_size=10)
print(df.head())

print(train.head())
print(test.head())

print("Number of Train Images:{}".format(len(train)))
print("Number of Test Images:{}".format(len(test)))

# Set classes
classes = df["class"].unique().tolist()

# Get list with all image file paths
filepaths = list()
for (dirpath, dirnames, filenames) in os.walk(DATASET_PATH):
    filepaths += [os.path.join(dirpath, file) for file in filenames if file.endswith(".jpg")]

filepaths_train = ["data/dataset/images/"+t for t in train['filename'].tolist()]
filepaths_test = ["data/dataset/images/"+t for t in test['filename'].tolist()]

# Create COCO Datasets
train_json = create_coco_format_json(train, classes, filepaths_train)

with open('data/dataset/train.json', 'w', encoding='utf-8') as f:
    json.dump(train_json, f, indent=4)

# val_json = create_coco_format_json(test, classes, filepaths)

# with open('data/dataset/val.json', 'w', encoding='utf-8') as f:
#     json.dump(val_json, f, indent=4)
