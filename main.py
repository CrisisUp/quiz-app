"""
Quiz Interativo — Servidor FastAPI com síntese de voz (edge-tts) e renderização LaTeX (KaTeX).
Execução: uvicorn main:app --reload --port 8000
"""

import json
import re
from pathlib import Path

import edge_tts
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Quiz Interativo", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
QUESTOES_PATH = BASE_DIR / "questoes.json"


# ---------------------------------------------------------------------------
#  Sanitizador Regex de LaTeX para Fala (pt-BR)
# ---------------------------------------------------------------------------

_GREEK_MAP: dict[str, str] = {
    r"\alpha": "alfa",
    r"\beta": "beta",
    r"\gamma": "gama",
    r"\delta": "delta",
    r"\Delta": "delta maiúsculo",
    r"\epsilon": "épsilon",
    r"\zeta": "zeta",
    r"\eta": "eta",
    r"\theta": "teta",
    r"\Theta": "teta maiúsculo",
    r"\iota": "iota",
    r"\kappa": "kapa",
    r"\lambda": "lambda",
    r"\Lambda": "lambda maiúsculo",
    r"\mu": "mi",
    r"\nu": "ni",
    r"\xi": "xi",
    r"\Xi": "xi maiúsculo",
    r"\pi": "pi",
    r"\Pi": "pi maiúsculo",
    r"\rho": "ro",
    r"\sigma": "sigma",
    r"\Sigma": "sigma maiúsculo",
    r"\tau": "tau",
    r"\phi": "fi",
    r"\Phi": "fi maiúsculo",
    r"\chi": "qui",
    r"\psi": "psi",
    r"\Psi": "psi maiúsculo",
    r"\omega": "ômega",
    r"\Omega": "ômega maiúsculo",

    # Funções trigonométricas e hiperbólicas
    r"\sin": "seno",
    r"\cos": "cosseno",
    r"\tan": "tangente",
    r"\sec": "secante",
    r"\csc": "cossecante",
    r"\cot": "cotangente",
    r"\arcsin": "arco seno",
    r"\arccos": "arco cosseno",
    r"\arctan": "arco tangente",
    r"\sinh": "seno hiperbólico",
    r"\cosh": "cosseno hiperbólico",
    r"\tanh": "tangente hiperbólica",
}


def _sanitize_latex_for_speech(text: str) -> str:
    """Traduz expressões LaTeX em notação matemática para fala em pt-BR."""

    # 1. Remover delimitadores KaTeX
    out = re.sub(r"\$\$(.+?)\$\$", r"\1", text, flags=re.DOTALL)
    out = re.sub(r"\$(.+?)\$", r"\1", out)

    # 2. Remover environments LaTeX (aligned, cases …)
    out = re.sub(r"\\begin\{[^}]+\}", "", out)
    out = re.sub(r"\\end\{[^}]+\}", "", out)

    # 2b. Remover \text{...} mantendo o conteúdo (deve vir ANTES de \frac)
    out = re.sub(r"\\text\{([^{}]+)\}", r"\1", out)

    # 3. Comandos com dois argumentos: \frac{a}{b} \to "a sobre b"
    out = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1 sobre \2", out)

    # 4. Comandos com um argumento: \sqrt{x} \to "raiz quadrada de x"
    out = re.sub(r"\\sqrt\{([^{}]+)\}", r"raiz quadrada de \1", out)

    # 5. Subscritos: x_{10} ou x_1  →  "x índice 10"
    out = re.sub(
        r"([A-Za-z0-9])_\{([^{}]+)\}",
        r"\1 índice \2",
        out,
    )
    out = re.sub(r"([A-Za-z0-9])_(\w)", r"\1 índice \2", out)

    # 6. Potências: x^{2} ou x^2  →  "x ao quadrado" / "x elevado a …"
    def _power_repl(m: re.Match) -> str:
        base, exp = m.group(1), m.group(2)
        mapping = {"2": "ao quadrado", "3": "ao cubo"}
        return f"{base} {mapping.get(exp, f'elevado a {exp}')}"

    out = re.sub(r"([A-Za-z0-9])\^\{([^{}]+)\}", _power_repl, out)
    out = re.sub(r"([A-Za-z0-9])\^(\w)", _power_repl, out)

    # 7. Letras gregas
    for cmd, spoken in sorted(_GREEK_MAP.items(), key=lambda x: -len(x[0])):
        out = out.replace(cmd, spoken)

    # 8. Operadores e símbolos
    symbol_map = [
        (r"\cdot", " vezes "),
        (r"\times", " vezes "),
        (r"\div", " dividido "),
        (r"\pm", " mais ou menos "),
        (r"\mp", " menos ou mais "),
        (r"\neq", " diferente de "),
        (r"\ne", " diferente de "),
        (r"\leq", " menor ou igual a "),
        (r"\le", " menor ou igual a "),
        (r"\geq", " maior ou igual a "),
        (r"\ge", " maior ou igual a "),
        (r"\approx", " aproximadamente igual a "),
        (r"\equiv", " equivalente a "),
        (r"\infty", " infinito "),
        (r"\pi", " pi "),
        (r"\%", " por cento "),
        (r"/", " dividido "),
        (r"\-", " menos "),
        (r"-", " menos "),
        (r"'", " linha "),
        (r"\prime", " linha "),
    ]
    for pattern, spoken in symbol_map:
        out = out.replace(pattern, spoken)

    # 9. Limpar resíduos
    out = re.sub(r"\\[a-zA-Z]+", "", out)          # comandos não mapeados
    out = re.sub(r"[{}]", " ", out)                  # chaves restantes
    out = re.sub(r"\s{2,}", " ", out).strip()        # espaços múltiplos

    return out


# ---------------------------------------------------------------------------
#  Endpoints da API
# ---------------------------------------------------------------------------

@app.get("/api/questoes")
async def get_questoes():
    """Retorna todas as questões do quiz."""
    raw = QUESTOES_PATH.read_text(encoding="utf-8")
    return json.loads(raw)


@app.get("/api/tts")
async def tts(texto: str = Query(..., description="Texto para síntese de voz")):
    """Gera áudio MP3 completo via edge-tts (voz pt-BR-FranciscaNeural)."""
    texto_limpo = _sanitize_latex_for_speech(texto)

    # Pausa explícita ANTES e DEPOIS de "menos" para forçar pronúncia
    # (testes mostram que pontuação forte gera ~32KB vs 25KB sem)
    texto_limpo = texto_limpo.replace(" menos ", " ... menos ... ")

    communicate = edge_tts.Communicate(texto_limpo, "pt-BR-FranciscaNeural")
    audio_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])

    return StreamingResponse(
        iter([bytes(audio_data)]),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-cache",
            "Content-Length": str(len(audio_data)),
            "Content-Disposition": "inline; filename=\"tts.mp3\"",
        },
    )


# ---------------------------------------------------------------------------
#  Favicon (evita 404 no console)
# ---------------------------------------------------------------------------

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon", status_code=204)


# ---------------------------------------------------------------------------
#  SPA — index.html no root
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    index_html = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_html.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Arquivos estáticos (deve ser o ÚLTIMO — catch-all de /static)
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
