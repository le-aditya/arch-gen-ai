"""Renders the structured node/edge diagrams (PRD section 25) as vector figures
inside the PDF report.

The web UI draws these diagrams with SVG; the PDF previously only printed the
caption, which left sections 8 and 9 with no diagram at all. This module draws
the same layered blueprint on a reportlab canvas: rows are derived from the
longest path to each node, edges are routed orthogonally with arrowheads, and
shapes follow the node kind (client, gateway, service, database, queue, infra).
"""
from __future__ import annotations

from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable

from app.schemas.schemas import Diagram

INK = colors.HexColor("#0E2A3F")
CYANOTYPE = colors.HexColor("#3E7CB1")
AMBER = colors.HexColor("#D98E36")
MUTED = colors.HexColor("#6B7C8C")
EDGE = colors.HexColor("#8FA6B8")

NODE_H = 32
MIN_NODE_W = 78
GAP_X = 16
GAP_V = 36
PAD = 2

FILL = {
    "client": colors.HexColor("#FFFFFF"),
    "gateway": colors.HexColor("#FDF3E6"),
    "service": colors.HexColor("#EAF2F8"),
    "database": colors.HexColor("#E8F1EC"),
    "queue": colors.HexColor("#F4EEF7"),
    "infra": colors.HexColor("#F2F4F6"),
}
STROKE = {
    "client": INK,
    "gateway": AMBER,
    "service": CYANOTYPE,
    "database": colors.HexColor("#4F8A6B"),
    "queue": colors.HexColor("#7C5C93"),
    "infra": MUTED,
}

# (font size, max characters per line) attempts, widest first.
_FIT_STEPS = [(7.4, 20), (7.0, 18), (6.6, 16), (6.2, 14), (5.8, 12)]


