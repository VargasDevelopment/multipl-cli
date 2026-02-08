from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_v1x402_verify_response_200_kind import GetV1X402VerifyResponse200Kind
from ..models.get_v1x402_verify_response_200_service import GetV1X402VerifyResponse200Service
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_v1x402_verify_response_200_api import GetV1X402VerifyResponse200Api
    from ..models.get_v1x402_verify_response_200_economics import (
        GetV1X402VerifyResponse200Economics,
    )
    from ..models.get_v1x402_verify_response_200_links import GetV1X402VerifyResponse200Links


T = TypeVar("T", bound="GetV1X402VerifyResponse200")


@_attrs_define
class GetV1X402VerifyResponse200:
    """
    Attributes:
        ok (bool):
        kind (GetV1X402VerifyResponse200Kind):
        service (GetV1X402VerifyResponse200Service):
        tagline (str):
        summary (str):
        economics (GetV1X402VerifyResponse200Economics):
        links (GetV1X402VerifyResponse200Links):
        api (GetV1X402VerifyResponse200Api):
        getting_started (list[str] | Unset):
    """

    ok: bool
    kind: GetV1X402VerifyResponse200Kind
    service: GetV1X402VerifyResponse200Service
    tagline: str
    summary: str
    economics: GetV1X402VerifyResponse200Economics
    links: GetV1X402VerifyResponse200Links
    api: GetV1X402VerifyResponse200Api
    getting_started: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        kind = self.kind.value

        service = self.service.value

        tagline = self.tagline

        summary = self.summary

        economics = self.economics.to_dict()

        links = self.links.to_dict()

        api = self.api.to_dict()

        getting_started: list[str] | Unset = UNSET
        if not isinstance(self.getting_started, Unset):
            getting_started = self.getting_started

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "kind": kind,
                "service": service,
                "tagline": tagline,
                "summary": summary,
                "economics": economics,
                "links": links,
                "api": api,
            }
        )
        if getting_started is not UNSET:
            field_dict["getting_started"] = getting_started

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_v1x402_verify_response_200_api import GetV1X402VerifyResponse200Api
        from ..models.get_v1x402_verify_response_200_economics import (
            GetV1X402VerifyResponse200Economics,
        )
        from ..models.get_v1x402_verify_response_200_links import GetV1X402VerifyResponse200Links

        d = dict(src_dict)
        ok = d.pop("ok")

        kind = GetV1X402VerifyResponse200Kind(d.pop("kind"))

        service = GetV1X402VerifyResponse200Service(d.pop("service"))

        tagline = d.pop("tagline")

        summary = d.pop("summary")

        economics = GetV1X402VerifyResponse200Economics.from_dict(d.pop("economics"))

        links = GetV1X402VerifyResponse200Links.from_dict(d.pop("links"))

        api = GetV1X402VerifyResponse200Api.from_dict(d.pop("api"))

        getting_started = cast(list[str], d.pop("getting_started", UNSET))

        get_v1x402_verify_response_200 = cls(
            ok=ok,
            kind=kind,
            service=service,
            tagline=tagline,
            summary=summary,
            economics=economics,
            links=links,
            api=api,
            getting_started=getting_started,
        )

        return get_v1x402_verify_response_200
