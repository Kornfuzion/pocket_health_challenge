from typing import Dict, Any, Set, Optional
import pydicom
import base64


class DicomAttributeExtractor:
    PIXEL_DATA_TAG_KEY: str = "(7fe0,0010)"
    TRAILING_PADDING_TAG_KEY: str = "(fffc,fffc)"
    HISTOGRAM_TABLE_TAG_KEY: str = "(0043,1029)"
    UNIQUE_IMAGE_ID_TAG_KEY: str = "(0043,1028)"
    USER_DEFINED_DATA_TAG_KEY: str = "(0043,102a)"

    BINARY_DATA_TAGS: Set[str] = {
        PIXEL_DATA_TAG_KEY, 
        TRAILING_PADDING_TAG_KEY, 
        HISTOGRAM_TABLE_TAG_KEY,
        UNIQUE_IMAGE_ID_TAG_KEY,
        USER_DEFINED_DATA_TAG_KEY,
    }

    @classmethod
    def serialize_body(cls, tag_key: str, value: Any) -> Dict[str, Any]:
        # Base64 encode + utf-8 decode to binary safely transmit in json format
        if tag_key in cls.BINARY_DATA_TAGS:
            return base64.b64encode(value).decode('utf-8')
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
    def get_tag_key(cls, tag: pydicom.tag.BaseTag) -> str:
        return str(tag).replace(" ", "")

    @classmethod
    def extract_dicom_attributes(cls, file_path: str, tags: Optional[Set[str]] = None) -> Dict[str, Any]:
        dcm = pydicom.dcmread(file_path)
        attributes = {}
        for element in dcm:
            tag_key = cls.get_tag_key(element.tag)
            if not tags or tag_key in tags:
                attributes[tag_key] = cls.get_json_body(tag_key, element)
        return attributes
        