"""Marshmallow schema definitions

This module contains marshmallow schemas responsible for
serializing/deserializing request and response objects
"""
from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    post_load,
    validate,
    validates,
)

from .config import DOCUMENT_SIZE_THRESHOLD_BYTES
from .models import Detail, Match, PolicyBreak, ScanResult


class DocumentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    filename = fields.Str(validate=validate.Length(max=256))
    document = fields.Str(required=True)

    @validates("document")
    def validate_document(self, document: str) -> str:
        """
        validate that document is smaller than scan limit
        """
        encoded = document.encode("utf-8")
        if len(encoded) > DOCUMENT_SIZE_THRESHOLD_BYTES:
            raise ValidationError(
                "file exceeds the maximum allowed size of {}B".format(
                    DOCUMENT_SIZE_THRESHOLD_BYTES
                )
            )

        if "\x00" in document:
            raise ValidationError("document has null characters")

        return document


class MatchSchema(Schema):
    match = fields.Str(required=True)
    match_type = fields.Str(data_key="type", required=True)
    line_start = fields.Int(allow_none=True)
    line_end = fields.Int(allow_none=True)
    index_start = fields.Int(allow_none=True)
    index_end = fields.Int(allow_none=True)

    @post_load
    def make_match(self, data, **kwargs):
        return Match(**data)


class PolicyBreakSchema(Schema):
    break_type = fields.Str(data_key="type", required=True)
    policy = fields.Str(required=True)
    matches = fields.List(fields.Nested(MatchSchema), required=True)

    @post_load
    def make_policy_break(self, data, **kwargs):
        return PolicyBreak(**data)


class ScanResultSchema(Schema):
    policy_break_count = fields.Integer(required=True)
    policies = fields.List(fields.Str(), required=True)
    policy_breaks = fields.List(fields.Nested(PolicyBreakSchema), required=True)

    @post_load
    def make_scan_result(self, data, **kwargs):
        return ScanResult(**data)


class DetailSchema(Schema):
    detail = fields.Str(required=True)

    @post_load
    def make_detail_response(self, data, **kwargs):
        return Detail(**data)