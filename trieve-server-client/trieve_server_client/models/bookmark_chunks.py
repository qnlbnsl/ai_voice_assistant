from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, List
from typing import cast
from typing import Dict

if TYPE_CHECKING:
  from ..models.chunk_metadata_with_file_data import ChunkMetadataWithFileData





T = TypeVar("T", bound="BookmarkChunks")


@_attrs_define
class BookmarkChunks:
    """ 
        Attributes:
            metadata (List['ChunkMetadataWithFileData']):
     """

    metadata: List['ChunkMetadataWithFileData']
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.chunk_metadata_with_file_data import ChunkMetadataWithFileData
        metadata = []
        for metadata_item_data in self.metadata:
            metadata_item = metadata_item_data.to_dict()
            metadata.append(metadata_item)






        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "metadata": metadata,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.chunk_metadata_with_file_data import ChunkMetadataWithFileData
        d = src_dict.copy()
        metadata = []
        _metadata = d.pop("metadata")
        for metadata_item_data in (_metadata):
            metadata_item = ChunkMetadataWithFileData.from_dict(metadata_item_data)



            metadata.append(metadata_item)


        bookmark_chunks = cls(
            metadata=metadata,
        )

        bookmark_chunks.additional_properties = d
        return bookmark_chunks

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