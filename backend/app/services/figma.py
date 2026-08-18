"""Figma input path: URL validation, file-key extraction, and deterministic
normalization into `DesignStructure` (PROJECT_SPEC.md section 13).

Extraction is deliberately limited to the facts PROJECT_SPEC.md section 13
calls out -- frames, text nodes, groups, auto-layout containers, layout
direction, spacing, alignment. This is not a complete Figma parser: shapes,
components/instances, styles, fills, and prototype interactions are not
extracted, and no visual role is guessed from a node's name. Missing
information is left `None`/empty rather than invented (PROJECT_SPEC.md
section 10).

Confidence
----------
`DesignStructure.confidence` fields are defined (see
`app.schemas.design_structure` module docstring) as vision-stage
probabilistic certainty about a discrete observation. That concept does not
naturally apply to Figma: a `TEXT` node's `characters` are read directly and
completely from the file's document graph, with no perceptual ambiguity to
quantify -- unlike inferring "this is a button" from pixels.

Decision: `FIGMA_ELEMENT_CONFIDENCE = 1.0` is used for every `DesignElement`
produced by this module, representing full certainty of *extraction* (not
visual interpretation). This is a deliberate, documented choice, not a copy
of n8n's unexplained `0.9` placeholder. `DesignGroup` carries no confidence
field at all (see `design_structure.py`), so groups need no such value.
`RepeatedStructure`/`Relationship`/`CustomPattern` are not populated by this
module, so no confidence decision is needed for them here.
"""

import re

from app.clients.figma import FigmaClient
from app.schemas.design_structure import (
    DesignElement,
    DesignGroup,
    DesignStructure,
    LayoutDescription,
)

FIGMA_ELEMENT_CONFIDENCE = 1.0

_FIGMA_URL_PATTERN = re.compile(
    r"^https?://(?:www\.)?figma\.com/(?:file|design)/(?P<file_key>[a-zA-Z0-9]+)(?:[/?].*)?$"
)

_AUTO_LAYOUT_MODES = ("VERTICAL", "HORIZONTAL")


class InvalidFigmaUrlError(ValueError):
    """Raised when a Figma URL is malformed or does not contain a file key."""


def extract_file_key(figma_url: str) -> str:
    """Validate `figma_url` and return its file key.

    Accepts both Figma's legacy `/file/<key>/...` and current
    `/design/<key>/...` URL forms.
    """
    match = _FIGMA_URL_PATTERN.match(figma_url.strip())
    if not match:
        raise InvalidFigmaUrlError(f"Could not extract a Figma file key from URL: {figma_url!r}")
    return match.group("file_key")


def _unanimous_value(nodes: list[dict], key: str) -> object | None:
    """Return the shared value of `key` across `nodes` if all agree, else `None`.

    Nodes missing the key are ignored; if no node has the key, returns `None`.
    """
    values = {node[key] for node in nodes if node.get(key) is not None}
    if len(values) == 1:
        return next(iter(values))
    return None


def _describe_overall_structure(frames: list[dict]) -> str:
    """Describe the set of top-level frames without picking a single "winner".

    Only reports a layout direction when every frame that declares a
    `layoutMode` agrees on it; otherwise the description stays silent on
    direction rather than defaulting to the first frame's value.
    """
    if not frames:
        return "no frames"

    count_description = "1 frame" if len(frames) == 1 else f"{len(frames)} frames"

    modes = {frame["layoutMode"] for frame in frames if frame.get("layoutMode")}
    if len(modes) == 1:
        return f"{count_description}, all {next(iter(modes))}"
    return count_description


def _format_spacing(item_spacing: object) -> str | None:
    if not isinstance(item_spacing, (int, float)):
        return None
    return f"{item_spacing:g}px"


def normalize_figma_file(document: dict) -> DesignStructure:
    """Deterministically normalize a raw Figma "get file" response into a `DesignStructure`.

    See the module docstring for the deliberately limited scope of this
    extraction and the confidence design decision.
    """
    pages = document.get("document", {}).get("children", []) or []

    frames: list[dict] = []
    text_nodes: list[dict] = []
    group_nodes: list[dict] = []
    auto_layout_nodes: list[dict] = []

    def traverse(node: dict) -> None:
        node_type = node.get("type")

        if node_type == "FRAME":
            frames.append(node)
        elif node_type == "TEXT":
            text_nodes.append(node)
        elif node_type == "GROUP":
            group_nodes.append(node)

        if node.get("layoutMode") in _AUTO_LAYOUT_MODES:
            auto_layout_nodes.append(node)

        for child in node.get("children", []) or []:
            traverse(child)

    for page in pages:
        traverse(page)

    layout = LayoutDescription(
        overall_structure=_describe_overall_structure(frames),
        regions=[frame.get("name", "") for frame in frames],
        spacing=_format_spacing(_unanimous_value(auto_layout_nodes, "itemSpacing")),
        alignment=_unanimous_value(auto_layout_nodes, "primaryAxisAlignItems"),
        responsive_hints=None,
    )

    groups = [
        DesignGroup(
            id=node["id"],
            type="group",
            children=[child["id"] for child in node.get("children", []) or [] if child.get("id")],
        )
        for node in group_nodes
    ]

    elements = [
        DesignElement(
            id=node["id"],
            visual_role="text",
            visible_text=node.get("characters") or node.get("name"),
            confidence=FIGMA_ELEMENT_CONFIDENCE,
        )
        for node in text_nodes
    ]

    return DesignStructure(
        layout=layout,
        groups=groups,
        elements=elements,
        source="figma",
    )


async def build_design_structure_from_figma_url(
    figma_url: str, client: FigmaClient
) -> DesignStructure:
    """Full Figma input path: URL -> file key -> Figma API -> `DesignStructure`.

    Raises `InvalidFigmaUrlError` before any network call if `figma_url` is
    malformed, and `FigmaAPIError` (from `app.clients.figma`) if the Figma
    API call fails.
    """
    file_key = extract_file_key(figma_url)
    document = await client.get_file(file_key)
    return normalize_figma_file(document)
