"""CSS complementario para ocultar el chrome superior de Streamlit en deploy.

Usar solo después de st.set_page_config en cada página (no en app.py antes de pg.run).
"""

from __future__ import annotations

import streamlit as st

# Refuerzo visual: la barra superior (logo Streamlit + toolbar) queda fuera del layout.
_HIDE_HEADER_CSS = """
<style>
    header[data-testid="stHeader"] {
        display: none !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    .block-container {
        padding-top: 1rem !important;
    }
</style>
"""


def hide_streamlit_top_bar() -> None:
    st.markdown(_HIDE_HEADER_CSS, unsafe_allow_html=True)
