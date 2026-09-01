"""
Ortak model çağrı katmanı.

Üç aracın tamamı bu dosyadaki generate() ve generate_json() fonksiyonlarını
kullanır. SDK yerine doğrudan REST çağrısı yapılır: paket sürümü değişse bile
kod kırılmaz.

Anahtar .streamlit/secrets.toml içinde tutulur, asyla tarayıcıya gönderilmez.
"""

import json
import re

import requests
import streamlit as st

TIMEOUT = 90


class ModelError(Exception):
    """Kullanıcıya gösterilebilir model hatası."""


def _provider():
    """Hangi anahtar tanımlıysa o sağlayıcıyı kullan."""
    if "GEMINI_API_KEY" in st.secrets:
        return "gemini", st.secrets["GEMINI_API_KEY"]
    if "ANTHROPIC_API_KEY" in st.secrets:
        return "anthropic", st.secrets["ANTHROPIC_API_KEY"]
    raise ModelError(
        "Model anahtarı bulunamadı. .streamlit/secrets.toml içine "
        "GEMINI_API_KEY veya ANTHROPIC_API_KEY ekleyin."
    )


GEMINI_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-2.5-flash",
    "gemini-flash-latest",
]


def _gemini(key, prompt, system, temperature, max_tokens, json_mode=False):
    """
    Gemini cagrisi.

    Model adlari zaman icinde degisiyor; listedeki ilk calisan model
    kullanilir ve sonraki cagrilar icin hatirlanir.
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}

    headers = {"x-goog-api-key": key, "content-type": "application/json"}

    known = st.session_state.get("_gemini_model")
    candidates = [known] + GEMINI_MODELS if known else GEMINI_MODELS

    last = None
    for model in candidates:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{model}:generateContent"
        )
        r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        if r.status_code == 404:
            last = r
            continue
        r.raise_for_status()
        st.session_state["_gemini_model"] = model
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    if last is not None:
        last.raise_for_status()
    raise ModelError("Kullanilabilir bir model bulunamadi.")


def _anthropic(key, prompt, system, temperature, max_tokens):
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        payload["system"] = system

    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=payload,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def generate(prompt, system=None, temperature=0.4, max_tokens=4000, json_mode=False):
    """Metin uretir. Hata durumunda ModelError firlatir."""
    name, key = _provider()

    try:
        if name == "gemini":
            return _gemini(key, prompt, system, temperature, max_tokens, json_mode)
        return _anthropic(key, prompt, system, temperature, max_tokens)

    except requests.exceptions.Timeout:
        raise ModelError("Yanit zaman asimina ugradi. Tekrar deneyin.")
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        detail = ""
        try:
            detail = e.response.json().get("error", {}).get("message", "")
        except Exception:
            pass
        if code == 429:
            raise ModelError("Kullanim sinirina ulasildi. Bir dakika sonra tekrar deneyin.")
        if code in (401, 403):
            raise ModelError("API anahtari gecersiz. Anahtari kontrol edin.")
        if code == 404:
            raise ModelError(f"Model bulunamadi. {detail}".strip())
        raise ModelError(f"Model istegi basarisiz oldu (kod {code}). {detail}".strip())
    except (KeyError, IndexError):
        raise ModelError("Modelden beklenen bicimde yanit gelmedi. Tekrar deneyin.")
    except requests.exceptions.RequestException:
        raise ModelError("Baglanti kurulamadi. Internet baglantinizi kontrol edin.")


def generate_json(prompt, system=None, temperature=0.3, max_tokens=8000):
    """
    Modelden JSON ister ve parse eder.

    Model bazen JSON'u ``` bloğu içinde döndürür; ilk süslü parantezden
    sonuncuya kadar olan kısmı ayıklayarak bunu tolere ederiz.
    """
    guard = (
        "Yanıtını SADECE geçerli JSON olarak ver. Markdown kod bloğu, "
        "açıklama veya ek metin ekleme."
    )
    system = f"{system}\n\n{guard}" if system else guard

    raw = generate(
        prompt,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=True,
    )

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ModelError("Yanıt okunamadı. Lütfen tekrar oluşturun.")
