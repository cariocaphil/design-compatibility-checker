import pytest
from pydantic import ValidationError

from app.schemas.compatibility import (
    CompatibilityAssessment,
    CompatibilitySummary,
    CustomImplementationWarning,
    ElementMapping,
    GroupMapping,
    LayoutMapping,
    SemanticImplementationMapping,
)


def _summary(**overrides: object) -> CompatibilitySummary:
    defaults: dict[str, object] = {
        "compatibility_score": 80.0,
        "customization_effort": "minor",
        "overall_compatibility": "Mostly achievable with standard MUI components",
        "confidence": 0.85,
    }
    defaults.update(overrides)
    return CompatibilitySummary(**defaults)


def test_compatibility_summary_requires_all_core_fields() -> None:
    with pytest.raises(ValidationError):
        CompatibilitySummary(compatibility_score=80.0, customization_effort="minor")


@pytest.mark.parametrize("score", [0.0, 100.0])
def test_compatibility_score_accepts_boundary_values(score: float) -> None:
    _summary(compatibility_score=score)


@pytest.mark.parametrize("score", [-1.0, 101.0])
def test_compatibility_score_rejects_out_of_range_values(score: float) -> None:
    with pytest.raises(ValidationError):
        _summary(compatibility_score=score)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_compatibility_summary_confidence_rejects_out_of_range_values(confidence: float) -> None:
    with pytest.raises(ValidationError):
        _summary(confidence=confidence)


def test_compatibility_summary_rejects_invalid_customization_effort_literal() -> None:
    with pytest.raises(ValidationError):
        _summary(customization_effort="extreme")


def test_custom_implementation_warning_rejects_invalid_severity_literal() -> None:
    with pytest.raises(ValidationError):
        CustomImplementationWarning(
            target="hero-carousel", reason="No MUI equivalent", severity="critical"
        )


def test_custom_implementation_warning_accepts_known_severities() -> None:
    warning = CustomImplementationWarning(
        target="hero-carousel", reason="No MUI equivalent", severity="high"
    )

    assert warning.severity == "high"


def test_compatibility_assessment_defaults_all_lists_to_empty() -> None:
    assessment = CompatibilityAssessment(summary=_summary())

    assert assessment.layout_mappings == []
    assert assessment.element_mappings == []
    assert assessment.group_mappings == []
    assert assessment.semantic_implementation_mappings == []
    assert assessment.custom_implementation_warnings == []


def test_compatibility_assessment_allows_more_items_than_old_n8n_max_items_caps() -> None:
    # n8n's structured-output schema capped these lists at 2/5/3/4/3 respectively.
    # That was prompt/tool-schema tuning for the matcher LLM call, not a domain
    # invariant, so the domain model must not reject larger, still-valid results.
    assessment = CompatibilityAssessment(
        summary=_summary(),
        layout_mappings=[
            LayoutMapping(
                layout_id=f"layout-{i}",
                mui_components=["Container"],
                customization_level="minor",
                reason="...",
                confidence=0.8,
            )
            for i in range(3)
        ],
        element_mappings=[
            ElementMapping(
                element_id=f"el-{i}",
                mui_component="TextField",
                variant="outlined",
                customization_level="none",
                reason="...",
                confidence=0.9,
            )
            for i in range(6)
        ],
        group_mappings=[
            GroupMapping(
                group_id=f"group-{i}",
                mui_container_component="Stack",
                mui_child_component="TextField",
                customization_level="none",
                reason="...",
                confidence=0.85,
            )
            for i in range(4)
        ],
        semantic_implementation_mappings=[
            SemanticImplementationMapping(
                semantic_pattern_name=f"pattern-{i}",
                semantic_type="layout",
                mui_strategy=["Stack"],
                reason="...",
                customization_level="minor",
                confidence=0.7,
            )
            for i in range(5)
        ],
        custom_implementation_warnings=[
            CustomImplementationWarning(target=f"target-{i}", reason="...", severity="low")
            for i in range(4)
        ],
    )

    assert len(assessment.layout_mappings) == 3
    assert len(assessment.element_mappings) == 6
    assert len(assessment.group_mappings) == 4
    assert len(assessment.semantic_implementation_mappings) == 5
    assert len(assessment.custom_implementation_warnings) == 4


def test_compatibility_assessment_realistic_construction_round_trips() -> None:
    payload = {
        "summary": {
            "compatibility_score": 78.5,
            "customization_effort": "medium",
            "overall_compatibility": "Achievable with moderate theming",
            "confidence": 0.8,
        },
        "layout_mappings": [
            {
                "layout_id": "layout-1",
                "mui_components": ["Container", "Stack"],
                "customization_level": "minor",
                "reason": "Single-column form maps to a vertical Stack",
                "confidence": 0.9,
            }
        ],
        "element_mappings": [
            {
                "element_id": "el-1",
                "mui_component": "TextField",
                "variant": "outlined",
                "customization_level": "none",
                "reason": "Standard bordered input",
                "confidence": 0.95,
            }
        ],
        "group_mappings": [
            {
                "group_id": "group-1",
                "mui_container_component": "Stack",
                "mui_child_component": "TextField",
                "customization_level": "none",
                "reason": "Grouped inputs map to a Stack of TextFields",
                "confidence": 0.9,
            }
        ],
        "semantic_implementation_mappings": [
            {
                "semantic_pattern_name": "grouped-form-inputs",
                "semantic_type": "layout",
                "mui_strategy": ["Stack with consistent spacing"],
                "reason": "Preserves the grouping semantics",
                "customization_level": "minor",
                "confidence": 0.85,
            }
        ],
        "custom_implementation_warnings": [
            {
                "target": "animated-hero",
                "reason": "No MUI equivalent for a looping background video",
                "severity": "medium",
            }
        ],
    }

    assessment = CompatibilityAssessment.model_validate(payload)
    dumped = assessment.model_dump()

    assert dumped["summary"]["compatibility_score"] == 78.5
    assert dumped["layout_mappings"][0]["mui_components"] == ["Container", "Stack"]
    assert dumped["element_mappings"][0]["mui_component"] == "TextField"
    assert dumped["group_mappings"][0]["mui_container_component"] == "Stack"
    assert dumped["semantic_implementation_mappings"][0]["semantic_pattern_name"] == (
        "grouped-form-inputs"
    )
    assert dumped["custom_implementation_warnings"][0]["severity"] == "medium"
