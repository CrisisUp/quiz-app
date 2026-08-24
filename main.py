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
    # Letras gregas
    r"\alpha": "alfa",
    r"\beta": "beta",
    r"\gamma": "gama",
    r"\delta": "delta",
    r"\Delta": "delta maiúsculo",
    r"\epsilon": "épsilon",
    r"\varepsilon": "épsilon",
    r"\zeta": "zeta",
    r"\eta": "eta",
    r"\theta": "teta",
    r"\vartheta": "teta",
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
    r"\varpi": "pi",
    r"\Pi": "pi maiúsculo",
    r"\rho": "ro",
    r"\varrho": "ro",
    r"\sigma": "sigma",
    r"\varsigma": "sigma",
    r"\Sigma": "sigma maiúsculo",
    r"\tau": "tau",
    r"\phi": "fi",
    r"\varphi": "fi",
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

    # Logaritmos
    r"\log": "logaritmo",
    r"\ln": "logaritmo natural",
    r"\lg": "logaritmo base 10",
    r"\log_": "logaritmo base ",

    # Funções elementares
    r"\exp": "exponencial",
    r"\lim": "limite",
    r"\limsup": "limite superior",
    r"\liminf": "limite inferior",
    r"\max": "máximo",
    r"\min": "mínimo",
    r"\sup": "supremo",
    r"\inf": "ínfimo",
    r"\det": "determinante",
    r"\tr": "traço",
    r"\dim": "dimensão",
    r"\ker": "núcleo",
    r"\im": "imagem",
    r"\deg": "grau",
    r"\arg": "argumento",
    r"\Re": "parte real",
    r"\Im": "parte imaginária",

    # Operadores grandes (somatórios, integrais, etc.)
    r"\sum": "soma",
    r"\prod": "produto",
    r"\int": "integral",
    r"\iint": "integral dupla",
    r"\iiint": "integral tripla",
    r"\oint": "integral de contorno",
    r"\coprod": "coproduto",
    r"\bigoplus": "soma direta",
    r"\bigotimes": "produto tensorial",
    r"\bigcup": "união",
    r"\bigcap": "interseção",
    r"\bigsqcup": "união disjunta",
    r"\bigvee": "ou lógico",
    r"\bigwedge": "e lógico",

    # Conjuntos numéricos comuns
    r"\mathbb{R}": "R",
    r"\mathbb{N}": "N",
    r"\mathbb{Z}": "Z",
    r"\mathbb{Q}": "Q",
    r"\mathbb{C}": "C",
    r"\mathbb{H}": "H",
    r"\mathbb{P}": "P",
    r"\mathcal": "caligráfico ",
    r"\mathfrak": "gótico ",
    r"\mathbf": "negrito ",
    r"\mathrm": "romano ",
    r"\mathit": "itálico ",

    # Derivadas parciais
    r"\partial": "parcial",

    # Raízes enésimas
    r"\sqrt[": "raiz índice ",

    # Binomial
    r"\binom": "binomial",
    r"\choose": "escolher",

    # Fatorial
    r"\!": "",  # espaço negativo - ignorar

    # Unidades SI comuns (para conversão antes do / genérico)
    r"\meter": "metro",
    r"\metre": "metro",
    r"\m": "metro",
    r"\second": "segundo",
    r"\s": "segundo",
    r"\kilogram": "quilograma",
    r"\kg": "quilograma",
    r"\gram": "grama",
    r"\g": "grama",
    r"\newton": "newton",
    r"\N": "newton",
    r"\joule": "joule",
    r"\J": "joule",
    r"\watt": "watt",
    r"\W": "watt",
    r"\coulomb": "coulomb",
    r"\C": "coulomb",
    r"\volt": "volt",
    r"\V": "volt",
    r"\ampere": "ampere",
    r"\A": "ampere",
    r"\ohm": "ohm",
    r"\farad": "farad",
    r"\F": "farad",
    r"\henry": "henry",
    r"\H": "henry",
    r"\hertz": "hertz",
    r"\Hz": "hertz",
    r"\pascal": "pascal",
    r"\Pa": "pascal",
    r"\lumen": "lumen",
    r"\lm": "lumen",
    r"\lux": "lux",
    r"\lx": "lux",
    r"\becquerel": "becquerel",
    r"\Bq": "becquerel",
    r"\gray": "gray",
    r"\Gy": "gray",
    r"\sievert": "sievert",
    r"\Sv": "sievert",
    r"\katal": "katal",
    r"\kat": "katal",
    r"\degree": "grau",
    r"\celsius": "grau celsius",
    r"\Celsius": "grau celsius",
    r"\kelvin": "kelvin",
    r"\K": "kelvin",
    r"\mole": "mol",
    r"\mol": "mol",
    r"\candela": "candela",
    r"\cd": "candela",
}


