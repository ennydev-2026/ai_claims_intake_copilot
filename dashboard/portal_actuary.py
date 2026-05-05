from __future__ import annotations

import html
from collections import Counter
from datetime import datetime

import pandas as pd
import streamlit as st

from api_client import api_get
from ui_chrome import hide_streamlit_top_bar

_PRIMARY = "#2563eb"
_SURFACE = "#f8fafc"
_CARD = "#ffffff"
_TEXT = "#0f172a"
_MUTED = "#64748b"
_GREEN = "#16a34a"
_ORANGE = "#ea580c"


def _inject_portal_css() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
            html, body, [class*="css"] {{
                font-family: 'DM Sans', sans-serif;
            }}
            .block-container {{
                padding-top: 1.25rem !important;
                padding-bottom: 2rem !important;
                max-width: 1280px !important;
            }}
            .portal-shell {{
                background: {_SURFACE};
                border-radius: 16px;
                padding: 0.5rem 0 1.5rem 0;
            }}
            .portal-topbar {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: {_CARD};
                border-radius: 14px;
                padding: 12px 20px;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
                margin-bottom: 1.25rem;
            }}
            .portal-brand {{
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 700;
                font-size: 1.05rem;
                color: {_TEXT};
            }}
            .portal-brand span.shield {{
                display: inline-flex;
                width: 32px;
                height: 32px;
                border-radius: 8px;
                background: {_PRIMARY};
                color: white;
                align-items: center;
                justify-content: center;
                font-size: 16px;
            }}
            .portal-nav {{
                display: flex;
                gap: 1.5rem;
                align-items: center;
            }}
            .portal-nav a {{
                color: {_MUTED};
                text-decoration: none;
                font-size: 0.95rem;
                font-weight: 500;
            }}
            .portal-nav a.active {{
                color: {_PRIMARY};
                border-bottom: 2px solid {_PRIMARY};
                padding-bottom: 2px;
            }}
            .portal-user {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .portal-avatar {{
                width: 40px;
                height: 40px;
                border-radius: 12px;
                background: #e0e7ff;
                color: {_PRIMARY};
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.9rem;
            }}
            .portal-bell {{
                position: relative;
                color: {_PRIMARY};
                font-size: 1.1rem;
            }}
            .portal-bell .badge {{
                position: absolute;
                top: -6px;
                right: -8px;
                background: {_PRIMARY};
                color: white;
                font-size: 0.65rem;
                padding: 2px 5px;
                border-radius: 8px;
            }}
            .kpi-card {{
                background: {_CARD};
                border-radius: 14px;
                padding: 16px 18px;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
                border: 1px solid #e2e8f0;
            }}
            .kpi-label {{
                font-size: 0.78rem;
                color: {_MUTED};
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 6px;
            }}
            .kpi-value {{
                font-size: 1.65rem;
                font-weight: 700;
                color: {_TEXT};
            }}
            .widget-card {{
                background: {_CARD};
                border-radius: 14px;
                padding: 16px 18px;
                margin-bottom: 14px;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
                border: 1px solid #e2e8f0;
            }}
            .widget-title {{
                font-weight: 700;
                font-size: 0.95rem;
                color: {_TEXT};
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .prio-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 999px;
                font-size: 0.8rem;
                font-weight: 600;
            }}
            .prio-alta {{ background: #fee2e2; color: #b91c1c; }}
            .prio-media {{ background: #ffedd5; color: {_ORANGE}; }}
            .prio-baja {{ background: #dcfce7; color: {_GREEN}; }}
            .timeline-step {{
                display: flex;
                align-items: flex-start;
                gap: 10px;
                margin-bottom: 10px;
                font-size: 0.88rem;
                color: {_TEXT};
            }}
            .timeline-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-top: 5px;
                flex-shrink: 0;
            }}
            .dot-done {{ background: {_GREEN}; }}
            .dot-active {{ background: {_PRIMARY}; box-shadow: 0 0 0 3px rgba(37,99,235,0.25); }}
            .dot-pending {{ background: #cbd5e1; }}
            .insight-box {{
                background: #eff6ff;
                border-radius: 10px;
                padding: 12px 14px;
                font-size: 0.88rem;
                color: #1e3a8a;
                margin-top: 10px;
                border: 1px solid #bfdbfe;
            }}
            ul.faltantes {{
                margin: 8px 0 0 1rem;
                padding: 0;
                color: {_ORANGE};
                font-size: 0.88rem;
            }}
            div[data-testid="stSidebarNav"] {{
                padding-top: 0.5rem;
            }}
            .analyst-snippet-card {{
                margin-bottom: 4px;
            }}
            .snippet-meta {{
                font-size: 0.75rem;
                color: {_MUTED};
                margin: 4px 0 8px 0;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _safe_summary():
    try:
        return api_get("/api/v1/claims/dashboard/summary"), None
    except Exception as exc:
        return None, str(exc)


def _safe_recent():
    try:
        return api_get("/api/v1/claims/recent?limit=100"), None
    except Exception as exc:
        return None, str(exc)


def _build_insights(summary: dict, claims: list) -> tuple[str, list[str], list[str]]:
    bullets: list[str] = []
    faltantes: list[str] = []
    if summary["total_claims"] == 0:
        return (
            "Aún no hay volumen registrado en el periodo. Cuando ingresen reclamos, aquí verás "
            "prioridades y tipos dominantes.",
            ["Sin datos suficientes para alertas automáticas."],
            [],
        )
    counts = Counter({"alta": summary["alta"], "media": summary["media"], "baja": summary["baja"]})
    dominant = counts.most_common(1)[0][0]
    bullets.append(f"Prioridad modal observada: **{dominant}** ({counts[dominant]} reclamos).")

    if claims:
        df = pd.DataFrame(claims)
        types = df["claim_type"].fillna("(sin tipo)").value_counts().head(3)
        top_types = ", ".join(types.index.tolist())
        bullets.append(f"Tipos de siniestro más frecuentes: {top_types}.")
        try:
            dates = pd.to_datetime(df["created_at"], utc=True)
            last = dates.max()
            bullets.append(f"Último ingreso registrado: **{last.strftime('%Y-%m-%d %H:%M')} UTC**.")
        except Exception:
            pass

    if claims:
        sample = claims[0]
        mi = sample.get("missing_items") or []
        if isinstance(mi, list) and mi:
            faltantes = [str(x) for x in mi[:4]]

    narrative = (
        "Resumen actuarial rápido basado en la cartera ingestada: distribución de prioridades y "
        "mix de tipos de siniestro. Use los gráficos para detectar concentraciones."
    )
    return narrative, bullets if bullets else ["Sin alertas destacadas en este snapshot."], faltantes


def _truncate_preview(text: str | None, max_len: int = 220) -> str:
    if not text:
        return "(Sin resumen)"
    t = str(text).strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def _format_created_at(value) -> str:
    if value is None:
        return "—"
    s = str(value)
    try:
        s_norm = s.replace("Z", "+00:00") if s.endswith("Z") and "+" not in s else s
        dt = datetime.fromisoformat(s_norm)
        if dt.tzinfo is not None:
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return s[:32]


def _prio_badge_class(level: str | None) -> str:
    key = str(level or "").lower()
    if key == "alta":
        return "prio-alta"
    if key == "baja":
        return "prio-baja"
    return "prio-media"


st.set_page_config(page_title="Claims Intake Copilot — Visión actuarial", layout="wide")
hide_streamlit_top_bar()
_inject_portal_css()


@st.dialog("Detalle del caso", width="large")
def _claim_detail_dialog(claim_id: str) -> None:
    if not claim_id:
        st.warning("Identificador de reclamo no válido.")
        return
    try:
        d = api_get(f"/api/v1/claims/{claim_id}")
    except Exception as exc:
        st.error(f"No se pudo cargar el detalle: {exc}")
        return

    st.markdown(f"### `{d.get('claim_id', claim_id)}`")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Prioridad:**", str(d.get("priority_level", "—")))
    with c2:
        st.write("**Tipo:**", d.get("claim_type") or "—")
    st.caption(_format_created_at(d.get("created_at")))
    st.markdown("#### Análisis de IA del caso")
    st.text(d.get("analyst_summary") or "(Sin resumen)")
    with st.expander("Extracción estructurada", expanded=False):
        st.json(d.get("structured_extraction") or {})
    with st.expander("Reclamo en bruto", expanded=False):
        st.json(d.get("raw_claim") or {})

summary, summary_err = _safe_summary()
claims, claims_err = _safe_recent()
last_three = (claims or [])[:3] if not claims_err and claims else []

st.markdown('<div class="portal-shell">', unsafe_allow_html=True)

# Top bar (HTML + streamlit page link row below for real navigation)
col_logo, col_nav, col_user = st.columns([2.2, 2.8, 2])

with col_logo:
    st.markdown(
        """
        <div class="portal-brand">
          <span class="shield">&#128737;</span>
          <span>Claims Intake Copilot</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_nav:
    st.markdown(
        """
        <div class="portal-nav" style="justify-content:center;">
          <span style="color:#2563eb;font-weight:600;border-bottom:2px solid #2563eb;padding-bottom:2px;">Inicio</span>
          <span style="color:#64748b;">Mis reclamos</span>
          <span style="color:#64748b;">Ayuda</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_user:
    st.markdown(
        """
        <div class="portal-user" style="justify-content:flex-end;">
          <div class="portal-bell">&#128276;<span class="badge">2</span></div>
          <div class="portal-avatar">MS</div>
          <div><strong>María Sánchez</strong><br/><span style="color:#64748b;font-size:0.85rem;">Actuaría</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.page_link("internal_ops.py", label="Operaciones internas", icon=":material/build:")

st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("### Portal de Siniestros")
st.caption(
    "Vista consolidada para seguimiento de cartera, priorización y concentración de riesgos "
    "(demo actuarial)."
)

if summary_err:
    st.error(f"No se pudo cargar el resumen: {summary_err}")
if claims_err:
    st.warning(f"Datos recientes limitados: {claims_err}")

if summary is None:
    summary = {"total_claims": 0, "alta": 0, "media": 0, "baja": 0}

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Total reclamos</div>'
        f'<div class="kpi-value">{summary["total_claims"]}</div></div>',
        unsafe_allow_html=True,
    )
with kpi2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Prioridad alta</div>'
        f'<div class="kpi-value" style="color:#b91c1c;">{summary["alta"]}</div></div>',
        unsafe_allow_html=True,
    )
with kpi3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Prioridad media</div>'
        f'<div class="kpi-value" style="color:#ea580c;">{summary["media"]}</div></div>',
        unsafe_allow_html=True,
    )
with kpi4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Prioridad baja</div>'
        f'<div class="kpi-value" style="color:#16a34a;">{summary["baja"]}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br/>", unsafe_allow_html=True)

main, aside = st.columns([2.15, 1])

with main:
    st.markdown("#### Indicadores de cartera")
    if claims and not claims_err:
        df = pd.DataFrame(claims)
        df["claim_type"] = df["claim_type"].fillna("(sin tipo)")
        by_type = df["claim_type"].value_counts()
        chart_df = by_type.rename_axis("tipo").reset_index(name="conteo")
        st.markdown('<div class="widget-card">', unsafe_allow_html=True)
        st.caption("Distribución por tipo de siniestro")
        st.bar_chart(chart_df.set_index("tipo"))
        st.markdown("</div>", unsafe_allow_html=True)

        try:
            df["_day"] = pd.to_datetime(df["created_at"], utc=True).dt.date
            by_day = df.groupby("_day").size().rename("ingresos").sort_index()
            line_df = by_day.reset_index()
            line_df["_day"] = line_df["_day"].astype(str)
            st.markdown('<div class="widget-card">', unsafe_allow_html=True)
            st.caption("Ingresos por día (UTC)")
            st.line_chart(line_df.set_index("_day"))
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception:
            st.info("No fue posible construir la serie temporal con los datos actuales.")
    else:
        st.markdown(
            '<div class="widget-card"><p style="color:#64748b;margin:0;">'
            "No hay reclamos recientes para graficar. Ejecute un intake desde "
            '<strong>Operaciones internas</strong>.</p></div>',
            unsafe_allow_html=True,
        )

with aside:
    narrative, bullets, faltantes_extra = _build_insights(summary, claims or [])
    st.markdown(
        '<div class="widget-title">&#10024; Asistente de cartera</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="widget-card">{narrative}</div>', unsafe_allow_html=True)
    for b in bullets:
        st.markdown(f"- {b}")
    if faltantes_extra:
        st.markdown('<p style="font-size:0.85rem;color:#64748b;margin:12px 0 4px 0;">Faltantes (último reclamo)</p>', unsafe_allow_html=True)
        items = "".join(f"<li>{x}</li>" for x in faltantes_extra)
        st.markdown(f'<ul class="faltantes">{items}</ul>', unsafe_allow_html=True)

    st.markdown(
        '<div class="widget-title" style="margin-top:12px;">Últimos resúmenes del analista</div>',
        unsafe_allow_html=True,
    )
    if claims_err:
        st.caption("No se pudieron cargar los resúmenes recientes.")
    elif not last_three:
        st.markdown(
            '<p style="color:#64748b;font-size:0.88rem;margin:0;">'
            "Aún no hay resúmenes para mostrar.</p>",
            unsafe_allow_html=True,
        )
    else:
        for row in last_three:
            cid = str(row.get("claim_id") or "")
            rid = row.get("id", cid)
            preview = _truncate_preview(row.get("analyst_summary"))
            lvl = row.get("priority_level") or "media"
            pcls = _prio_badge_class(lvl)
            dt_display = _format_created_at(row.get("created_at"))
            ctype = row.get("claim_type") or "—"
            lbl = str(lvl).capitalize()

            esc_cid = html.escape(cid)
            esc_meta = html.escape(f"{dt_display} · {ctype}")
            esc_preview = html.escape(preview)
            st.markdown(
                f'<div class="widget-card analyst-snippet-card">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">'
                f'<span style="font-weight:600;font-size:0.9rem;color:#0f172a;">{esc_cid}</span>'
                f'<span class="prio-badge {pcls}">{html.escape(lbl)}</span></div>'
                f'<p class="snippet-meta">{esc_meta}</p>'
                f'<p style="font-size:0.85rem;color:#475569;line-height:1.45;margin:0;white-space:pre-wrap;">'
                f"{esc_preview}</p></div>",
                unsafe_allow_html=True,
            )
            if st.button("Ver detalle del caso", key=f"detail_dlg_{rid}"):
                _claim_detail_dialog(cid)

    # Priority badge from dominant level
    dom = "media"
    if summary["total_claims"]:
        pr = Counter({"alta": summary["alta"], "media": summary["media"], "baja": summary["baja"]})
        dom = pr.most_common(1)[0][0]
    cls = {"alta": "prio-alta", "media": "prio-media", "baja": "prio-baja"}[dom]
    label = dom.capitalize()
    st.markdown(
        f'<div class="widget-card"><div class="kpi-label">Prioridad estimada (moda)</div>'
        f'<span class="prio-badge {cls}">{label}</span>'
        f'<div class="insight-box">Los umbrales son orientativos para priorizar revisión actuarial.</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="widget-title">Estado del pipeline</div>', unsafe_allow_html=True)
    steps = [
        ("Recibido", "dot-done" if summary["total_claims"] else "dot-pending"),
        ("En revisión", "dot-active" if summary["total_claims"] else "dot-pending"),
        ("Documentación / cierre", "dot-pending"),
    ]
    html_steps = ""
    for label_s, cls_d in steps:
        html_steps += f'<div class="timeline-step"><span class="timeline-dot {cls_d}"></span><span>{label_s}</span></div>'
    st.markdown(f'<div class="widget-card">{html_steps}</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
