import pytest
from pydantic import BaseModel, ValidationError

from app.schemas.design_summary import (
    DesignSummary,
    SummaryAmbiguousPattern,
    SummaryCustomPattern,
    SummaryElement,
    SummaryGroup,
    SummaryLayout,
    SummaryRelationship,
    SummaryRepeatedStructure,
    SummarySemanticPattern,
)

SUMMARY_MODELS: list[type[BaseModel]] = [
    DesignSummary,
    SummaryLayout,
    SummaryGroup,
    SummaryElement,
    SummaryRepeatedStructure,
    SummarySemanticPattern,
    SummaryRelationship,
    SummaryCustomPattern,
    SummaryAmbiguousPattern,
]


@pytest.mark.parametrize("model_class", SUMMARY_MODELS)
def test_no_design_summary_model_exposes_a_confidence_field(model_class: type[BaseModel]) -> None:
    # DesignSummary is a deterministic, reduced projection: confidence is
    # diagnostic input to the (future) projection logic, never re-exposed here.
    assert "confidence" not in model_class.model_fields


def test_summary_layout_defaults_regions_to_empty_list() -> None:
    layout = SummaryLayout(overall_structure="single-column")

    assert layout.regions == []
    assert layout.alignment is None
    assert layout.spacing is None


def test_summary_group_defaults_children_to_empty_list() -> None:
    group = SummaryGroup(id="group-1", type="form-section")

    assert group.children == []


def test_summary_element_represents_a_divider() -> None:
    divider = SummaryElement(
        id="div-1",
        role="divider",
        text="OR",
        orientation="horizontal",
        continuity="interrupted",
        associated_icon="chevron",
    )

    assert divider.orientation == "horizontal"
    assert divider.continuity == "interrupted"
    assert divider.associated_icon == "chevron"


def test_summary_element_ordinary_element_leaves_divider_fields_none() -> None:
    element = SummaryElement(id="btn-1", role="button", text="Submit")

    assert element.orientation is None
    assert element.continuity is None
    assert element.associated_icon is None


def test_summary_repeated_structure_defaults_visible_text_list_to_empty() -> None:
    repeated = SummaryRepeatedStructure(id="rep-1", item_type="card", count=3)

    assert repeated.visible_text_list == []


def test_summary_semantic_pattern_rejects_invalid_importance_literal() -> None:
    with pytest.raises(ValidationError):
        SummarySemanticPattern(name="grouped-inputs", type="layout", importance="urgent")


def test_summary_relationship_requires_all_core_fields() -> None:
    with pytest.raises(ValidationError):
        SummaryRelationship(source="label-1", target="input-1")


def test_summary_custom_pattern_requires_all_core_fields() -> None:
    with pytest.raises(ValidationError):
        SummaryCustomPattern(type="carousel")


def test_summary_ambiguous_pattern_requires_all_core_fields() -> None:
    with pytest.raises(ValidationError):
        SummaryAmbiguousPattern(description="Unclear whether this button submits the form")


def test_summary_ambiguous_pattern_construction() -> None:
    pattern = SummaryAmbiguousPattern(
        description="Unclear whether the divider label is decorative",
        reason="No visible hover/focus affordance",
    )

    assert pattern.description == "Unclear whether the divider label is decorative"
    assert pattern.reason == "No visible hover/focus affordance"


def test_design_summary_defaults_all_lists_to_empty() -> None:
    summary = DesignSummary(layout=SummaryLayout(overall_structure="single-column"))

    assert summary.groups == []
    assert summary.elements == []
    assert summary.repeated_structures == []
    assert summary.semantic_patterns == []
    assert summary.missing_or_ambiguous_patterns == []
    assert summary.relationships == []
    assert summary.custom_patterns == []
    assert summary.source is None


def test_design_summary_realistic_construction_round_trips() -> None:
    payload = {
        "layout": {"overall_structure": "single-column form", "regions": ["header", "form"]},
        "groups": [{"id": "group-1", "type": "form-section", "children": ["el-1"]}],
        "elements": [
            {"id": "el-1", "role": "text-field", "text": "Email"},
            {
                "id": "el-2",
                "role": "divider",
                "text": "OR",
                "orientation": "horizontal",
                "continuity": "interrupted",
            },
        ],
        "repeated_structures": [
            {
                "id": "rep-1",
                "item_type": "social-login-button",
                "count": 3,
                "visible_text_list": ["Google", "Apple", "GitHub"],
            }
        ],
        "semantic_patterns": [
            {
                "name": "grouped-form-inputs",
                "type": "layout",
                "importance": "high",
                "implementation_implications": ["Use a container with consistent spacing"],
            }
        ],
        "missing_or_ambiguous_patterns": [
            {
                "description": "Unclear whether the divider label is decorative",
                "reason": "No visible hover/focus affordance",
            }
        ],
        "relationships": [{"source": "el-1", "target": "group-1", "relationship": "member-of"}],
        "custom_patterns": [{"type": "animated-hero", "description": "A looping background video"}],
        "source": "screenshot",
    }

    summary = DesignSummary.model_validate(payload)
    dumped = summary.model_dump()

    assert dumped["groups"][0]["id"] == "group-1"
    assert dumped["elements"][1]["orientation"] == "horizontal"
    assert dumped["repeated_structures"][0]["count"] == 3
    assert dumped["semantic_patterns"][0]["implementation_implications"] == [
        "Use a container with consistent spacing"
    ]
    assert dumped["missing_or_ambiguous_patterns"][0] == {
        "description": "Unclear whether the divider label is decorative",
        "reason": "No visible hover/focus affordance",
    }
    assert dumped["relationships"][0]["relationship"] == "member-of"
    assert dumped["custom_patterns"][0]["type"] == "animated-hero"
    assert dumped["source"] == "screenshot"
