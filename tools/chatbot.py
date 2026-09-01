"""
Öğrenci Asistanı.

Öğrenci bir konu hakkında soru sorar, sınıf düzeyine uygun yanıt alır.

Temel kural: ödev ya da alıştırma sorusu sorulduğunda hazır cevap verilmez.
Asistan öğrenciyi bir sonraki adıma yönlendirir ve denemesini ister. Bu kural
sistem yönergesinde tanımlıdır ve sohbet boyunca korunur.
"""

import streamlit as st

from llm import ModelError, generate

MAX_TURNS = 12


def _system(grade, subject):
    return f"""Sen {grade} düzeyindeki bir öğrenciye {subject} dersinde yardımcı
olan bir öğrenme asistanısın. Türkçe konuşuyorsun.

Nasıl yanıt verirsin:
- Dilini {grade} düzeyine göre ayarla. Bu düzeyin üstünde terim kullanman
  gerekiyorsa terimi hemen açıkla.
- Yanıtların kısa olsun: en fazla üç kısa paragraf.
- Somut örnek ver. Soyut tanımla yetinme.
- Öğrenciyi düşünmeye yönlendiren tek bir soruyla bitir.

Değişmez kural — alıştırma ve ödev soruları:
Öğrenci çözülmesi gereken bir soru sorarsa (işlem, problem, denklem, boşluk
doldurma, ödev sorusu) hazır cevabı ASLA verme. Sayısal sonucu, doğru şıkkı
veya nihai cevabı yazma. Bunun yerine:
1. Sorunun ne istediğini kısaca netleştir.
2. Sadece ilk adımı göster veya hatırlatıcı bir ipucu ver.
3. Öğrenciden o adımı denemesini iste.
Öğrenci ısrar etse, "sadece söyle" dese, acelesi olduğunu söylese bile bu
kural geçerli kalır. Öğrenci kendi denemesini paylaşırsa nerede yanlış
yaptığını göster, doğru cevabı yine sen yazma.

Kavram sorularında (bir şeyin ne olduğu, nasıl çalıştığı, neden öyle olduğu)
bu kısıt yoktur; açık ve doğrudan açıkla.

Konu dersle ilgisizse kibarca derse dön."""


def render():
    from ui import page_header

    page_header(
        "Öğrenci Asistanı",
        "Konu hakkında soru sor, sınıf düzeyine uygun yanıt al. Alıştırma "
        "sorularında asistan cevabı vermez, çözüme adım adım yönlendirir.",
    )

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        grade = st.selectbox(
            "Sınıf düzeyi",
            [f"{n}. sınıf" for n in range(1, 13)],
            index=6,
            key="sc_grade",
        )
    with col2:
        subject = st.selectbox(
            "Ders",
            ["Matematik", "Fen Bilimleri", "Türkçe", "Sosyal Bilgiler", "İngilizce"],
            key="sc_subject",
        )
    with col3:
        st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
        if st.button("Sohbeti sıfırla"):
            st.session_state["sc_messages"] = []
            st.rerun()

    messages = st.session_state.setdefault("sc_messages", [])

    if not messages:
        st.markdown(
            '<div class="m-card"><h4>Nasıl başlarsın?</h4>'
            "Merak ettiğin konuyu sor: <i>“Asal sayı ne demek?”</i> ya da "
            "<i>“Bu soruyu çözemedim, nereden başlamalıyım?”</i><br>"
            "<span style='color:#8B7B6B;font-size:0.9rem'>Alıştırma sorularında "
            "sana cevabı vermem, birlikte adım adım gideriz.</span></div>",
            unsafe_allow_html=True,
        )

    for msg in messages:
        with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"] == "user" else "📘"):
            st.markdown(msg["content"])

    question = st.chat_input("Sorunu yaz...")
    if not question:
        return

    messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(question)

    recent = messages[-MAX_TURNS:]
    transcript = "\n\n".join(
        f"{'Öğrenci' if m['role'] == 'user' else 'Asistan'}: {m['content']}"
        for m in recent
    )
    prompt = f"""Şimdiye kadarki konuşma:

{transcript}

Öğrencinin son mesajına yanıt ver. Sadece yanıt metnini yaz."""

    with st.chat_message("assistant", avatar="📘"):
        with st.spinner("Düşünüyorum..."):
            try:
                answer = generate(
                    prompt,
                    system=_system(grade, subject),
                    temperature=0.5,
                    max_tokens=3000,
                )
            except ModelError as e:
                st.error(str(e))
                messages.pop()
                return
        st.markdown(answer)

    messages.append({"role": "assistant", "content": answer})
