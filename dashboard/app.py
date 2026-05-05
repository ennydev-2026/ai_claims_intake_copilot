from __future__ import annotations

import streamlit as st

pg = st.navigation(
    [
        st.Page("portal_actuary.py", title="Inicio", default=True, icon=":material/dashboard:"),
        st.Page("internal_ops.py", title="Operaciones", url_path="internal", icon=":material/build:"),
    ]
)
pg.run()