def _sanitize_latex_for_speech(text: str) -> str:
    """Traduz expressões LaTeX em notação matemática para fala em pt-BR."""

    # 1. Remover delimitadores KaTeX
    out = re.sub(r"\$\$(.+?)\$\$", r"\1", text, flags=re.DOTALL)
    out = re.sub(r"\$(.+?)\$", r"\1", out)

    # 2. Remover environments LaTeX (aligned, cases, matrix, array, etc.)
    # Captura ambientes de matriz antes de remover
    out = re.sub(r"\\begin\{(p|b|B|v|V|small)matrix\}", "", out)
    out = re.sub(r"\\end\{(p|b|B|v|V|small)matrix\}", "", out)
    # Remove outros environments
    out = re.sub(r"\\begin\{[^}]+\}", "", out)
    out = re.sub(r"\\end\{[^}]+\}", "", out)

    # 2b. Remover & e \\ de matrizes
    out = re.sub(r"&", " , ", out)
    out = re.sub(r"\\\\", " ; ", out)

    # 2b. Remover \text{...} mantendo o conteúdo (deve vir ANTES de \frac)
    out = re.sub(r"\\text\{([^{}]+)\}", r"\1", out)

    # 2c. Remover \left / \right
    out = re.sub(r"\\left", "", out)
    out = re.sub(r"\\right", "", out)

    # 2d. Norma: \|x\| -> "norma de x" (antes do symbol_map para não duplicar)
    out = re.sub(r"\\\|([^|]+)\\\|", r"norma de \1", out)

    # 2e. Produto interno: \langle u, v \rangle -> "produto interno de u e v"
    out = re.sub(r"\\langle\s*([^,]+)\s*,\s*([^>]+)\s*\\rangle", r"produto interno de \1 e \2", out)

    # 2f. \pmod / \mod -> "módulo n"
    out = re.sub(r"\\pmod\s*\{([^}]+)\}", r"módulo \1", out)
    out = re.sub(r"\\pmod\s+([a-zA-Z0-9]+)", r"módulo \1", out)
    out = re.sub(r"\\mod\s+([a-zA-Z0-9]+)", r"módulo \1", out)

    # 2d. Raízes enésimas: \sqrt[n]{x} -> "raiz índice n de x"
    out = re.sub(r"\\sqrt\[([^\]]+)\]\{([^{}]+)\}", r"raiz índice \1 de \2", out)

    # 2e. Binomial: \binom{n}{k} -> "binomial n k"
    out = re.sub(r"\\binom\{([^{}]+)\}\{([^{}]+)\}", r"binomial \1 \2", out)
    out = re.sub(r"\\choose\{([^{}]+)\}\{([^{}]+)\}", r"\1 escolher \2", out)

    # 2f. Logaritmos com base: \log_a b -> "logaritmo de b na base a"
    out = re.sub(r"\\log_\{?([^{}]+)\}?\s*([a-zA-Z0-9]+)", r"logaritmo de \2 na base \1", out)
    out = re.sub(r"\\log\s+([a-zA-Z0-9]+)", r"logaritmo de \1", out)
    out = re.sub(r"\\ln\s+([a-zA-Z0-9]+)", r"logaritmo natural de \1", out)
    out = re.sub(r"\\lg\s+([a-zA-Z0-9]+)", r"logaritmo base 10 de \1", out)

    # 2g. Limites: \lim_{x \to a} -> "limite quando x tende a a"
    out = re.sub(r"\\lim_\{([^}]+)\}", r"limite quando \1", out)
    out = re.sub(r"\\lim\s+", "limite ", out)

    # 2h. Integrais com limites: \int_a^b -> "integral de a até b"
    out = re.sub(r"\\int_\{([^}]+)\}\^\{([^}]+)\}", r"integral de \1 até \2", out)
    out = re.sub(r"\\int_([^ ]+)\^([^ ]+)", r"integral de \1 até \2", out)
    out = re.sub(r"\\iint", "integral dupla", out)
    out = re.sub(r"\\iiint", "integral tripla", out)
    out = re.sub(r"\\oint", "integral de contorno", out)
    out = re.sub(r"\\int", "integral", out)

    # 2i. Somatórios com limites: \sum_{i=1}^n -> "soma de i igual a 1 até n"
    out = re.sub(r"\\sum_\{([^}]+)\}\^\{([^}]+)\}", r"soma de \1 até \2", out)
    out = re.sub(r"\\sum_([^ ]+)\^([^ ]+)", r"soma de \1 até \2", out)
    out = re.sub(r"\\sum", "soma", out)
    out = re.sub(r"\\prod_\{([^}]+)\}\^\{([^}]+)\}", r"produto de \1 até \2", out)
    out = re.sub(r"\\prod", "produto", out)

    # 2j. Derivadas parciais: \frac{\partial f}{\partial x} -> "parcial f sobre parcial x"
    # (o \frac já trata, só garantir que \partial -> "parcial")

    # 3. Comandos com dois argumentos: \frac{a}{b} -> "a sobre b"
    out = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1 sobre \2", out)

    # 3b. Unidades compostas (antes do / genérico)
    # Padrões comuns: m/s, km/h, kg*m/s^2, N*m, J/s, etc.
    # Substitui unidades conhecidas antes de processar / genérico
    unit_patterns = [
        # Temperatura (antes de C genérico)
        (r"°\s*C", "graus celsius"),
        # Aceleração
        (r"m\s*/\s*s\s*\^\s*2", "metros por segundo ao quadrado"),
        (r"m\s*/\s*s\s*\^2", "metros por segundo ao quadrado"),
        (r"m\/s\^2", "metros por segundo ao quadrado"),
        (r"kg\s*\*\s*m\s*/\s*s\s*\^\s*2", "newton"),  # kg*m/s^2 = N
        # Velocidade
        (r"m\s*/\s*s", "metros por segundo"),
        (r"km\s*/\s*h", "quilômetros por hora"),
        (r"cm\s*/\s*s", "centímetros por segundo"),
        # Força/Energia/Potência
        (r"N\s*\*\s*m", "newton metro"),
        (r"J\s*/\s*s", "watts"),  # J/s = W
        # Unidades simples COM NÚMERO antes (ex: "10 N", "5 m/s")
        (r"(\d+(?:\.\d+)?)\s*m\b", r"\1 metros"),
        (r"(\d+(?:\.\d+)?)\s*kg\b", r"\1 quilogramas"),
        (r"(\d+(?:\.\d+)?)\s*s\b", r"\1 segundos"),
        (r"(\d+(?:\.\d+)?)\s*W\b", r"\1 watts"),
        (r"(\d+(?:\.\d+)?)\s*Pa\b", r"\1 pascals"),
        (r"(\d+(?:\.\d+)?)\s*Hz\b", r"\1 hertz"),
        (r"(\d+(?:\.\d+)?)\s*K\b", r"\1 kelvin"),
        (r"(\d+(?:\.\d+)?)\s*C\b", r"\1 coulombs"),
        (r"(\d+(?:\.\d+)?)\s*mol\b", r"\1 mol"),
        (r"(\d+(?:\.\d+)?)\s*N\b", r"\1 newtons"),
        (r"(\d+(?:\.\d+)?)\s*J\b", r"\1 joules"),
        (r"(\d+(?:\.\d+)?)\s*V\b", r"\1 volts"),
        (r"(\d+(?:\.\d+)?)\s*A\b", r"\1 amperes"),
        (r"(\d+(?:\.\d+)?)\s*Ω\b", r"\1 ohms"),
        (r"(\d+(?:\.\d+)?)\s*F\b", r"\1 farads"),
        (r"(\d+(?:\.\d+)?)\s*H\b", r"\1 henrys"),
        (r"(\d+(?:\.\d+)?)\s*Pa\b", r"\1 pascals"),
        # Unidades compostas (sem número antes, mas padrão conhecido)
        (r"\bm\s*/\s*s\b", "metros por segundo"),
        (r"\bkm\s*/\s*h\b", "quilômetros por hora"),
        (r"\bcm\s*/\s*s\b", "centímetros por segundo"),
        (r"\bN\s*\*\s*m\b", "newton metro"),
        (r"\bJ\s*/\s*s\b", "watts"),
    ]
    for pattern, spoken in unit_patterns:
        out = re.sub(pattern, spoken, out, flags=re.IGNORECASE)

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

    # 6b. Floor e Ceiling: \lfloor x \rfloor -> "piso de x", \lceil x \rceil -> "teto de x"
    out = re.sub(r"\\lfloor\s*([^\\]+)\s*\\rfloor", r"piso de \1", out)
    out = re.sub(r"\\lceil\s*([^\\]+)\s*\\rceil", r"teto de \1", out)

    # 6c. Fatorial: n! -> "n fatorial" (mas não confundir com negação lógica)
    # Fatorial aparece após: número, variável única (início de palavra), ou fecha parêntese/colchete/chave
    # NÃO após letras no meio de palavra (ex: "Correto!" não é fatorial)
    # Múltiplos ! (fatorial duplo, triplo) -> "n fatorial duplo", etc.
    def _factorial_repl(m: re.Match) -> str:
        base = m.group(1) or m.group(2)
        excl_count = len(m.group(0)) - len(base)
        if excl_count == 1:
            return f"{base} fatorial"
        elif excl_count == 2:
            return f"{base} fatorial duplo"
        elif excl_count == 3:
            return f"{base} fatorial triplo"
        else:
            return f"{base} fatorial {excl_count} vezes"

    # Padrão: (letra isolada no início de palavra) OU (dígito/fecha bracket) + !
    # (?<!\w) garante que a letra não tem letra/dígito/underscore antes
    out = re.sub(r"(?:(?<!\w)([a-zA-Z])|([0-9\)\]\}]))\s*!+", _factorial_repl, out)

    # 7. Letras gregas
    for cmd, spoken in sorted(_GREEK_MAP.items(), key=lambda x: -len(x[0])):
        out = out.replace(cmd, spoken)

    # 8. Operadores e símbolos
    symbol_map = [
        # Aritméticos
        (r"\cdot", " vezes "),
        (r"\times", " vezes "),
        (r"\div", " dividido "),
        (r"\pm", " mais ou menos "),
        (r"\mp", " menos ou mais "),

        # Relacionais
        (r"\neq", " diferente de "),
        (r"\ne", " diferente de "),
        (r"\leq", " menor ou igual a "),
        (r"\le", " menor ou igual a "),
        (r"\geq", " maior ou igual a "),
        (r"\ge", " maior ou igual a "),
        (r"\ll", " muito menor que "),
        (r"\gg", " muito maior que "),
        (r"\approx", " aproximadamente igual a "),
        (r"\equiv", " equivalente a "),
        (r"\sim", " semelhante a "),
        (r"\simeq", " semelhante a "),
        (r"\cong", " congruente a "),
        (r"\propto", " proporcional a "),

        # Lógicos
        (r"\land", " e "),
        (r"\lor", " ou "),
        (r"\lnot", " não "),
        (r"\neg", " não "),
        (r"\implies", " implica "),
        (r"\Rightarrow", " implica "),
        (r"\iff", " se e somente se "),
        (r"\Leftrightarrow", " se e somente se "),
        (r"\forall", " para todo "),
        (r"\exists", " existe "),
        (r"\nexists", " não existe "),

        # Conjuntos
        (r"\in", " pertence a "),
        (r"\notin", " não pertence a "),
        (r"\subset", " subconjunto de "),
        (r"\subseteq", " subconjunto ou igual a "),
        (r"\supset", " superconjunto de "),
        (r"\supseteq", " superconjunto ou igual a "),
        (r"\cup", " união "),
        (r"\cap", " intersecção "),
        (r"\setminus", " diferença "),
        (r"\complement", " complementar "),
        (r"\emptyset", " conjunto vazio "),
        (r"\varnothing", " conjunto vazio "),

        # Setas
        (r"\to", " tende a "),
        (r"\rightarrow", " tende a "),
        (r"\leftarrow", " vem de "),
        (r"\mapsto", " mapeia em "),
        (r"\uparrow", " tende a infinito "),
        (r"\downarrow", " tende a menos infinito "),

        # Composição e outros operadores
        (r"\circ", " composto com "),

        # Outros
        (r"\infty", " infinito "),
        (r"\pi", " pi "),
        (r"\%", " por cento "),
        (r"/", " dividido "),
        (r"\-", " menos "),
        (r"-", " menos "),
        (r"'", " linha "),
        (r"\prime", " linha "),

        # Acentos comuns
        (r"\hat", " chapéu "),
        (r"\tilde", " til "),
        (r"\bar", " barra "),
        (r"\vec", " vetor "),
        (r"\overrightarrow", " vetor "),
        (r"\dot", " ponto "),
        (r"\ddot", " dois pontos "),

        # Delimitadores - floor/ceiling são tratados antes via regex
        (r"\langle", " produto interno "),
        (r"\rangle", " produto interno "),
        (r"\|", " norma "),

        # Espaços
        (r"\quad", " "),
        (r"\qquad", " "),
        (r"\,", " "),
        (r"\:", " "),
        (r"\;", " "),
        (r"\!", ""),
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
