# Download the COCO 2017 dataset and export it in YOLOv5 format
# Only specific classes that I think will be relevant for my project are exported

import fiftyone as fo
import fiftyone.zoo as foz

dataset = foz.load_zoo_dataset(
    "coco-2017",
    label_types=["detections"],
    classes=["person", "car", "bicycle", "motorcycle", "truck", "cat", "dog", "bird"],
)


export_dir = "C:\\Users\Felix\Desktop\Camera\\rtsp-object-detection\\train\datasets"
splits = ["train", "validation", "test"]
label_types = ["detections"]
label_field="ground_truth"
classes = ["person", "car", "bicycle", "motorcycle", "truck", "cat", "dog", "bird"]
# for split in splits:
#     split_view = dataset.
#     split_view.export(
#         export_dir,
#         dataset_type=fo.types.COCODetectionDataset,
#         label_field="detections",
#         split=split,
#         classes=classes,
#     )

for split in splits:
    split_view = dataset.match_tags(split)
    split_view.export(
        export_dir = export_dir,
        dataset_type=fo.types.YOLOv5Dataset,
        label_field=label_field,
        split=split,
        classes=classes,
    )