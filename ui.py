"""
Ortak görsel dil.

Streamlit'in varsayılan görünümü bir veri aracına benziyor. Buradaki CSS,
arayüzü öğretmenin yabancılık çekmeyeceği bir ürüne yaklaştırmak için var:
Madlen'in krem/turuncu paleti, başlıklarda slab serif, gövdede sans.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --cream: #FDF6EC;
  --surface: #FFFFFF;
  --ink: #2E2622;
  --muted: #8B7B6B;
  --orange: #C86A1E;
  --line: #E9D9C3;
}

#MainMenu, footer, header [data-testid="stStatusWidget"] { visibility: hidden; }
footer { display: none; }

html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

h1, h2, h3, .m-display {
  font-family: 'Zilla Slab', Georgia, serif !important;
  color: var(--ink);
  letter-spacing: -0.01em;
}

section[data-testid="stSidebar"] {
  background: #FFFDF9;
  border-right: 1px solid var(--line);
}

.m-brand {
  font-family: 'Zilla Slab', Georgia, serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--orange);
  margin: 0.2rem 0 0.1rem 0;
}

.m-brand-sub {
  font-size: 0.82rem;
  color: var(--muted);
  margin-bottom: 1.4rem;
  line-height: 1.45;
}

.m-lede {
  color: var(--muted);
  font-size: 0.97rem;
  line-height: 1.6;
  max-width: 62ch;
  margin-bottom: 1.6rem;
}

.m-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 1.15rem 1.3rem;
  margin-bottom: 0.85rem;
}

.m-card h4 {
  font-family: 'Zilla Slab', Georgia, serif;
  font-size: 1.05rem;
  margin: 0 0 0.5rem 0;
  color: var(--ink);
}

.m-slide {
  background: var(--surface);
  border: 1px solid var(--line);
  border-left: 3px solid var(--orange);
  border-radius: 8px;
  padding: 1rem 1.2rem;
  margin-bottom: 0.7rem;
}

.m-slide-n {
  font-size: 0.78rem;
  color: var(--orange);
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.m-slide h4 {
  font-family: 'Zilla Slab', Georgia, serif;
  font-size: 1.02rem;
  margin: 0 0 0.55rem 0;
}

.m-slide ul { margin: 0 0 0.6rem 1.1rem; padding: 0; }
.m-slide li { margin-bottom: 0.28rem; font-size: 0.93rem; line-height: 1.5; }

.m-visual {
  font-size: 0.85rem;
  color: var(--muted);
  border-top: 1px dashed var(--line);
  padding-top: 0.5rem;
  margin-top: 0.5rem;
}

.m-chip {
  display: inline-block;
  background: #F6E8D6;
  color: #8A4E12;
  border-radius: 20px;
  padding: 0.18rem 0.7rem;
  font-size: 0.8rem;
  font-weight: 500;
  margin: 0 0.35rem 0.35rem 0;
}

.stButton > button {
  background: var(--orange);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  padding: 0.55rem 1.4rem;
}

.stButton > button:hover { background: #B25C15; color: #fff; }

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
  border-radius: 8px !important;
  border-color: var(--line) !important;
}

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
</style>
"""


def setup(title):
    st.set_page_config(
        page_title=f"{title} · Madlen Next",
        page_icon="◉",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown('<div class="m-brand">Madlen Next</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="m-brand-sub">Öğrencinin nerede takıldığını görün, '
        "bir sonraki dersi ona göre kurun.</div>",
        unsafe_allow_html=True,
    )


def page_header(title, lede):
    st.markdown(f"# {title}")
    st.markdown(f'<div class="m-lede">{lede}</div>', unsafe_allow_html=True)
