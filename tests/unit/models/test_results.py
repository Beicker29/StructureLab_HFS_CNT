from __future__ import annotations

import pytest
from pydantic import ValidationError

from steel_connections.models.diagnostics import DiagnosticLevel, DesignError, DesignWarning
from steel_connections.models.results import CheckStatus, LimitStateResult
from steel_connections.models.units import Quantity


def test_limit_state_result_requires_na_reason() -> None:
    with pytest.raises(ValidationError):
        LimitStateResult(
            name="not applicable check",
            rule_id="TEST.NA",
            clause="test",
            source_document="test",
            status=CheckStatus.NA,
            demand=None,
            capacity=None,
            dcr=None,
            equation="not_applicable",
        )


def test_limit_state_result_keeps_warning_separate_from_check_status() -> None:
    result = LimitStateResult(
        name="sample",
        rule_id="TEST.OK",
        clause="test",
        source_document="test",
        status=CheckStatus.OK,
        demand=Quantity(value=10.0, unit="kN"),
        capacity=Quantity(value=20.0, unit="kN"),
        dcr=0.5,
        equation="demand / capacity",
        warnings=[DesignWarning(message="review note")],
        errors=[],
    )

    assert result.status == CheckStatus.OK
    assert result.warnings[0].level == DiagnosticLevel.WARNING
    assert not hasattr(CheckStatus, "WARNING")


def test_design_error_is_structured_diagnostic() -> None:
    error = DesignError(
        error_code="MISSING_REQUIRED_INPUT",
        stage="evaluate",
        rule_id="TEST.ERROR",
        missing_fields=["geometry.x"],
        message="Missing geometry.x",
        source_document="test source",
    )

    assert error.level == DiagnosticLevel.ERROR
    assert error.missing_fields == ["geometry.x"]
