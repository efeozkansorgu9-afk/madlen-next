"""
Ders Hazırlık Asistanı.

Öğretmen konu ve sınıf düzeyi girer; kazanımlar, beş slaytlık ders akışı ve
tartışma soruları döner. Sınıf bağlamında kayıtlı bir kavram yanılgısı varsa
plan onu hedefleyen kısa bir girişle başlar.
"""

import streamlit as st

from llm import ModelError, generate_json

SYSTEM = """Sen Türkiye'deki K-12 öğretmenleri için ders planı hazırlayan bir
eğitim asistanısın. MEB müfredatının dilini ve kazanım mantığını kullan.
Planlar sınıf içinde uygulanabilir, somut ve zaman sınırlı olsun.
Genel geçer ifadeler yerine konuya özgü örnekler ver."""

SCHEMA = """{
  "objectives": ["kazanım cümlesi", "..."],
  "opening": "dersin ilk dakikaları için kısa açılış önerisi",
  "slides": [
    {"title": "slayt başlığı",
     "bullets": ["madde", "madde", "madde"],
     "visual": "bu slayt için görsel önerisi"}
  ],
  "discussion": ["tartışma sorusu", "..."],
  "exit_check": ["çıkış kontrolü sorusu", "..."]
}"""


def render():
    from ui import page_header

    page_header(
        "Ders Hazırlığı",
        "Konuyu ve sınıf düzeyini girin, uygulanabilir bir ders planı alın. "
        "Değerlendirme aracında bir kavram yanılgısı kaydedildiyse plan onunla başlar.",
    )

    gap = st.session_state.get("class_gap")
    if gap:
        st.markdown(
            f'<div class="m-card"><h4>Sınıf bağlamı</h4>'
            f"Son değerlendirmede öne çıkan güçlük: <b>{gap}</b><br>"
            "<span style='color:#8B7B6B;font-size:0.9rem'>"
            "Plan bu güçlüğü hedefleyen beş dakikalık bir girişle açılacak."
            "</span></div>",
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([3, 2])
    with col1:
        topic = st.text_input(
            "Konu",
            placeholder="Örnek: Birinci dereceden denklemler",
        )
    with col2:
        grade = st.selectbox(
            "Sınıf düzeyi",
            [f"{n}. sınıf" for n in range(1, 13)],
            index=6,
        )

    col3, col4 = st.columns([2, 3])
    with col3:
        duration = st.selectbox("Ders süresi", ["40 dakika", "60 dakika", "80 dakika"])
    with col4:
        notes = st.text_input(
            "Eklemek istediğiniz not (isteğe bağlı)",
            placeholder="Örnek: Sınıfta görsel materyal kullanmayı tercih ediyorum",
        )

    if st.button("Ders planı oluştur"):
        if not topic.strip():
            st.warning("Devam etmek için bir konu yazın.")
            return

        prompt = f"""Aşağıdaki ders için plan hazırla.

Konu: {topic}
Sınıf düzeyi: {grade}
Süre: {duration}
Öğretmen notu: {notes or "yok"}
Sınıfta gözlenen güçlük: {gap or "kayıt yok"}

Kurallar:
- Tam 5 slayt üret, her slaytta 3-4 madde olsun.
- 3 kazanım, 3 tartışma sorusu, 3 çıkış kontrolü sorusu yaz.
- Sınıfta gözlenen bir güçlük varsa açılışı ona ayır.
- Çıkış kontrolü soruları kazanımları ölçsün, kısa cevaplı olsun.

Şu JSON şemasına birebir uy:
{SCHEMA}"""

        with st.spinner("Ders planınız hazırlanıyor..."):
            try:
                plan = generate_json(prompt, system=SYSTEM)
            except ModelError as e:
                st.error(str(e))
                return

        st.session_state["lesson_plan"] = plan
        st.session_state["lesson_meta"] = {"topic": topic, "grade": grade}

    plan = st.session_state.get("lesson_plan")
    if not plan:
        return

    meta = st.session_state.get("lesson_meta", {})
    st.markdown("---")
    st.markdown(f"### {meta.get('topic', 'Ders planı')} · {meta.get('grade', '')}")

    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### Ders akışı")
        opening = plan.get("opening")
        if opening:
            st.markdown(
                f'<div class="m-card"><h4>Açılış</h4>{opening}</div>',
                unsafe_allow_html=True,
            )

        for i, slide in enumerate(plan.get("slides", []), start=1):
            bullets = "".join(f"<li>{b}</li>" for b in slide.get("bullets", []))
            visual = slide.get("visual", "")
            st.markdown(
                f'<div class="m-slide">'
                f'<div class="m-slide-n">Slayt {i}</div>'
                f'<h4>{slide.get("title", "")}</h4>'
                f"<ul>{bullets}</ul>"
                f'<div class="m-visual">Görsel önerisi: {visual}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("#### Kazanımlar")
        for o in plan.get("objectives", []):
            st.markdown(f'<div class="m-chip">{o}</div>', unsafe_allow_html=True)

        st.markdown("#### Tartışma soruları")
        for q in plan.get("discussion", []):
            st.markdown(f'<div class="m-card">{q}</div>', unsafe_allow_html=True)

        st.markdown("#### Çıkış kontrolü")
        for q in plan.get("exit_check", []):
            st.markdown(f'<div class="m-card">{q}</div>', unsafe_allow_html=True)

    st.download_button(
        "Planı indir",
        data=_as_text(plan, meta),
        file_name="ders-plani.txt",
        mime="text/plain",
    )


def _as_text(plan, meta):
    lines = [f"{meta.get('topic', '')} — {meta.get('grade', '')}", ""]
    lines.append("KAZANIMLAR")
    lines += [f"- {o}" for o in plan.get("objectives", [])]
    lines += ["", "AÇILIŞ", plan.get("opening", ""), "", "DERS AKIŞI"]
    for i, s in enumerate(plan.get("slides", []), start=1):
        lines.append(f"\nSlayt {i}: {s.get('title', '')}")
        lines += [f"  - {b}" for b in s.get("bullets", [])]
        lines.append(f"  Görsel: {s.get('visual', '')}")
    lines += ["", "TARTIŞMA SORULARI"]
    lines += [f"- {q}" for q in plan.get("discussion", [])]
    lines += ["", "ÇIKIŞ KONTROLÜ"]
    lines += [f"- {q}" for q in plan.get("exit_check", [])]
    return "\n".join(lines)
