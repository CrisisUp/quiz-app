# Quiz Interativo Neural 🧠

Aplicação completa de questionários interativos com **interface Web (SPA)**, **renderização LaTeX via KaTeX** e **síntese de voz neural em Português do Brasil (pt-BR)** usando `edge-tts` com a voz `pt-BR-FranciscaNeural`.

---

## ✨ Funcionalidades

| Recurso | Descrição |
|---------|-----------|
| 🎤 **TTS Neural** | Síntese de voz via `edge-tts` (Microsoft) com voz `pt-BR-FranciscaNeural` |
| 📐 **LaTeX Completo** | KaTeX via CDN — suporte a `$inline$` e `$$display$$` |
| ⌨️ **Acessibilidade por Teclado** | `A/B/C/D` selecionam, `R`/`Espaço` ouvem, `Enter` confirma/avança |
| 🌙 **Dark Mode** | Interface responsiva, centralizada, tipografia limpa |
| 📊 **Progresso & Score** | Barra de progresso, contador de acertos, tela final com placar |
| 🔁 **Feedback Imediato** | Explicação da questão após confirmar, opções marcadas certo/errado |
| 🛑 **Controle de Áudio** | Botões Ouvir, Parar, Confirmar, Próxima |

---

## 🛠 Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|------------|--------|
| **Backend** | FastAPI | 0.141.1 |
| **ASGI Server** | Uvicorn | 0.52.0 |
| **TTS** | edge-tts | 7.2.8 |
| **Validação** | Pydantic | 2.13.4 |
| **Frontend** | HTML5 + CSS3 + JS Vanilla (ES6+) | — |
| **Math Render** | KaTeX | 0.16.21 (CDN) |
| **Python** | CPython | 3.14+ |

---

## 🚀 Execução Local

```bash
# 1. Clone
git clone https://github.com/CrisisUp/quiz-app.git
cd quiz-app

# 2. Dependências
pip install -r requirements.txt

# 3. Rode o servidor
uvicorn main:app --reload --port 8000

# 4. Abra no navegador
# http://localhost:8000
```

---

## 📁 Estrutura do Projeto

```
quiz-app/
├── main.py              # Backend FastAPI + TTS + sanitizador LaTeX
├── questoes.json        # Banco de questões (LaTeX + pt-BR)
├── requirements.txt     # Dependências pinadas
├── .gitignore
└── static/
    └── index.html       # SPA completa (HTML + CSS + JS)
```

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Serve a SPA (`static/index.html`) |
| `GET` | `/api/questoes` | Retorna todas as questões (JSON, UTF-8) |
| `GET` | `/api/tts?texto=...` | Retorna áudio MP3 (streaming) via `edge-tts` |
| `GET` | `/favicon.ico` | Retorna 204 (evita 404 no console) |

### Exemplo TTS
```bash
curl "http://localhost:8000/api/tts?texto=x%5E2%20-%205x%20%2B%206%20%3D%200" -o questao3.mp3
```

---

## 🧮 Sanitizador LaTeX → Fala (pt-BR)

O backend converte expressões matemáticas para português falado **antes** de sintetizar:

| LaTeX | Fala |
|-------|------|
| `\frac{a}{b}` | "a sobre b" |
| `\sqrt{x}` | "raiz quadrada de x" |
| `x^2` | "x ao quadrado" |
| `x^3` | "x ao cubo" |
| `x^n` | "x elevado a n" |
| `x_1` | "x índice 1" |
| `\alpha` | "alfa" |
| `\beta` | "beta" |
| `\pi` | "pi" |
| `\infty` | "infinito" |
| `\neq` | "diferente de" |
| `\leq` | "menor ou igual a" |
| `\geq` | "maior ou igual a" |
| `\pm` | "mais ou menos" |
| `\cdot` | "vezes" |
| `-` | "menos" |

> **Nota:** O sanitizador adiciona pausas explícitas (`... menos ...`) para garantir que o "menos" seja pronunciado claramente pela voz neural.

---

## ⌨️ Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| `A` `B` `C` `D` | Seleciona a respectiva alternativa |
| `R` ou `Espaço` | Lê enunciado + alternativas |
| `Enter` | Confirma resposta (se não respondeu) **ou** Avança (se já respondeu) |

---

## 📝 Formato das Questões (`questoes.json`)

```json
[
  {
    "id": 1,
    "categoria": "Aritmética",
    "pergunta": "Qual é o resultado de $3^2 + 4^2$?",
    "opcoes": [
      {"letra": "A", "texto": "7"},
      {"letra": "B", "texto": "12"},
      {"letra": "C", "texto": "25"},
      {"letra": "D", "texto": "49"}
    ],
    "resposta": "C",
    "explicacao": "$3^2 = 9$ e $4^2 = 16$. Logo, $9 + 16 = 25$."
  }
]
```

- **`pergunta`** e **`explicacao`** aceitam LaTeX com `$...$` (inline) e `$$...$$` (display)
- **`opcoes[].texto`** também aceita LaTeX
- Acentuação pt-BR nativa (UTF-8)

---

## 🎨 Personalização

### Adicionar questões
Edite `questoes.json` mantendo a estrutura acima.

### Trocar voz TTS
Em `main.py`, linha ~149:
```python
communicate = edge_tts.Communicate(texto_limpo, "pt-BR-FranciscaNeural")
```
Voices disponíveis: `pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`, `pt-BR-ThalitaNeural`, etc.

### Temas/Cores
Edite as variáveis CSS em `:root` no `<style>` do `static/index.html`:
```css
:root {
  --bg:        #0f1117;
  --surface:   #1a1d27;
  --accent:    #6c8cff;
  --success:   #34d399;
  --danger:    #f87171;
  /* ... */
}
```

---

## 📦 Deploy (Vercel)

```bash
# Instale a Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

> O projeto usa `vercel.ts` nativo (FastAPI detectado automaticamente). Variáveis de ambiente não são necessárias.

---

## 📄 Licença

MIT — Use livremente para estudos, ensino ou base para outros projetos.

---

## 🤝 Créditos

- **KaTeX** — Khan Academy
- **edge-tts** — Microsoft Edge TTS wrapper
- **FastAPI** — Sebastián Ramírez
- **Voz pt-BR-FranciscaNeural** — Microsoft Speech Platform