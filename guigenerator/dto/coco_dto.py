from typing import List


class CocoDto:
    def __init__(self, licenses: List['LicenseDto'], info: 'InfoDto',
                 categories: List['CategoryDto'], images: List['ImageDto'],
                 annotations: List['AnnotationDto']):
        self.licenses = licenses
        self.info = info
        self.categories = categories
        self.images = images
        self.annotations = annotations


class LicenseDto:
    def __init__(self, name="", id_=0, url=""):
        self.name = name
        self.id = id_
        self.url = url


class InfoDto:
    def __init__(self, contributor="", date_created="", description="", url="",
                 version="", year=""):
        self.contributor = contributor
        self.date_created = date_created
        self.description = description
        self.url = url
        self.version = version
        self.year = year


class CategoryDto:
    def __init__(self, id_, name, supercategory=""):
        self.id = id_
        self.name = name
        self.supercategory = supercategory


class ImageDto:
    def __init__(self, id_, width: int, height: int, file_name,
                 license_=0, flickr_url="", coco_url="", date_captured=0):
        self.id = id_
        self.width = width
        self.height = height
        self.file_name = file_name
        self.license = license_
        self.flickr_url = flickr_url
        self.coco_url = coco_url
        self.date_captured = date_captured


class AnnotationDto:
    def __init__(self, id_: int, image_id: int, category_id: int,
                 bbox: List[float], area: float = -1, iscrowd: int = 0,
                 segmentation: list = None, attributes: dict = None):
        if segmentation is None:
            segmentation = []
        if area == -1:
            area = bbox[2] * bbox[3]
        if attributes is None:
            attributes = {
                "occluded": False
            }
        if "occluded" not in attributes.keys():
            attributes["occluded"] = False

        self.id = id_
        self.image_id = image_id
        self.category_id = category_id
        self.segmentation = segmentation
        self.area = area
        self.bbox = bbox
        self.iscrowd = iscrowd
        self.attributes = attributes


class LabelInputLinksDto(object):
    def __init__(self, links: List['LabelInputDto']):
        self.links = links


class LabelInputDto(object):
    def __init__(self, image_id: int, label_id: int, input_id: int):
        self.image_id = image_id
        self.label_id = label_id
        self.input_id = input_id
