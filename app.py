"""
Madlen Next — üç öğretmen aracı tek uygulamada.

Her araç tek başına çalışır. Aralarındaki bağ isteğe bağlı bir katman:
değerlendirme aracı bir kavram yanılgısı kaydederse, ders hazırlığı bir
sonraki planı o yanılgıyı hedefleyerek açar.
"""

import streamlit as st

import ui

PAGES = {
    "Ders Hazırlığı": "lesson_prep",
    "Öğrenci Asistanı": "chatbot",
    "Kompozisyon Değerlendirme": "essay_grader",
}

ui.setup("Ders Hazırlığı")
ui.sidebar_brand()

choice = st.sidebar.radio("Araçlar", list(PAGES.keys()), label_visibility="collapsed")

gap = st.session_state.get("class_gap")
if gap:
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='font-size:0.82rem;color:#8B7B6B'>Sınıf bağlamı</div>"
        f"<div style='font-size:0.9rem;color:#2E2622;margin-top:0.2rem'>{gap}</div>",
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Bağlamı temizle"):
        del st.session_state["class_gap"]
        st.rerun()

module = PAGES[choice]

if module == "lesson_prep":
    from tools import lesson_prep

    lesson_prep.render()
else:
    st.markdown(f"# {choice}")
    st.info("Bu araç sırada. Ders Hazırlığı şu anda kullanılabilir.")
