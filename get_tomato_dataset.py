import os
import requests
import zipfile
import shutil
import json
import glob

# Define paths
zip_url = "http://assets.laboro.ai.s3.amazonaws.com/laborotomato/laboro_tomato.zip"
zip_path = "laboro_tomato.zip"
unzip_dir = "/app/yolov8/dataset"
laboro_tomato_dir = os.path.join(unzip_dir, 'laboro_tomato')
train_label_dir = "dataset/labels/train"
val_label_dir = "dataset/labels/val"
train_image_dir = "dataset/images/train"
val_image_dir = "dataset/images/val"
annotations_dir = "dataset/laboro_tomato/annotations/"
train_annotation_file = os.path.join(annotations_dir, 'train.json')
val_annotation_file = os.path.join(annotations_dir, 'test.json')

def coco_to_yolo(coco_annotation_path, output_dir, image_dir):
    # Load COCO annotations
    with open(coco_annotation_path, 'r') as f:
        coco_data = json.load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Map category IDs to a zero-based index for YOLO
    categories = {cat['id']: idx for idx, cat in enumerate(coco_data['categories'])}

    # Process each image
    for img in coco_data['images']:
        img_id = img['id']
        img_file_name = img['file_name']
        img_width = img['width']
        img_height = img['height']

        # Prepare annotation file
        yolo_file_path = os.path.join(output_dir, f"{os.path.splitext(img_file_name)[0]}.txt")
        with open(yolo_file_path, 'w') as yolo_file:
            # Get annotations for this image
            annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == img_id]
            for ann in annotations:
                bbox = ann['bbox']  # COCO bbox format: [x_min, y_min, width, height]
                x_min, y_min, width, height = bbox
                x_center = (x_min + width / 2) / img_width
                y_center = (y_min + height / 2) / img_height
                norm_width = width / img_width
                norm_height = height / img_height

                class_id = categories[ann['category_id']]
                yolo_file.write(f"{class_id} {x_center} {y_center} {norm_width} {norm_height}\n")

    print("Conversion complete!")


# Download the zip file
print("Downloading the laboro_tomato dataset...")
response = requests.get(zip_url)
response.raise_for_status()  # Ensure we notice bad responses
with open(zip_path, 'wb') as f:
    f.write(response.content)
print("Download completed.")

# Unzip the file
print("Unzipping the dataset...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(unzip_dir)
print("Unzipping completed.")

# Create directories
print("Setting up directory structure...")
os.makedirs(train_label_dir, exist_ok=True)
os.makedirs(val_label_dir, exist_ok=True)
os.makedirs(train_image_dir, exist_ok=True)
os.makedirs(val_image_dir, exist_ok=True)
print("Directory structure set up.")

# Move image files to the correct directories
print("Organizing images...")
for img_file in glob.glob(os.path.join(laboro_tomato_dir, 'train', '*.jpg')):
    shutil.move(img_file, train_image_dir)

for img_file in glob.glob(os.path.join(laboro_tomato_dir, 'test', '*.jpg')):
    shutil.move(img_file, val_image_dir)
print("Image organization completed.")

# Convert annotations
print("Converting train annotations")
coco_to_yolo(
    train_annotation_file, 
    train_label_dir, 
    train_image_dir)
print("Converting test(val) annotations")
coco_to_yolo(
    val_annotation_file, 
    val_label_dir, 
    val_image_dir)

# Delete the zip file
print("Cleaning up the zip file...")
os.remove(zip_path)
print("Zip file deleted.")

# Delete the unzipped dataset directory
print("Cleaning up the extracted dataset directory...")
shutil.rmtree(laboro_tomato_dir)
print("Extracted dataset directory deleted.")

print("All tasks completed successfully.")