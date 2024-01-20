from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="EditMessageData")


@_attrs_define
class EditMessageData:
    """ 
        Attributes:
            message_sort_order (int):
            new_message_content (str):
            topic_id (str):
     """

    message_sort_order: int
    new_message_content: str
    topic_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        message_sort_order = self.message_sort_order

        new_message_content = self.new_message_content

        topic_id = self.topic_id


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "message_sort_order": message_sort_order,
            "new_message_content": new_message_content,
            "topic_id": topic_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        message_sort_order = d.pop("message_sort_order")

        new_message_content = d.pop("new_message_content")

        topic_id = d.pop("topic_id")

        edit_message_data = cls(
            message_sort_order=message_sort_order,
            new_message_content=new_message_content,
            topic_id=topic_id,
        )

        edit_message_data.additional_properties = d
        return edit_message_data

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties