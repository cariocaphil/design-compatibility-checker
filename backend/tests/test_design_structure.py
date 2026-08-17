import pytest
from pydantic import ValidationError

from app.schemas.design_structure import (
    CustomPattern,
    DesignElement,
    DesignGroup,
    DesignStructure,
    LayoutDescription,
    Relationship,
    RepeatedStructure,
)


def test_layout_description_requires_only_overall_structure() -> None:
    layout = LayoutDescription(overall_structure="single-column")

    assert layout.regions == []
    assert layout.spacing is None
    assert layout.alignment is None
    assert layout.responsive_hints is None


def test_layout_description_has_no_confidence_field() -> None:
    assert "confidence" not in LayoutDescription.model_fields


def test_design_group_requires_id_type_and_confidence() -> None:
    with pytest.raises(ValidationError):
        DesignGroup(id="group-1", type="card")  # missing confidence


def test_design_group_defaults_children_to_empty_list() -> None:
    group = DesignGroup(id="group-1", type="card", confidence=0.8)

    assert group.children == []


@pytest.mark.parametrize("confidence", [0.0, 1.0])
def test_design_group_confidence_accepts_boundary_values(confidence: float) -> None:
    DesignGroup(id="group-1", type="card", confidence=confidence)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_design_group_confidence_rejects_out_of_range_values(confidence: float) -> None:
    with pytest.raises(ValidationError):
        DesignGroup(id="group-1", type="card", confidence=confidence)


def test_design_element_requires_visual_role_and_confidence() -> None:
    with pytest.raises(ValidationError):
        DesignElement(id="el-1")  # missing visual_role and confidence


def test_design_element_optional_fields_default_to_none() -> None:
    element = DesignElement(id="el-1", visual_role="button", confidence=0.9)

    assert element.visible_text is None
    assert element.state is None
    assert element.interaction_hint is None
    assert element.orientation is None
    assert element.continuity is None
    assert element.associated_icon is None


@pytest.mark.parametrize("confidence", [0.0, 1.0])
def test_design_element_confidence_accepts_boundary_values(confidence: float) -> None:
    DesignElement(id="el-1", visual_role="button", confidence=confidence)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_design_element_confidence_rejects_out_of_range_values(confidence: float) -> None:
    with pytest.raises(ValidationError):
        DesignElement(id="el-1", visual_role="button", confidence=confidence)


def test_design_element_represents_a_divider_via_visual_role_and_metadata() -> None:
    divider = DesignElement(
        id="div-1",
        visual_role="divider",
        visible_text="OR",
        state=None,
        orientation="horizontal",
        continuity="interrupted",
        associated_icon="chevron",
        confidence=0.85,
    )

    assert divider.orientation == "horizontal"
    assert divider.continuity == "interrupted"
    assert divider.associated_icon == "chevron"
    assert divider.visible_text == "OR"


def test_design_element_ordinary_element_leaves_divider_fields_none() -> None:
    button = DesignElement(id="btn-1", visual_role="button", confidence=0.95)

    assert button.orientation is None
    assert button.continuity is None
    assert button.associated_icon is None


def test_design_element_state_is_reserved_for_genuine_ui_states() -> None:
    checkbox = DesignElement(id="cb-1", visual_role="checkbox", state="checked", confidence=0.9)

    assert checkbox.state == "checked"


def test_repeated_structure_item_count_not_cross_validated_against_visible_items() -> None:
    # Deliberate leniency: item_count is a self-reported hint from the vision
    # stage and is not required to equal len(visible_items).
    repeated = RepeatedStructure(
        id="rep-1",
        item_type="card",
        item_count=5,
        visible_items=["A", "B"],
        confidence=0.7,
    )

    assert repeated.item_count == 5
    assert repeated.visible_items == ["A", "B"]


def test_repeated_structure_item_count_rejects_negative_values() -> None:
    with pytest.raises(ValidationError):
        RepeatedStructure(id="rep-1", item_type="card", item_count=-1, confidence=0.7)


def test_relationship_requires_confidence() -> None:
    with pytest.raises(ValidationError):
        Relationship(source="label-1", target="input-1", relationship="labels")


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_relationship_confidence_rejects_out_of_range_values(confidence: float) -> None:
    with pytest.raises(ValidationError):
        Relationship(
            source="label-1", target="input-1", relationship="labels", confidence=confidence
        )


def test_custom_pattern_requires_confidence() -> None:
    with pytest.raises(ValidationError):
        CustomPattern(type="carousel", description="An auto-rotating image carousel")


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_custom_pattern_confidence_rejects_out_of_range_values(confidence: float) -> None:
    with pytest.raises(ValidationError):
        CustomPattern(
            type="carousel",
            description="An auto-rotating image carousel",
            confidence=confidence,
        )


def test_design_structure_defaults_all_lists_to_empty() -> None:
    structure = DesignStructure(layout=LayoutDescription(overall_structure="single-column"))

    assert structure.groups == []
    assert structure.elements == []
    assert structure.repeated_structures == []
    assert structure.relationships == []
    assert structure.custom_patterns == []
    assert structure.source is None


def test_design_structure_source_only_accepts_known_literals() -> None:
    with pytest.raises(ValidationError):
        DesignStructure(
            layout=LayoutDescription(overall_structure="single-column"),
            source="hand-drawn-sketch",
        )


def test_design_structure_realistic_construction_round_trips() -> None:
    payload = {
        "layout": {
            "overall_structure": "single-column form",
            "regions": ["header", "form", "footer"],
            "spacing": "16px",
            "alignment": "center",
            "responsive_hints": None,
        },
        "groups": [
            {
                "id": "group-1",
                "type": "form-section",
                "children": ["el-1", "el-2"],
                "confidence": 0.9,
            }
        ],
        "elements": [
            {
                "id": "el-1",
                "visual_role": "text-field",
                "visible_text": "Email",
                "confidence": 0.92,
            },
            {
                "id": "el-2",
                "visual_role": "divider",
                "visible_text": "OR",
                "orientation": "horizontal",
                "continuity": "interrupted",
                "confidence": 0.8,
            },
        ],
        "repeated_structures": [
            {
                "id": "rep-1",
                "item_type": "social-login-button",
                "item_count": 3,
                "visible_items": ["Google", "Apple", "GitHub"],
                "confidence": 0.88,
            }
        ],
        "relationships": [
            {"source": "el-1", "target": "group-1", "relationship": "member-of", "confidence": 0.95}
        ],
        "custom_patterns": [
            {
                "type": "animated-hero",
                "description": "A looping background video",
                "confidence": 0.6,
            }
        ],
        "source": "screenshot",
    }

    structure = DesignStructure.model_validate(payload)
    dumped = structure.model_dump()

    assert dumped["layout"]["overall_structure"] == "single-column form"
    assert dumped["groups"][0]["confidence"] == 0.9
    assert dumped["elements"][1]["orientation"] == "horizontal"
    assert dumped["repeated_structures"][0]["item_count"] == 3
    assert dumped["relationships"][0]["relationship"] == "member-of"
    assert dumped["custom_patterns"][0]["type"] == "animated-hero"
    assert dumped["source"] == "screenshot"
