"""
Kompozisyon Değerlendirme.

Öğretmen öğrencinin metnini yapıştırır; dört ölçütte puan, metinden alıntılı
geri bildirim ve öğrenciyle paylaşılabilir bir özet döner.

Değerlendirme ayrıca tek bir öğrenme güçlüğü adlandırır. Öğretmen bunu sınıf
bağlamına aktarabilir; Ders Hazırlığı bir sonraki planı o güçlükle açar.
"""

import streamlit as st

from llm import ModelError, generate_json

MAX_CHARS = 8000

CRITERIA = ["Fikir ve içerik", "Organizasyon", "Dil ve anlatım", "Kanıt kullanımı"]

SYSTEM = """Sen Türkiye'deki K-12 öğretmenlerine kompozisyon değerlendirmesinde
yardımcı olan bir eğitim asistanısın. Geri bildirimin yapıcı, somut ve öğrencinin
yaş düzeyine uygun olsun. Övgüyü de eleştiriyi de metinden örnekle destekle.
Öğrenciyi yargılama, metni değerlendir."""

SCHEMA = """{
  "scores": [
    {"criterion": "Fikir ve içerik", "score": 0, "comment": "kısa gerekçe"},
    {"criterion": "Organizasyon", "score": 0, "comment": "..."},
    {"criterion": "Dil ve anlatım", "score": 0, "comment": "..."},
    {"criterion": "Kanıt kullanımı", "score": 0, "comment": "..."}
  ],
  "inline": [
    {"quote": "metinden birebir kısa alıntı", "note": "bu kısımla ilgili öneri"}
  ],
  "strength": "metnin en güçlü yanı, tek cümle",
  "summary_for_student": "öğrenciye doğrudan söylenebilecek 3-4 cümlelik özet",
  "learning_gap": "bu metinde öne çıkan tek bir öğrenme güçlüğü, kısa ve somut"
}"""


def render():
    from ui import page_header

    page_header(
        "Kompozisyon Değerlendirme",
        "Öğrencinin metnini yapıştırın. Dört ölçütte puan, metinden örnekli geri "
        "bildirim ve öğrenciyle paylaşabileceğiniz bir özet alırsınız.",
    )

    col1, col2 = st.columns([2, 3])
    with col1:
        grade = st.selectbox(
            "Sınıf düzeyi",
            [f"{n}. sınıf" for n in range(4, 13)],
            index=3,
            key="eg_grade",
        )
    with col2:
        assignment = st.text_input(
            "Ödev konusu (isteğe bağlı)",
            placeholder="Örnek: Okuduğunuz romanda kahramanın değişimi",
            key="eg_assignment",
        )

    essay = st.text_area(
        "Öğrencinin metni",
        height=260,
        placeholder="Öğrencinin kompozisyonunu buraya yapıştırın...",
        key="eg_essay",
    )

    if essay:
        st.caption(f"{len(essay)} karakter")

    if st.button("Değerlendir"):
        text = essay.strip()
        if len(text) < 100:
            st.warning("Değerlendirme için en az 100 karakterlik bir metin gerekiyor.")
            return
        if len(text) > MAX_CHARS:
            st.warning(
                f"Metin çok uzun ({len(text)} karakter). "
                f"Lütfen {MAX_CHARS} karakterin altına indirin."
            )
            return

        prompt = f"""Aşağıdaki öğrenci metnini değerlendir.

Sınıf düzeyi: {grade}
Ödev konusu: {assignment or "belirtilmemiş"}

Metin:
\"\"\"
{text}
\"\"\"

Kurallar:
- Dört ölçütün her birine 0-25 arası tam sayı puan ver.
- Her puana bir cümlelik somut gerekçe yaz.
- Metinden 2-3 kısa alıntı seç ve her biri için iyileştirme önerisi ver.
  Alıntılar metinde birebir geçmeli.
- Özeti öğrencinin kendisine hitap eder biçimde yaz.
- learning_gap alanına, bu öğrencinin çalışması gereken tek bir beceriyi
  somut olarak yaz. Genel ifade kullanma; "yazım hataları" değil,
  "paragraf geçişlerinde bağlaç kullanmıyor" gibi.

Şu JSON şemasına birebir uy:
{SCHEMA}"""

        with st.spinner("Metin değerlendiriliyor..."):
            try:
                result = generate_json(prompt, system=SYSTEM)
            except ModelError as e:
                st.error(str(e))
                return

        st.session_state["eg_result"] = result

    result = st.session_state.get("eg_result")
    if not result:
        return

    scores = result.get("scores", [])
    total = sum(int(s.get("score", 0)) for s in scores)

    st.markdown("---")

    head_l, head_r = st.columns([3, 1])
    with head_l:
        st.markdown("### Değerlendirme")
    with head_r:
        st.metric("Toplam", f"{total}/100")

    cols = st.columns(len(scores) if scores else 1)
    for col, s in zip(cols, scores):
        with col:
            st.markdown(
                f'<div class="m-card"><h4>{s.get("criterion", "")}</h4>'
                f'<div style="font-size:1.6rem;font-family:Zilla Slab,serif;'
                f'color:#C86A1E;font-weight:600">{s.get("score", 0)}'
                f'<span style="font-size:0.9rem;color:#8B7B6B">/25</span></div>'
                f'<div style="font-size:0.88rem;color:#5C5149;margin-top:0.4rem">'
                f'{s.get("comment", "")}</div></div>',
                unsafe_allow_html=True,
            )

    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### Metin üzerinden geri bildirim")
        for item in result.get("inline", []):
            st.markdown(
                f'<div class="m-slide">'
                f'<div style="font-style:italic;color:#5C5149;margin-bottom:0.5rem">'
                f'"{item.get("quote", "")}"</div>'
                f'<div style="font-size:0.93rem">{item.get("note", "")}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    with right:
        strength = result.get("strength")
        if strength:
            st.markdown("#### Güçlü yanı")
            st.markdown(f'<div class="m-card">{strength}</div>', unsafe_allow_html=True)

        st.markdown("#### Öğrenciyle paylaşılacak özet")
        summary = result.get("summary_for_student", "")
        st.markdown(f'<div class="m-card">{summary}</div>', unsafe_allow_html=True)
        st.download_button(
            "Özeti indir",
            data=summary,
            file_name="geri-bildirim.txt",
            mime="text/plain",
        )

    gap = result.get("learning_gap")
    if gap:
        st.markdown("---")
        st.markdown("#### Öne çıkan öğrenme güçlüğü")
        st.markdown(
            f'<div class="m-card" style="border-left:3px solid #C86A1E">'
            f"<b>{gap}</b><br><span style='color:#8B7B6B;font-size:0.9rem'>"
            "Bu güçlüğü sınıf bağlamına aktarırsanız, Ders Hazırlığı bir sonraki "
            "planı buna ayrılmış kısa bir girişle açar.</span></div>",
            unsafe_allow_html=True,
        )
        if st.button("Ders hazırlığına aktar"):
            st.session_state["class_gap"] = gap
            st.success("Sınıf bağlamına eklendi. Ders Hazırlığı sayfasında görünecek.")
