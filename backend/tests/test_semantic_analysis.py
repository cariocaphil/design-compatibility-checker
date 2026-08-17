import pytest
from pydantic import ValidationError

from app.schemas.semantic_analysis import AmbiguousPattern, SemanticAnalysis, SemanticPattern


def test_semantic_pattern_requires_all_core_fields() -> None:
    # Missing type/visual_evidence/purpose/importance/confidence.
    with pytest.raises(ValidationError):
        SemanticPattern(name="grouped-inputs")


def test_semantic_pattern_implementation_implications_default_to_empty_list() -> None:
    pattern = SemanticPattern(
        name="grouped-inputs",
        type="layout",
        visual_evidence="Inputs are visually grouped with consistent spacing",
        purpose="Signals that these fields belong to one logical section",
        importance="medium",
        confidence=0.8,
    )

    assert pattern.implementation_implications == []


def test_semantic_pattern_uses_implementation_implications_not_mui_implications() -> None:
    # Spec section 15 explicitly forbids MUI-specific naming in this generic layer.
    assert "implementation_implications" in SemanticPattern.model_fields
    assert "mui_implications" not in SemanticPattern.model_fields


def test_semantic_pattern_rejects_invalid_type_literal() -> None:
    with pytest.raises(ValidationError):
        SemanticPattern(
            name="grouped-inputs",
            type="not-a-real-type",
            visual_evidence="...",
            purpose="...",
            importance="medium",
            confidence=0.8,
        )


def test_semantic_pattern_rejects_invalid_importance_literal() -> None:
    with pytest.raises(ValidationError):
        SemanticPattern(
            name="grouped-inputs",
            type="layout",
            visual_evidence="...",
            purpose="...",
            importance="urgent",
            confidence=0.8,
        )


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_semantic_pattern_confidence_rejects_out_of_range_values(confidence: float) -> None:
    with pytest.raises(ValidationError):
        SemanticPattern(
            name="grouped-inputs",
            type="layout",
            visual_evidence="...",
            purpose="...",
            importance="medium",
            confidence=confidence,
        )


def test_ambiguous_pattern_requires_all_fields() -> None:
    with pytest.raises(ValidationError):
        AmbiguousPattern(description="Unclear whether this button submits the form")


@pytest.mark.parametrize("confidence", [0.0, 1.0])
def test_ambiguous_pattern_confidence_accepts_boundary_values(confidence: float) -> None:
    AmbiguousPattern(
        description="Unclear whether this button submits the form",
        reason="No visible loading/disabled state to confirm interactivity",
        confidence=confidence,
    )


def test_semantic_analysis_defaults_lists_to_empty() -> None:
    analysis = SemanticAnalysis()

    assert analysis.semantic_patterns == []
    assert analysis.missing_or_ambiguous_patterns == []


def test_semantic_analysis_realistic_construction_round_trips() -> None:
    payload = {
        "semantic_patterns": [
            {
                "name": "grouped-form-inputs",
                "type": "layout",
                "visual_evidence": "Inputs share consistent spacing and a bordered container",
                "purpose": "Groups related fields into one logical form section",
                "importance": "high",
                "implementation_implications": ["Use a container with consistent internal spacing"],
                "confidence": 0.9,
            }
        ],
        "missing_or_ambiguous_patterns": [
            {
                "description": "Unclear whether the divider label is decorative or interactive",
                "reason": "No visible hover/focus affordance",
                "confidence": 0.4,
            }
        ],
    }

    analysis = SemanticAnalysis.model_validate(payload)
    dumped = analysis.model_dump()

    assert dumped["semantic_patterns"][0]["name"] == "grouped-form-inputs"
    assert dumped["semantic_patterns"][0]["implementation_implications"] == [
        "Use a container with consistent internal spacing"
    ]
    assert dumped["missing_or_ambiguous_patterns"][0]["confidence"] == 0.4
