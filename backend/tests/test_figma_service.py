import pytest

from app.schemas.design_structure import DesignStructure
from app.services.figma import (
    FIGMA_ELEMENT_CONFIDENCE,
    InvalidFigmaUrlError,
    build_design_structure_from_figma_url,
    extract_file_key,
    normalize_figma_file,
)

# --- extract_file_key ---


@pytest.mark.parametrize(
    ("url", "expected_key"),
    [
        ("https://www.figma.com/design/ABC123/My-File", "ABC123"),
        ("https://figma.com/design/ABC123", "ABC123"),
        ("https://figma.com/file/XYZ789/Old-Format?node-id=1-2", "XYZ789"),
        ("http://www.figma.com/file/abc123def/Name", "abc123def"),
    ],
)
def test_extract_file_key_accepts_valid_figma_urls(url: str, expected_key: str) -> None:
    assert extract_file_key(url) == expected_key


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not-a-url",
        "https://example.com/design/ABC123",
        "https://figma.com/proto/ABC123/Name",
        "https://figma.com/design/",
    ],
)
def test_extract_file_key_rejects_invalid_urls(url: str) -> None:
    with pytest.raises(InvalidFigmaUrlError):
        extract_file_key(url)


# --- normalize_figma_file ---


def _text_node(node_id: str, characters: str | None = None, name: str = "") -> dict:
    node: dict = {"id": node_id, "type": "TEXT", "name": name}
    if characters is not None:
        node["characters"] = characters
    return node


def test_normalize_figma_file_handles_empty_document() -> None:
    structure = normalize_figma_file({"document": {"children": []}})

    assert structure.layout.overall_structure == "no frames"
    assert structure.layout.regions == []
    assert structure.layout.spacing is None
    assert structure.layout.alignment is None
    assert structure.groups == []
    assert structure.elements == []
    assert structure.source == "figma"


def test_normalize_figma_file_extracts_frames_text_and_groups() -> None:
    document = {
        "document": {
            "children": [
                {
                    "id": "0:1",
                    "type": "CANVAS",
                    "children": [
                        {
                            "id": "1:1",
                            "type": "FRAME",
                            "name": "Screen 1",
                            "layoutMode": "VERTICAL",
                            "itemSpacing": 16,
                            "primaryAxisAlignItems": "CENTER",
                            "children": [
                                _text_node("1:2", characters="Welcome"),
                                {
                                    "id": "1:3",
                                    "type": "GROUP",
                                    "name": "Button Group",
                                    "children": [
                                        _text_node("1:4", characters="OK"),
                                        _text_node("1:5", characters="Cancel"),
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ]
        }
    }

    structure = normalize_figma_file(document)

    assert structure.layout.overall_structure == "1 frame, all VERTICAL"
    assert structure.layout.regions == ["Screen 1"]
    assert structure.layout.spacing == "16px"
    assert structure.layout.alignment == "CENTER"

    assert len(structure.groups) == 1
    group = structure.groups[0]
    assert group.id == "1:3"
    assert group.type == "group"
    assert group.children == ["1:4", "1:5"]
    assert not hasattr(group, "confidence")

    assert len(structure.elements) == 3
    element_ids = {el.id for el in structure.elements}
    assert element_ids == {"1:2", "1:4", "1:5"}
    for element in structure.elements:
        assert element.visual_role == "text"
        assert element.confidence == FIGMA_ELEMENT_CONFIDENCE

    assert structure.source == "figma"


def test_normalize_figma_file_falls_back_to_node_name_when_no_characters() -> None:
    document = {
        "document": {
            "children": [
                {
                    "id": "0:1",
                    "type": "CANVAS",
                    "children": [_text_node("1:1", name="Untitled Text")],
                }
            ]
        }
    }

    structure = normalize_figma_file(document)

    assert structure.elements[0].visible_text == "Untitled Text"


def test_normalize_figma_file_omits_direction_when_frames_disagree() -> None:
    document = {
        "document": {
            "children": [
                {
                    "id": "0:1",
                    "type": "CANVAS",
                    "children": [
                        {"id": "1:1", "type": "FRAME", "name": "A", "layoutMode": "VERTICAL"},
                        {"id": "1:2", "type": "FRAME", "name": "B", "layoutMode": "HORIZONTAL"},
                    ],
                }
            ]
        }
    }

    structure = normalize_figma_file(document)

    assert structure.layout.overall_structure == "2 frames"
    assert structure.layout.regions == ["A", "B"]


def test_normalize_figma_file_ignores_frames_without_layout_mode_for_unanimity() -> None:
    document = {
        "document": {
            "children": [
                {
                    "id": "0:1",
                    "type": "CANVAS",
                    "children": [
                        {"id": "1:1", "type": "FRAME", "name": "A", "layoutMode": "VERTICAL"},
                        {"id": "1:2", "type": "FRAME", "name": "B"},
                    ],
                }
            ]
        }
    }

    structure = normalize_figma_file(document)

    assert structure.layout.overall_structure == "2 frames, all VERTICAL"


def test_normalize_figma_file_spacing_alignment_none_when_auto_layout_nodes_disagree() -> None:
    document = {
        "document": {
            "children": [
                {
                    "id": "0:1",
                    "type": "CANVAS",
                    "children": [
                        {
                            "id": "1:1",
                            "type": "FRAME",
                            "name": "A",
                            "layoutMode": "VERTICAL",
                            "itemSpacing": 8,
                            "primaryAxisAlignItems": "MIN",
                        },
                        {
                            "id": "1:2",
                            "type": "FRAME",
                            "name": "B",
                            "layoutMode": "HORIZONTAL",
                            "itemSpacing": 24,
                            "primaryAxisAlignItems": "CENTER",
                        },
                    ],
                }
            ]
        }
    }

    structure = normalize_figma_file(document)

    assert structure.layout.spacing is None
    assert structure.layout.alignment is None


# --- build_design_structure_from_figma_url ---


class _StubFigmaClient:
    def __init__(self, document: dict) -> None:
        self.document = document
        self.requested_file_keys: list[str] = []

    async def get_file(self, file_key: str) -> dict:
        self.requested_file_keys.append(file_key)
        return self.document


async def test_build_design_structure_from_figma_url_composes_the_full_pipeline() -> None:
    document = {"document": {"children": []}}
    client = _StubFigmaClient(document)

    structure = await build_design_structure_from_figma_url(
        "https://www.figma.com/design/ABC123/My-File", client
    )

    assert isinstance(structure, DesignStructure)
    assert client.requested_file_keys == ["ABC123"]
    assert structure.source == "figma"


async def test_build_design_structure_from_figma_url_rejects_invalid_url_first() -> None:
    client = _StubFigmaClient({"document": {"children": []}})

    with pytest.raises(InvalidFigmaUrlError):
        await build_design_structure_from_figma_url("https://example.com/not-figma", client)

    assert client.requested_file_keys == []
