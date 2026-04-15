from __future__ import annotations

from html import escape
from pathlib import Path

from steel_connections.data.sections_repository import get_beam_profile_properties, get_column_profile_properties
from steel_connections.models.input import AISC358MomentCase, InputCase
from steel_connections.models.units import Quantity


def _fmt_length(q: Quantity) -> str:
    return f"{q.value:.1f} {q.unit}"


def _require_length(case: AISC358MomentCase, field_name: str) -> Quantity:
    value = getattr(case.geometry, field_name)
    if value is None:
        raise ValueError(f"Missing required geometry field '{field_name}' for geometry artifact.")
    return value


def _hline(x1: float, x2: float, y: float, label: str) -> str:
    xm = (x1 + x2) / 2.0
    return (
        f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="#111111" stroke-width="1.6" />'
        f'<line x1="{x1:.1f}" y1="{y-8:.1f}" x2="{x1:.1f}" y2="{y+8:.1f}" stroke="#111111" stroke-width="1.4" />'
        f'<line x1="{x2:.1f}" y1="{y-8:.1f}" x2="{x2:.1f}" y2="{y+8:.1f}" stroke="#111111" stroke-width="1.4" />'
        f'<text x="{xm-28:.1f}" y="{y-10:.1f}" font-family="Arial, sans-serif" font-size="20" fill="#111111">{escape(label)}</text>'
    )


def _vdim(x: float, y1: float, y2: float, label: str, *, text_dx: float = 10.0) -> str:
    ym = (y1 + y2) / 2.0
    return (
        f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="#111111" stroke-width="1.6" />'
        f'<line x1="{x-7:.1f}" y1="{y1:.1f}" x2="{x+7:.1f}" y2="{y1:.1f}" stroke="#111111" stroke-width="1.4" />'
        f'<line x1="{x-7:.1f}" y1="{y2:.1f}" x2="{x+7:.1f}" y2="{y2:.1f}" stroke="#111111" stroke-width="1.4" />'
        f'<text x="{x+text_dx:.1f}" y="{ym+5:.1f}" font-family="Arial, sans-serif" font-size="20" fill="#111111">{escape(label)}</text>'
    )


