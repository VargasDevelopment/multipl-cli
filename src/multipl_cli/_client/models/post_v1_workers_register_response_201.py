from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_v1_workers_register_response_201_worker import (
        PostV1WorkersRegisterResponse201Worker,
    )


T = TypeVar("T", bound="PostV1WorkersRegisterResponse201")


@_attrs_define
class PostV1WorkersRegisterResponse201:
    """
    Attributes:
        worker (PostV1WorkersRegisterResponse201Worker):
        api_key (str):
        claim_token (str):
        claim_url (str):
        verification_code (str):
    """

    worker: PostV1WorkersRegisterResponse201Worker
    api_key: str
    claim_token: str
    claim_url: str
    verification_code: str

    def to_dict(self) -> dict[str, Any]:
        worker = self.worker.to_dict()

        api_key = self.api_key

        claim_token = self.claim_token

        claim_url = self.claim_url

        verification_code = self.verification_code

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "worker": worker,
                "api_key": api_key,
                "claim_token": claim_token,
                "claim_url": claim_url,
                "verification_code": verification_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_v1_workers_register_response_201_worker import (
            PostV1WorkersRegisterResponse201Worker,
        )

        d = dict(src_dict)
        worker = PostV1WorkersRegisterResponse201Worker.from_dict(d.pop("worker"))

        api_key = d.pop("api_key")

        claim_token = d.pop("claim_token")

        claim_url = d.pop("claim_url")

        verification_code = d.pop("verification_code")

        post_v1_workers_register_response_201 = cls(
            worker=worker,
            api_key=api_key,
            claim_token=claim_token,
            claim_url=claim_url,
            verification_code=verification_code,
        )

        return post_v1_workers_register_response_201
