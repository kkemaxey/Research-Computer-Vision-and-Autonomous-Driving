import random
import shutil
from pathlib import Path

ROOT = Path('.')
VALIDATION_SET_FRACTION = .2
SEED = 42

original_photos = ROOT / 'pictures'


if not original_photos.is_dir():
    raise SystemExit("Couldn't find 'pictures' directory in current directory")


val_img_dir = ROOT / "validation_images"
train_img_dir = ROOT / "training_images"

val_img_dir.mkdir(parents=True, exist_ok=True)
train_img_dir.mkdir(parents=True, exist_ok=True)


original_photos_sorted = sorted(p for p in original_photos.iterdir() if p.suffix.lower() == ".jpg")


random.seed(SEED)
random.shuffle(original_photos_sorted)

val_img_num = round(len(original_photos_sorted) * VALIDATION_SET_FRACTION)

val_imgs = original_photos_sorted[:val_img_num]
training_imgs = original_photos_sorted[val_img_num:]

for img in val_imgs:    
    shutil.move(img, val_img_dir)

for img in training_imgs:
    shutil.move(img, train_img_dir)






