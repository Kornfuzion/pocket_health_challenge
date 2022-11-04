from typing import Dict, Any, Set, Optional, List
import pydicom
import base64
from pydicom.tag import Tag


class DicomAttributeExtractor:
    PIXEL_DATA_TAG_KEY: str = "0x7fe00010"
    TRAILING_PADDING_TAG_KEY: str = "0xfffcfffc"
    HISTOGRAM_TABLE_TAG_KEY: str = "0x00431029"
    UNIQUE_IMAGE_ID_TAG_KEY: str = "0x00431028"
    USER_DEFINED_DATA_TAG_KEY: str = "0x0043102a"

    BINARY_DATA_TAGS: Set[str] = {
        PIXEL_DATA_TAG_KEY, 
        TRAILING_PADDING_TAG_KEY, 
        HISTOGRAM_TABLE_TAG_KEY,
        UNIQUE_IMAGE_ID_TAG_KEY,
        USER_DEFINED_DATA_TAG_KEY,
    }

    @classmethod
    def serialize_body(cls, tag_key: str, value: Any) -> Dict[str, Any]:
        # Base64 encode + utf-8 decode to safely transmit binary via json
        if tag_key in cls.BINARY_DATA_TAGS:
            return base64.b64encode(value).decode("utf-8")
        else:
            return str(value)

    @classmethod
    def get_json_body(cls, tag_key: str, element: pydicom.dataelem.DataElement) -> Dict[str, Any]:
        return {
            "VR": element.VR,
            "name": element.name,
            "value": cls.serialize_body(tag_key, element.value),
        }

    @classmethod
    def validate_tag_keys(cls, tag_keys: List[str]) -> bool:
        try:
            [Tag(tag_key) for tag_key in tag_keys]
        except Exception:
            return False
        return True

    @classmethod
    def get_zero_padded_hex(cls, value: int) -> str:
        return "{0:#0{1}x}".format(value, 6)

    @classmethod
    def get_tag_key_from_tag(cls, tag: Tag) -> str:
        return cls.get_zero_padded_hex(tag.group) + cls.get_zero_padded_hex(tag.elem)[2:]

    @classmethod
    def extract_dicom_attributes(cls, file_path: str, tag_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        dcm = pydicom.dcmread(file_path)
        attributes = {}
        for element in dcm:
            tag_key = cls.get_tag_key_from_tag(element.tag)
            if not tag_keys or tag_key in tag_keys:
                attributes[tag_key] = cls.get_json_body(tag_key, element)
        return attributes
        