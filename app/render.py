from __future__ import annotations
import streamlit as st
from typing import Dict, List


def _render_list(title: str, items: List[str]) -> None:
    st.markdown(f"### {title}")
    for x in items:
        st.write(f"- {x}")


import streamlit as st

def render_passport(passport: dict) -> None:
    st.markdown("## AI-Аудит процесса")

    st.markdown(
        f"**Оценка готовности искусственного интеллекта:** {passport.get('ai_score', '—')} / 100  \n"
        f"**Уровень зрелости процесса:** {passport.get('maturity_level', '—')} / 5"
    )

    def render_list(title: str, items):
        st.markdown(f"### {title}")
        if not items:
            st.markdown("- —")
            return
        for x in items:
            st.markdown(f"- {x}")

    render_list("Участники", passport.get("participants", []))
    render_list("Документы", passport.get("documents", []))
    render_list("Этапы", passport.get("stages", []))
    render_list("Риски", passport.get("risks", []))
    render_list("Узкие места", passport.get("bottlenecks", []))
    render_list("Рекомендации", passport.get("recommendations", []))
