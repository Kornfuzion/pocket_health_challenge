from typing import Dict, Any, Set, Optional
import pydicom
import base64
from pydicom.tag import Tag


class DicomAttributeExtractor:
    @classmethod
    def serialize_body(cls, value: Any) -> Dict[str, Any]:
        # Base64 encode + utf-8 decode to safely transmit binary via json
        if isinstance(value, (bytes, bytearray)):
            return base64.b64encode(value).decode("utf-8")
        else:
            return str(value)

    @classmethod
    def get_json_body(cls, element: pydicom.dataelem.DataElement) -> Dict[str, Any]:
        return {
            "VR": element.VR,
            "name": element.name,
            "value": cls.serialize_body(element.value),
        }

    @classmethod
    def validate_tag_keys(cls, tag_keys: Set[str]) -> bool:
        try:
            [Tag(tag_key) for tag_key in tag_keys]
        except Exception:
            return False
        return True

    @classmethod
    def get_zero_padded_hex(cls, value: int) -> str:
        # Produce hex code resembling: 0x0005
        return "{0:#0{1}x}".format(value, 6)

    @classmethod
    def get_tag_key_from_tag(cls, tag: Tag) -> str:
        return cls.get_zero_padded_hex(tag.group) + cls.get_zero_padded_hex(tag.elem)[2:]

    @classmethod
    def extract_dicom_attributes(cls, file_path: str, tag_keys: Set[str]) -> Dict[str, Any]:
        dcm = pydicom.dcmread(file_path)
        attributes = {}
        for element in dcm:
            tag_key = cls.get_tag_key_from_tag(element.tag)
            if not tag_keys or tag_key in tag_keys:
                attributes[tag_key] = cls.get_json_body(element)
        return attributes
        