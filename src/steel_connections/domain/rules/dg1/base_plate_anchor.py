from __future__ import annotations

from steel_connections.models.errors import not_implemented_error
from steel_connections.models.input import DG1BasePlateCase


def run(case: DG1BasePlateCase, rule_binding: object) -> None:
    _ = case
    raise not_implemented_error(
        rule_id=rule_binding.rule_id,
        source_document=rule_binding.source_document,
        message=(
            "Applicable DG1 rule is not implemented yet. "
            "This repository fails hard for applicable NOT_IMPLEMENTED rules."
        ),
    )