def _wrap(label: str, max_chars: int, max_lines: int = 2) -> list[str]:
    """Break a label into at most `max_lines` balanced lines."""
    label = " ".join(label.split())
    if len(label) <= max_chars:
        return [label]

    words = label.split(" ")
    if len(words) == 1:
        return [label]

    target_lines = min(max_lines, max(2, -(-len(label) // max_chars)))
    per_line = -(-len(label) // target_lines)
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > per_line and len(lines) < target_lines - 1:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines[:max_lines]


def _levels(nodes, edges) -> list[list]:
    """Longest-path layering, so every edge points from an upper to a lower row."""
    incoming = {n.id: 0 for n in nodes}
    for edge in edges:
        incoming[edge.target] = incoming.get(edge.target, 0) + 1

    level = {n.id: 0 for n in nodes if incoming.get(n.id, 0) == 0}
    if not level and nodes:
        level[nodes[0].id] = 0

    changed = True
    while changed:
        changed = False
        for edge in edges:
            if edge.source in level:
                candidate = level[edge.source] + 1
                if level.get(edge.target, -1) < candidate:
                    level[edge.target] = candidate
                    changed = True

    depth = max(level.values(), default=0)
    rows: list[list] = [[] for _ in range(depth + 1)]
    for node in nodes:
        rows[level.get(node.id, 0)].append(node)
    return rows


class DiagramFlowable(Flowable):
    """A self-sizing vector figure for one architecture or deployment diagram."""

    def __init__(self, diagram: Diagram):
        super().__init__()
        self.diagram = diagram
        self._scale = 1.0
        self._offset = 0.0
        self._height_natural = 0.0
        self._layout = None

    # -- layout ---------------------------------------------------------
    def _build(self, available_width: float):
        rows = _levels(self.diagram.nodes, self.diagram.edges)

        for font_size, max_chars in _FIT_STEPS:
            sized = []
            for row in rows:
                sized_row = []
                for node in row:
                    lines = _wrap(node.label, max_chars)
                    widest = max(stringWidth(line, "Helvetica", font_size) for line in lines)
                    sized_row.append({
                        "node": node,
                        "lines": lines,
                        "w": max(MIN_NODE_W, widest + 18),
                    })
                sized.append(sized_row)

            row_widths = [
                sum(n["w"] for n in row) + GAP_X * max(0, len(row) - 1)
                for row in sized
            ]
            natural_w = max(row_widths, default=0) + PAD * 2
            if natural_w <= available_width:
                return self._place(sized, row_widths, natural_w, font_size, 1.0)

        scale = available_width / natural_w if natural_w else 1.0
        return self._place(sized, row_widths, natural_w, font_size, min(scale, 1.0))

    def _place(self, sized, row_widths, natural_w, font_size, scale):
        content_w = natural_w - PAD * 2
        placed = {}
        top = PAD
        for index, row in enumerate(sized):
            x = PAD + (content_w - row_widths[index]) / 2
            y = top + index * (NODE_H + GAP_V)
            for item in row:
                node = item["node"]
                placed[node.id] = {
                    "id": node.id,
                    "kind": node.kind,
                    "lines": item["lines"],
                    "x": x,
                    "y": y,
                    "w": item["w"],
                    "cx": x + item["w"] / 2,
                    "level": index,
                }
                x += item["w"] + GAP_X

        rows = len(sized)
        graph_h = rows * NODE_H + max(0, rows - 1) * GAP_V
        total_h = graph_h + PAD * 2
        self._layout = {"placed": placed, "font_size": font_size, "width": natural_w}
        return natural_w, total_h + 6, scale

    def wrap(self, availWidth, availHeight):
        width, height, scale = self._build(availWidth)
        self._scale = scale
        # Claim the full column width so narrow diagrams (a deployment with few
        # nodes) are centred instead of hugging the left margin.
        self._offset = max(0.0, (availWidth - width * scale) / 2)
        self.width = availWidth
        self.height = height * scale
        self._height_natural = height
        return self.width, self.height

    # -- drawing --------------------------------------------------------
    def draw(self):
        canvas = self.canv
        canvas.saveState()
        if self._offset:
            canvas.translate(self._offset, 0)
        if self._scale != 1.0:
            canvas.scale(self._scale, self._scale)

        placed = self._layout["placed"]
        font_size = self._layout["font_size"]
        natural_h = self._height_natural

        out_degree: dict[str, int] = {}
        for edge in self.diagram.edges:
            out_degree[edge.source] = out_degree.get(edge.source, 0) + 1

        for edge in self.diagram.edges:
            source = placed.get(edge.source)
            target = placed.get(edge.target)
            if source is None or target is None:
                continue
            self._draw_edge(canvas, source, target, natural_h)

        for item in placed.values():
            if out_degree.get(item["id"], 0) > 1:
                canvas.setFillColor(EDGE)
                canvas.circle(item["cx"], natural_h - (item["y"] + NODE_H), 2.2, stroke=0, fill=1)

        for item in placed.values():
            self._draw_node(canvas, item, natural_h, font_size)

        canvas.restoreState()

    def _draw_edge(self, canvas, source, target, natural_h):
        sx = source["cx"]
        sy = natural_h - (source["y"] + NODE_H)
        tx = target["cx"]
        ty = natural_h - target["y"]

        canvas.setStrokeColor(EDGE)
        canvas.setLineWidth(0.9)
        canvas.setLineCap(0)

        path = canvas.beginPath()
        path.moveTo(sx, sy)
        if abs(sx - tx) < 0.5:
            path.lineTo(tx, ty + 5)
        else:
            mid_y = sy + (ty - sy) / 2
            path.lineTo(sx, mid_y)
            path.lineTo(tx, mid_y)
            path.lineTo(tx, ty + 5)
        canvas.drawPath(path, stroke=1, fill=0)

        canvas.setFillColor(EDGE)
        head = canvas.beginPath()
        head.moveTo(tx - 3.6, ty + 6)
        head.lineTo(tx + 3.6, ty + 6)
        head.lineTo(tx, ty)
        head.close()
        canvas.drawPath(head, stroke=0, fill=1)

    def _draw_node(self, canvas, item, natural_h, font_size):
        x = item["x"]
        y = natural_h - (item["y"] + NODE_H)
        w = item["w"]
        h = NODE_H
        kind = item["kind"]

        canvas.setFillColor(FILL.get(kind, FILL["service"]))
        canvas.setStrokeColor(STROKE.get(kind, STROKE["service"]))
        canvas.setLineWidth(1.0)

        if kind == "database":
            radius = 4.5
            # Bottom ellipse is stroked so the cylinder keeps a visible lower
            # arc once the body rectangle is filled over its upper half.
            canvas.ellipse(x, y, x + w, y + 2 * radius, stroke=1, fill=1)
            canvas.rect(x, y + radius, w, h - 2 * radius, stroke=0, fill=1)
            canvas.line(x, y + radius, x, y + h - radius)
            canvas.line(x + w, y + radius, x + w, y + h - radius)
            canvas.ellipse(x, y + h - 2 * radius, x + w, y + h, stroke=1, fill=1)
        elif kind == "gateway":
            cut = 8
            path = canvas.beginPath()
            path.moveTo(x + cut, y)
            path.lineTo(x + w, y)
            path.lineTo(x + w, y + h - cut)
            path.lineTo(x + w - cut, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y + cut)
            path.close()
            canvas.drawPath(path, stroke=1, fill=1)
        elif kind == "queue":
            canvas.rect(x, y, w, h, stroke=1, fill=1)
            canvas.setLineWidth(0.7)
            canvas.line(x + w - 12, y, x + w - 12, y + h)
            canvas.line(x + w - 20, y, x + w - 20, y + h)
        elif kind == "client":
            canvas.rect(x, y, w, h, stroke=1, fill=1)
            canvas.setLineWidth(0.7)
            canvas.line(x + 8, y + 7, x + w - 8, y + 7)
        elif kind == "infra":
            canvas.setDash(3, 2)
            canvas.rect(x, y, w, h, stroke=1, fill=1)
            canvas.setDash()
        else:
            canvas.rect(x, y, w, h, stroke=1, fill=1)

        canvas.setFillColor(INK)
        canvas.setFont("Helvetica", font_size)
        lines = item["lines"]
        first_baseline = y + h / 2 + (4.2 if len(lines) == 1 else 7.6)
        for index, line in enumerate(lines):
            canvas.drawCentredString(item["cx"], first_baseline - index * (font_size + 1.6), line)


def diagram_flowable(diagram: Diagram) -> DiagramFlowable:
    return DiagramFlowable(diagram)
