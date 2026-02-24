import streamlit as st
from app.pipeline import run_offline_brief_and_passport, run_api_audit

st.set_page_config(page_title="AI Business Process Auditor", layout="wide")
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
st.title("AI Business Process Auditor")

text = st.text_area(
    "Вставьте описание процесса",
    height=220,
    placeholder="Опишите процесс (участники, документы, этапы, риски, узкие места)...",
)

st.divider()

if "offline_md" not in st.session_state:
    st.session_state.offline_md = ""
if "api_md" not in st.session_state:
    st.session_state.api_md = ""

st.markdown("""
### Логика работы AI-аудита

Паспорт процесса  
↓  
Диагностика (внутренний анализ AI)  
↓  
Формирование аудиторского отчёта
""")

left, right = st.columns(2, gap="large")

with left:
    st.subheader("Базовый аудит процесса")
    if st.button("Сформировать базовый аудит", type="primary", use_container_width=True):
        t = (text or "").strip()
        if not t:
            st.error("Пустой ввод. Вставьте описание процесса.")
        else:
            passport_md, _passport = run_offline_brief_and_passport(t)
            st.session_state.offline_md = passport_md

    st.caption("Результат базового аудита")
    with st.container(height=560, border=True):
        st.markdown(st.session_state.offline_md or "—")

with right:
    st.subheader("API аудит процесса")

    if st.button("Сформировать API аудит", type="secondary", use_container_width=True):
        t = (text or "").strip()
        if not t:
            st.error("Пустой ввод. Вставьте описание процесса.")
        else:
            with st.spinner("Формирую API-отчёт..."):
                st.session_state.api_md = run_api_audit(t)

    st.caption("Результат API аудита")
    with st.container(height=560, border=True):
        st.markdown(st.session_state.api_md or "—")

    # КНОПКА СКАЧИВАНИЯ — строго после контейнера
    if st.session_state.api_md:
        st.download_button(
            label="Скачать API-отчёт (MD)",
            data=st.session_state.api_md,
            file_name="api_audit_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