def _build_chapter6_detail_svg(case: AISC358MomentCase) -> str:
    beam_profile = get_beam_profile_properties(
        beam_shape=case.sections.beam_shape,
        unit_system=case.units_system,
    )
    d = beam_profile["d"]
    tf = beam_profile["tf"]
    tw = beam_profile["tw"]

    bp = _require_length(case, "end_plate_width")
    g = _require_length(case, "bolt_gage")
    de = _require_length(case, "de")
    pb = _require_length(case, "pb")
    pfo = _require_length(case, "pfo")
    pfi = _require_length(case, "pfi")
    tcp = _require_length(case, "continuity_plate_thickness")
    # Nomenclature alignment:
    # pso := clear distance from top continuity plate to bolt line 2 centerline (input key: geometry.pfo)
    # psi := pfi + tfb - tcp (with pfi from input, tfb from beam section, tcp from input continuity plate)
    pso = pfo
    psi = Quantity(value=pfi.value + tf.value - tcp.value, unit=pfi.unit)
    if psi.value <= 0.0:
        raise ValueError(
            "Computed psi must be positive. Check geometry.pfi, beam flange thickness tfb, and geometry.continuity_plate_thickness."
        )
    lc_end_plate = _require_length(case, "clear_distance_end_plate")
    lc_column_flange = _require_length(case, "clear_distance_column_flange")
    column_end_distance = _require_length(case, "column_end_distance_to_beam_flange")

    # Distances are measured from the mid-thickness of the lower beam flange.
    h1 = Quantity(value=d.value - 0.5 * tf.value + pso.value + pb.value, unit=d.unit)
    h2 = Quantity(value=d.value - 0.5 * tf.value + pso.value, unit=d.unit)
    h3 = Quantity(value=d.value - 1.5 * tf.value - psi.value, unit=d.unit)
    h4 = Quantity(value=d.value - 1.5 * tf.value - psi.value - pb.value, unit=d.unit)
    hp = Quantity(value=2.0 * (d.value / 2.0 + pso.value + pb.value + de.value), unit=d.unit)

    width = 920
    height = 1160
    top = 160.0
    plate_h = 860.0
    plate_w = 240.0
    cx = 460.0
    x_left = cx - plate_w / 2.0
    x_right = cx + plate_w / 2.0
    bottom = top + plate_h

    scale = plate_h / hp.value if hp.value > 0.0 else 1.0
    half_gage = (g.value / bp.value) * (plate_w / 2.0) if bp.value > 0.0 else 50.0
    half_gage = max(28.0, min(half_gage, plate_w * 0.44))
    xb_l = cx - half_gage
    xb_r = cx + half_gage

    y0 = top
    y_de = y0 + de.value * scale
    y_de_pb = y_de + pb.value * scale
    y_de_pb_pfo = y_de_pb + pso.value * scale
    y_flange_top_outer = y_de_pb_pfo
    y_flange_top_inner = y_flange_top_outer + tf.value * scale
    y_tbf = y_flange_top_inner
    y_pfi = y_tbf + psi.value * scale
    y_pb2 = y_pfi + pb.value * scale

    # Bolt rows by connection variation.
    base_top = [
        de.value,
        de.value + pb.value,
        de.value + pb.value + pso.value + tf.value + psi.value,
        de.value + 2.0 * pb.value + pso.value + tf.value + psi.value,
    ]
    if case.connection_type == "bseep_8es":
        distances = sorted(base_top + [hp.value - item for item in base_top])
    else:
        distances = sorted([base_top[0], base_top[1], hp.value - base_top[1], hp.value - base_top[0]])
    bolt_y = [top + dist * scale for dist in distances]
    y_top_bolt = bolt_y[0]
    y_column_end_reference = max(26.0, y_flange_top_outer - column_end_distance.value * scale)

    bolts = "".join(
        f'<circle cx="{xb_l:.1f}" cy="{y:.1f}" r="8.5" fill="#111111" />'
        f'<circle cx="{xb_r:.1f}" cy="{y:.1f}" r="8.5" fill="#111111" />'
        for y in bolt_y
    )

    # Reference for h1-h4 is the mid-thickness of the lower flange.
    y_flange_bottom_outer = y_flange_top_outer + d.value * scale
    y_flange_bottom_mid = y_flange_bottom_outer - (tf.value * scale) / 2.0
    y_h1 = y_flange_bottom_mid - h1.value * scale
    y_h2 = y_flange_bottom_mid - h2.value * scale
    y_h3 = y_flange_bottom_mid - h3.value * scale
    y_h4 = y_flange_bottom_mid - h4.value * scale

    flange_t_px = max(tf.value * scale, 8.0)
    web_t_px = max(tw.value * scale, 6.0)
    y_flange_top_inner_draw = y_flange_top_outer + flange_t_px
    y_flange_bottom_inner_draw = y_flange_bottom_outer - flange_t_px
    web_x1 = cx - web_t_px / 2.0

    title = f"AISC 358 Chapter 6 - {escape(case.connection_type.upper())} Geometry Audit"
    info = [
        f"bp = {_fmt_length(bp)}",
        f"g = {_fmt_length(g)}",
        f"de = {_fmt_length(de)}",
        f"pb = {_fmt_length(pb)}",
        f"pso (geometry.pfo) = {_fmt_length(pso)}",
        f"pfi = {_fmt_length(pfi)}",
        f"tcp = {_fmt_length(tcp)}",
        f"psi = pfi + tfb - tcp = {_fmt_length(psi)}",
        f"lc_end_plate = {_fmt_length(lc_end_plate)}",
        f"lc_column_flange = {_fmt_length(lc_column_flange)}",
        f"column_end_distance = {_fmt_length(column_end_distance)}",
        f"h1 = {_fmt_length(h1)}",
        f"h2 = {_fmt_length(h2)}",
        f"h3 = {_fmt_length(h3)}",
        f"h4 = {_fmt_length(h4)}",
    ]
    info_text = "".join(
        f'<text x="36" y="{95 + i*30}" font-family="Arial, sans-serif" font-size="18" fill="#111111">{escape(line)}</text>'
        for i, line in enumerate(info)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect x="0" y="0" width="{width}" height="{height}" fill="#f7f7f7" />
  <text x="36" y="48" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#111111">{title}</text>
  {info_text}

  <rect x="{x_left:.1f}" y="{top:.1f}" width="{plate_w:.1f}" height="{plate_h:.1f}" fill="#ececec" stroke="#2c2c2c" stroke-width="2.2" />
  <rect x="{x_left+22:.1f}" y="{y_flange_top_outer:.1f}" width="{plate_w-44:.1f}" height="{flange_t_px:.1f}" fill="#d5d5d5" stroke="#2f2f2f" stroke-width="1.6" />
  <rect x="{x_left+22:.1f}" y="{y_flange_bottom_outer-flange_t_px:.1f}" width="{plate_w-44:.1f}" height="{flange_t_px:.1f}" fill="#d5d5d5" stroke="#2f2f2f" stroke-width="1.6" />
  <rect x="{web_x1:.1f}" y="{y_flange_top_inner_draw:.1f}" width="{web_t_px:.1f}" height="{y_flange_bottom_inner_draw-y_flange_top_inner_draw:.1f}" fill="#d5d5d5" stroke="#2f2f2f" stroke-width="1.6" />
  <line x1="{x_left+18:.1f}" y1="{y_flange_bottom_mid:.1f}" x2="{x_right-18:.1f}" y2="{y_flange_bottom_mid:.1f}" stroke="#6a6a6a" stroke-width="1.2" stroke-dasharray="5 4" />
  {bolts}

  {_hline(x_left, x_right, top-64, f"bp = {_fmt_length(bp)}")}
  {_hline(xb_l, xb_r, top-24, f"g = {_fmt_length(g)}")}
  {_hline(x_left, xb_l, y_top_bolt-24, f"lc_ep = {_fmt_length(lc_end_plate)}")}
  {_hline(xb_r, x_right, y_top_bolt+24, f"lc_cf = {_fmt_length(lc_column_flange)}")}

  {_vdim(x_right + 72, y0, y_de, f"de = {_fmt_length(de)}")}
  {_vdim(x_right + 72, y_de, y_de_pb, f"pb = {_fmt_length(pb)}")}
  {_vdim(x_right + 72, y_de_pb, y_de_pb_pfo, f"pso = {_fmt_length(pso)}")}
  {_vdim(x_right + 72, y_tbf, y_pfi, f"psi = {_fmt_length(psi)}")}
  {_vdim(x_right + 72, y_pfi, y_pb2, f"pb = {_fmt_length(pb)}")}

  {_vdim(x_left - 72, y_h1, y_flange_bottom_mid, f"h1 = {_fmt_length(h1)}", text_dx=-205)}
  {_vdim(x_left - 106, y_h2, y_flange_bottom_mid, f"h2 = {_fmt_length(h2)}", text_dx=-205)}
  {_vdim(x_left - 140, y_h3, y_flange_bottom_mid, f"h3 = {_fmt_length(h3)}", text_dx=-205)}
  {_vdim(x_left - 174, y_h4, y_flange_bottom_mid, f"h4 = {_fmt_length(h4)}", text_dx=-205)}
  <line x1="{x_left-236:.1f}" y1="{y_column_end_reference:.1f}" x2="{x_left-18:.1f}" y2="{y_column_end_reference:.1f}" stroke="#666666" stroke-width="1.2" stroke-dasharray="5 4" />
  {_vdim(x_left - 214, y_column_end_reference, y_flange_top_outer, f"a_col_end = {_fmt_length(column_end_distance)}", text_dx=-248)}

  <text x="{x_right + 24:.1f}" y="{(top+bottom)/2 + 8:.1f}" font-family="Arial, sans-serif" font-size="19" fill="#111111">tbw = {_fmt_length(tw)}</text>
  <text x="{x_right + 24:.1f}" y="{y_tbf - 12:.1f}" font-family="Arial, sans-serif" font-size="19" fill="#111111">tbf = {_fmt_length(tf)} (flange thickness)</text>
  <text x="{x_right + 24:.1f}" y="{bottom - 22:.1f}" font-family="Arial, sans-serif" font-size="19" fill="#111111">tp = {_fmt_length(_require_length(case, "end_plate_thickness"))}</text>
  <text x="{x_right + 24:.1f}" y="{bottom + 6:.1f}" font-family="Arial, sans-serif" font-size="17" fill="#111111">lc_ep: bolt center to end-plate edge</text>
  <text x="{x_right + 24:.1f}" y="{bottom + 30:.1f}" font-family="Arial, sans-serif" font-size="17" fill="#111111">lc_cf: bolt center to column-flange edge</text>
  <text x="{x_right + 24:.1f}" y="{bottom + 54:.1f}" font-family="Arial, sans-serif" font-size="17" fill="#111111">a_col_end: beam flange to column end</text>
  <text x="{x_right + 24:.1f}" y="{bottom + 78:.1f}" font-family="Arial, sans-serif" font-size="17" fill="#111111">psi = pfi + tfb - tcp</text>

  <text x="36" y="{height-20}" font-family="Arial, sans-serif" font-size="15" fill="#3a3a3a">
    Diagram generated by StructureLab_HFS_CNT for technical audit support.
  </text>
</svg>
"""


def _build_generic_moment_svg(case: AISC358MomentCase) -> str:
    title = f"AISC 358 - {escape(case.connection_type.upper())}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420">
  <rect x="0" y="0" width="900" height="420" fill="#f7f7f7" />
  <text x="30" y="54" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#111111">{title}</text>
  <text x="30" y="104" font-family="Arial, sans-serif" font-size="20" fill="#111111">
    Geometry detail artifact is specialized for Chapter 6 end-plate cases.
  </text>
</svg>
"""


def _build_bseep_8es_section_svg(case: AISC358MomentCase) -> str:
    beam = get_beam_profile_properties(
        beam_shape=case.sections.beam_shape,
        unit_system=case.units_system,
    )
    column = get_column_profile_properties(
        column_shape=case.sections.column_shape or "",
        unit_system=case.units_system,
    )
    g = _require_length(case, "bolt_gage")
    bp = _require_length(case, "end_plate_width")
    tp = _require_length(case, "end_plate_thickness")
    ts = _require_length(case, "stiffener_thickness")

    d_c = column["d"]
    b_cf = column["bf"]
    t_wc = column["tw"]
    t_fc = column["tf"]
    b_bf = beam["bf"]
    t_wb = beam["tw"]

    info = [
        f"bcf = {_fmt_length(b_cf)}",
        f"dc = {_fmt_length(d_c)}",
        f"twc = {_fmt_length(t_wc)}",
        f"tfc = {_fmt_length(t_fc)}",
        f"g = {_fmt_length(g)}",
        f"bp = {_fmt_length(bp)}",
        f"tp = {_fmt_length(tp)}",
        f"ts = {_fmt_length(ts)}",
        f"bbf = {_fmt_length(b_bf)}",
        f"twb = {_fmt_length(t_wb)}",
    ]
    info_text = "".join(
        f'<text x="32" y="{88 + i*26}" font-family="Arial, sans-serif" font-size="16" fill="#111111">{escape(line)}</text>'
        for i, line in enumerate(info)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="980" height="560" viewBox="0 0 980 560">
  <rect x="0" y="0" width="980" height="560" fill="#f7f7f7" />
  <text x="32" y="44" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#111111">
    BSEEP 8ES - Transverse Section Audit View
  </text>
  {info_text}

  <rect x="360" y="130" width="30" height="300" fill="#d4d4d4" stroke="#232323" stroke-width="1.8" />
  <rect x="620" y="130" width="30" height="300" fill="#d4d4d4" stroke="#232323" stroke-width="1.8" />
  <rect x="390" y="265" width="230" height="30" fill="#e7e7e7" stroke="#232323" stroke-width="1.8" />
  <rect x="650" y="245" width="220" height="70" fill="#efefef" stroke="#232323" stroke-width="1.8" />
  <line x1="760" y1="140" x2="760" y2="420" stroke="#444444" stroke-width="1.2" stroke-dasharray="6 4" />

  {_hline(392, 618, 240, f"g = {_fmt_length(g)}")}
  {_hline(650, 870, 216, f"bp = {_fmt_length(bp)}")}
  {_vdim(338, 130, 430, f"bcf = {_fmt_length(b_cf)}", text_dx=-150)}
  {_vdim(682, 130, 430, f"dc = {_fmt_length(d_c)}")}
  <text x="700" y="248" font-family="Arial, sans-serif" font-size="17" fill="#111111">twb = {_fmt_length(t_wb)}</text>
  <text x="700" y="270" font-family="Arial, sans-serif" font-size="17" fill="#111111">bbf = {_fmt_length(b_bf)}</text>
  <text x="700" y="294" font-family="Arial, sans-serif" font-size="17" fill="#111111">ts = {_fmt_length(ts)}</text>
  <text x="700" y="318" font-family="Arial, sans-serif" font-size="17" fill="#111111">tp = {_fmt_length(tp)}</text>
  <text x="700" y="342" font-family="Arial, sans-serif" font-size="17" fill="#111111">twc = {_fmt_length(t_wc)}</text>
  <text x="700" y="366" font-family="Arial, sans-serif" font-size="17" fill="#111111">tfc = {_fmt_length(t_fc)}</text>
</svg>
"""


def _build_bseep_8es_elevation_svg(case: AISC358MomentCase) -> str:
    beam = get_beam_profile_properties(
        beam_shape=case.sections.beam_shape,
        unit_system=case.units_system,
    )
    tfb = beam["tf"]
    d = beam["d"]
    de = _require_length(case, "de")
    pb = _require_length(case, "pb")
    pfo = _require_length(case, "pfo")
    pfi = _require_length(case, "pfi")
    tcp = _require_length(case, "continuity_plate_thickness")
    pso = pfo
    psi = Quantity(value=pfi.value + tfb.value - tcp.value, unit=pfi.unit)
    if psi.value <= 0.0:
        raise ValueError(
            "Computed psi must be positive. Check geometry.pfi, beam flange thickness tfb, and geometry.continuity_plate_thickness."
        )
    hst = Quantity(value=pfo.value + de.value, unit=pfo.unit)
    lst = Quantity(value=hst.value / 0.5773502691896257, unit=hst.unit)

    info = [
        f"de = {_fmt_length(de)}",
        f"pb = {_fmt_length(pb)}",
        f"pso (geometry.pfo) = {_fmt_length(pso)}",
        f"pfi = {_fmt_length(pfi)}",
        f"tcp = {_fmt_length(tcp)}",
        f"psi = pfi + tfb - tcp = {_fmt_length(psi)}",
        f"hst = {_fmt_length(hst)}",
        f"Lst = {_fmt_length(lst)}",
        f"tfb = {_fmt_length(tfb)}",
        f"d = {_fmt_length(d)}",
    ]
    info_text = "".join(
        f'<text x="32" y="{88 + i*26}" font-family="Arial, sans-serif" font-size="16" fill="#111111">{escape(line)}</text>'
        for i, line in enumerate(info)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="980" height="760" viewBox="0 0 980 760">
  <rect x="0" y="0" width="980" height="760" fill="#f7f7f7" />
  <text x="32" y="44" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#111111">
    BSEEP 8ES - Elevation Audit View
  </text>
  {info_text}

  <rect x="320" y="120" width="26" height="560" fill="#d4d4d4" stroke="#232323" stroke-width="1.8" />
  <rect x="400" y="120" width="18" height="560" fill="#d4d4d4" stroke="#232323" stroke-width="1.8" />
  <rect x="418" y="120" width="350" height="560" fill="#eeeeee" stroke="#232323" stroke-width="1.8" />
  <line x1="418" y1="400" x2="768" y2="400" stroke="#555555" stroke-width="1.3" stroke-dasharray="6 5" />

  <circle cx="456" cy="196" r="6.5" fill="#111111" />
  <circle cx="456" cy="248" r="6.5" fill="#111111" />
  <circle cx="456" cy="552" r="6.5" fill="#111111" />
  <circle cx="456" cy="604" r="6.5" fill="#111111" />

  {_vdim(792, 120, 680, f"d = {_fmt_length(d)}")}
  {_vdim(370, 170, 222, f"de = {_fmt_length(de)}", text_dx=-150)}
  {_vdim(370, 222, 274, f"pb = {_fmt_length(pb)}", text_dx=-150)}
  {_vdim(370, 274, 330, f"pso = {_fmt_length(pso)}", text_dx=-150)}
  {_vdim(370, 330, 382, f"psi = {_fmt_length(psi)}", text_dx=-150)}
  {_hline(452, 520, 640, f"Lst = {_fmt_length(lst)}")}
  {_vdim(542, 602, 680, f"hst = {_fmt_length(hst)}")}
  <text x="540" y="396" font-family="Arial, sans-serif" font-size="18" fill="#111111">tfb = {_fmt_length(tfb)}</text>
</svg>
"""


def _build_moment_connection_svg(case: AISC358MomentCase) -> str:
    if case.connection_type in {"bueep_4e", "bseep_4es", "bseep_8es"}:
        return _build_chapter6_detail_svg(case)
    return _build_generic_moment_svg(case)


def write_connection_geometry_artifact(case: InputCase, target_dir: str | Path) -> Path | None:
    if not isinstance(case, AISC358MomentCase):
        return None
    directory = Path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "geometry.svg"
    target.write_text(_build_moment_connection_svg(case), encoding="utf-8")
    if case.connection_type == "bseep_8es":
        extra_section = directory / "geometry_bseep_8es_section.svg"
        extra_section.write_text(_build_bseep_8es_section_svg(case), encoding="utf-8")
        extra_elevation = directory / "geometry_bseep_8es_elevation.svg"
        extra_elevation.write_text(_build_bseep_8es_elevation_svg(case), encoding="utf-8")
    return target
