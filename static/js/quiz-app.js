/**
 * Quiz App - Clean Code Refactored Frontend
 * Module Pattern with encapsulated state, no global pollution
 */
const QuizApp = (() => {
    "use strict";

    // =============================================================================
    // CONFIGURATION - Single source of truth for all constants
    // =============================================================================
    const Config = Object.freeze({
        // API
        API: {
            QUESTOES: "/api/questoes",
            TTS: "/api/tts",
        },

        // Display States - Single source of truth
        Display: Object.freeze({
            FLEX: "flex",
            NONE: "none",
            INLINE_FLEX: "inline-flex",
            BLOCK: "block",
        }),

        // Keyboard Shortcuts
        Keys: Object.freeze({
            OPTIONS: ["A", "B", "C", "D"],
            SPEAK: ["R", " "],        // R or Space
            CONFIRM: "ENTER",
            PREV: ["ARROWLEFT", "LEFT"],
            NEXT: ["ARROWRIGHT", "RIGHT"],
        }),

        // TTS
        TTS: {
            DELIMITER_REPLACEMENT: " ",  // Replace $ with space for TTS
        },

        // DOM Selectors - Single source of truth
        Selectors: Object.freeze({
            LOADING: "#loadingState",
            QUIZ: "#quizState",
            RESULTS: "#resultsState",
            TOOLBAR: "#toolbar",
            HINT: "#keyboardHint",
            PROGRESS_FILL: "#progressBarFill",
            PROGRESS_TEXT: "#progressText",
            SCORE_TEXT: "#scoreText",
            SCORE_BADGE: "#scoreBadge",
            BTN_SPEAK: "#btnSpeak",
            BTN_STOP: "#btnStop",
            BTN_CONFIRM: "#btnConfirm",
            BTN_PREV: "#btnPrev",
            BTN_NEXT_NAV: "#btnNextNav",
            QUESTION_SELECT: "#questionSelect",
            AUDIO_PLAYER: "#audioPlayer",
            OPTIONS_LIST: "#optionsList",
            EXPLANATION: "#explanation",
            OPTIONS_LIST: "#optionsList",
            EXPLANATION: "#explanation",
        },

        // CSS Classes
        Classes: Object.freeze({
            OPTION_BTN: "option-btn",
            SELECTED: "selected",
            CORRECT: "correct",
            WRONG: "wrong",
            DISABLED: "disabled",
            EXPLANATION: "explanation",
            CORRECT_EXPL: "correct-expl",
            WRONG_EXPL: "wrong-expl",
        }),

        // Audio
        Audio: {
            MIME_TYPE: "audio/mpeg",
        },
    };

    // =============================================================================
    // STATE - Encapsulated, private
    // =============================================================================
    let state = {
        questions: [],
        currentIndex: 0,
        score: 0,
        selectedOption: null,
        hasAnswered: false,
        currentTtsText: "",
    };

    // =============================================================================
    // DOM CACHE - Single point of access, cached on init
    // =============================================================================
    const dom = {};

    function cacheDomElements() {
        const selectors = Config.Selectors;
        dom.loading = document.querySelector(selectors.LOADING);
        dom.quiz = document.querySelector(selectors.QUIZ);
        dom.results = document.querySelector(selectors.RESULTS);
        dom.toolbar = document.querySelector(selectors.TOOLBAR);
        dom.hint = document.querySelector(selectors.HINT);
        dom.progressFill = document.querySelector(selectors.PROGRESS_FILL);
        dom.progressText = document.querySelector(selectors.PROGRESS_TEXT);
        dom.scoreText = document.querySelector(selectors.SCORE_TEXT);
        dom.scoreBadge = document.querySelector(selectors.SCORE_BADGE);
        dom.btnSpeak = document.querySelector(selectors.BTN_SPEAK);
        dom.btnStop = document.querySelector(selectors.BTN_STOP);
        dom.btnConfirm = document.querySelector(selectors.BTN_CONFIRM);
        dom.btnPrev = document.querySelector(selectors.BTN_PREV);
        dom.btnNextNav = document.querySelector(selectors.BTN_NEXT_NAV);
        dom.questionSelect = document.querySelector(selectors.QUESTION_SELECT);
        dom.audio = document.querySelector(selectors.AUDIO_PLAYER);
        dom.optionsList = document.querySelector(selectors.OPTIONS_LIST);
        dom.explanation = document.querySelector(selectors.EXPLANATION);
        dom.hint = document.querySelector(Config.Selectors.HINT);
    }

    // =============================================================================
    // CONSTANTS - Display states, no magic strings
    // =============================================================================
    const Display = Config.Display;
    const Keys = Config.Keys;
    const Classes = Config.Classes;

    // =============================================================================
    // PURE FUNCTIONS - No side effects, easily testable
    // =============================================================================

    /**
     * Build TTS API URL from text
     * @param {string} text - Text to convert to speech
     * @returns {string} API URL
     */
    function buildTtsUrl(text) {
        const cleaned = text.replace(/\$/g, Config.TTS.DELIMITER_REPLACEMENT);
        return `${Config.API.TTS}?texto=${encodeURIComponent(cleaned)}`;
    }

    /**
     * Render KaTeX math in element
     * @param {HTMLElement} el - Element containing LaTeX
     */
    function renderKaTeX(el) {
        if (typeof renderMathInElement === "function") {
            renderMathInElement(el, {
                delimiters: [
                    { left: "$$", right: "$$", display: true },
                    { left: "$", right: "$", display: false },
                ],
                throwOnError: false,
            });
        }
    }

    // =============================================================================
    // STATE MANAGEMENT - Explicit, controlled mutations
    // =============================================================================

    function resetQuestionState() {
        state.selectedOption = null;
        state.hasAnswered = false;
    }

    function setQuestionIndex(newIndex) {
        if (newIndex >= 0 && newIndex < state.questions.length) {
            state.currentIndex = newIndex;
        }
    }

    function incrementScore() {
        state.score++;
    }

    function markAnswered() {
        state.hasAnswered = true;
    }

    function selectOption(letter) {
        state.selectedOption = letter;
    }

    function setCurrentTtsText(text) {
        state.currentTtsText = text;
    }

    function setCurrentQuestionText(text) {
        state.currentTtsText = text;
    }

    function resetQuizState() {
        state.currentIndex = 0;
        state.score = 0;
    }

    // =============================================================================
    // DOM MANIPULATION - Single responsibility per function
    // =============================================================================

    function showElement(element, display = Display.FLEX) {
        if (element) element.style.display = display;
    }

    function hideElement(element) {
        if (element) element.style.display = Display.NONE;
    }

    function setElementDisplay(element, display) {
        if (element) element.style.display = display;
    }

    function setElementDisabled(element, disabled) {
        if (element) element.disabled = disabled;
    }

    function setElementFocus(element) {
        if (element) element.focus();
    }

    function setElementValue(element, value) {
        if (element) element.value = value;
    }

    function setElementText(element, text) {
        if (element) element.textContent = text;
    }

    function setElementHtml(element, html) {
        if (element) element.innerHTML = html;
    }

    function addClass(element, className) {
        if (element) element.classList.add(className);
    }

    function removeClass(element, className) {
        if (element) element.classList.remove(className);
    }

    function toggleClass(element, className, force) {
        if (element) element.classList.toggle(className, force);
    }

    // =============================================================================
    // RENDERERS - Pure presentation logic
    // =============================================================================

    /**
     * Build question card HTML
     * @param {Object} question - Question data
     * @param {number} currentIdx - Current question index (0-based)
     * @param {number} total - Total questions
     * @returns {string} HTML string
     */
    function buildQuestionHtml(question, currentIdx, total) {
        return `
            <div class="question-card">
                <div class="question-header">
                    <span class="question-category">${escapeHtml(question.categoria)}</span>
                    <span class="question-number">Questão ${currentIdx + 1} de ${total}</span>
                </div>
                <div class="question-text">${question.pergunta}</div>
                <div class="options" id="optionsList">
                    ${question.opcoes.map(opt => `
                        <button class="option-btn" data-letra="${escapeHtml(opt.letra)}" tabindex="0">
                            <span class="letter">${escapeHtml(opt.letra)}</span>
                            <span class="texto">${escapeHtml(opt.texto)}</span>
                        </button>
                    `).join("")}
                </div>
            </div>
            <div id="explanation"></div>
        `;
    }

    /**
     * Build explanation HTML
     * @param {boolean} isCorrect - Whether answer was correct
     * @param {string} explanation - Explanation text
     * @returns {string} HTML string
     */
    function buildExplanationHtml(isCorrect, explanation) {
        const cssClass = isCorrect ? Classes.CORRECT_EXPL : Classes.WRONG_EXPL;
        const icon = isCorrect ? "✅ Correto!" : "❌ Incorreto!";
        return `
            <div class="explanation ${Classes.EXPLANATION} ${cssClass}">
                <strong>${icon}</strong>
                ${explanation}
            </div>
        `;
    }

    /**
     * Build results screen HTML
     * @param {number} score - Correct answers count
     * @param {number} total - Total questions
     * @returns {string} HTML string
     */
    function buildResultsHtml(score, total) {
        const pct = Math.round((score / total) * 100);
        let msg;
        if (pct === 100) msg = "🏆 Perfeito! Você dominou todas as questões!";
        else if (pct >= 70) msg = "👏 Muito bem! Você tem um bom domínio do assunto.";
        else if (pct >= 40) msg = "📚 Continue estudando, você está no caminho certo!";
        else msg = "💪 Não desista! Revise o conteúdo e tente novamente.";

        return `
            <div class="category">Resultado Final</div>
            <div class="big-score"><span>${score}</span>/${total}</div>
            <div class="label">${pct}% de acerto</div>
            <div class="message">${msg}</div>
            <button class="btn btn-primary" onclick="QuizApp.restart()" style="margin:0 auto">
                🔄 Reiniciar Quiz
            </button>
        `;
    }

    /**
     * Build option button HTML
     * @param {Object} option - Option data {letra, texto}
     * @returns {string} HTML string
     */
    function buildOptionHtml(option) {
        return `
            <button class="${Classes.OPTION_BTN}" data-letra="${escapeHtml(option.letra)}" tabindex="0">
                <span class="letter">${escapeHtml(option.letra)}</span>
                <span class="texto">${escapeHtml(option.texto)}</span>
            </button>
        `;
    }

    /**
     * Build question selector options
     * @param {Array} questions - Array of questions
     * @param {number} currentIdx - Current index
     * @returns {string} HTML string
     */
    function buildQuestionSelectorHtml(questions, currentIdx) {
        return questions.map((q, i) =>
            `<option value="${i}" ${i === state.currentIndex ? "selected" : ""}>
                ${i + 1}. ${escapeHtml(q.categoria)}
            </option>`
        ).join("");
    }

    // =============================================================================
    // UI STATE MANAGEMENT - Explicit UI state transitions
    // =============================================================================

    function showLoading() {
        hideElement(dom.quiz);
        hideElement(dom.toolbar);
        hideElement(dom.hint);
        showElement(dom.loading, Display.FLEX);
    }

    function showQuiz() {
        hideElement(dom.loading);
        hideElement(dom.results);
        showElement(dom.quiz, Display.BLOCK);
        showElement(dom.toolbar, Display.FLEX);
        showElement(dom.hint, Display.BLOCK);
    }

    function showResults() {
        hideElement(dom.quiz);
        hideElement(dom.toolbar);
        hideElement(dom.hint);
        showElement(dom.results, Display.BLOCK);
    }

    function showToolbar() {
        showElement(dom.toolbar, Display.FLEX);
    }

    function hideToolbar() {
        hideElement(dom.toolbar);
    }

    function showHint() {
        showElement(dom.hint, Display.BLOCK);
    }

    function hideHint() {
        hideElement(dom.hint);
    }

    // =============================================================================
    // TOOLBAR STATE MANAGEMENT
    // =============================================================================

    function setConfirmButtonState(enabled) {
        setElementDisabled(dom.btnConfirm, !enabled);
    }

    function showConfirmButton() {
        showElement(dom.btnConfirm, Display.INLINE_FLEX);
        hideElement(dom.btnNextNav);
    }

    function hideConfirmButton() {
        hideElement(dom.btnConfirm);
    }

    function showNextNavButton() {
        showElement(dom.btnNextNav, Display.INLINE_FLEX);
        hideElement(dom.btnConfirm);
    }

    function hideNextNavButton() {
        hideElement(dom.btnNextNav);
    }

    function setPrevButtonState(disabled) {
        setElementDisabled(dom.btnPrev, disabled);
    }

    function setNextNavButtonState(disabled) {
        setElementDisabled(dom.btnNextNav, disabled);
    }

    function setQuestionSelectValue(value) {
        setElementValue(dom.questionSelect, value);
    }

    function populateQuestionSelector() {
        dom.questionSelect.innerHTML = buildQuestionSelectorHtml(state.questions, state.currentIndex);
    }

    function updateNavigationUI() {
        setPrevButtonState(state.currentIndex === 0);
        setNextNavButtonState(state.currentIndex === state.questions.length - 1);
        setQuestionSelectValue(state.currentIndex);
    }

    // =============================================================================
    // PROGRESS & SCORE UI
    // =============================================================================

    function updateProgress() {
        const pct = (state.currentIndex / state.questions.length) * 100;
        setElementStyleWidth(dom.progressFill, `${pct}%`);
        setElementText(dom.progressText, `Questão ${state.currentIndex + 1} de ${state.questions.length}`);
    }

    function updateScore() {
        const suffix = state.score === 1 ? "a" : "as";
        setElementText(dom.scoreText, `${state.score} corret${suffix}`);
    }

    function setElementStyleWidth(element, width) {
        if (element) element.style.width = width;
    }

    // =============================================================================
    // AUDIO / TTS
    // =============================================================================

    function playAudio(text) {
        const url = buildTtsUrl(text);
        dom.audio.src = url;
        dom.audio.load();
        dom.audio.oncanplaythrough = () => {
            dom.audio.play().catch(() => {}); // Silent fail for autoplay policy
        };
    }

    function stopAudio() {
        if (dom.audio) {
            dom.audio.pause();
            dom.audio.oncanplaythrough = null;
            dom.audio.removeAttribute("src");
            dom.audio.load();
        }
    }

    // =============================================================================
    // CORE LOGIC - Business logic
    // =============================================================================

    function selectOption(letter) {
        if (state.hasAnswered) return;

        state.selectedOption = letter;

        // Update visual selection
        document.querySelectorAll(`.${Classes.OPTION_BTN}`).forEach(btn => {
            removeClass(btn, Classes.SELECTED);
            if (btn.dataset.letra === letter) {
                addClass(btn, Classes.SELECTED);
            }
        });

        setConfirmButtonState(false); // enabled = false -> disabled = true
    }

    function buildSpeechText(question, selectedLetter, isCorrect) {
        const correctOption = question.opcoes.find(o => o.letra === question.resposta);
        if (isCorrect) {
            return `Correto! A alternativa ${question.resposta}: ${correctOption.texto}. ${question.explicacao}`;
        } else {
            return `Incorreto. A resposta certa é a alternativa ${question.resposta}: ${question.opcoes.find(o => o.letra === question.resposta).texto}. ${question.explicacao}`;
        }
    }

    function showExplanation(isCorrect, explanation) {
        const explDiv = document.getElementById("explanation");
        if (!explDiv) return;

        const cssClass = isCorrect ? Classes.CORRECT_EXPL : Classes.WRONG_EXPL;
        const icon = isCorrect ? "✅ Correto!" : "❌ Incorreto!";

        explDiv.innerHTML = `
            <div class="${Classes.EXPLANATION} ${isCorrect ? Classes.CORRECT_EXPL : Classes.WRONG_EXPL}">
                <strong>${isCorrect ? "✅ Correto!" : "❌ Incorreto!"}</strong>
                ${explanation}
            </div>
        `;
        renderKaTeX(explDiv);
    }

    function lockOptions(correctLetter, selectedLetter) {
        document.querySelectorAll(`.${Classes.OPTION_BTN}`).forEach(btn => {
            setElementDisabled(btn, true);
            removeClass(btn, Classes.SELECTED);
            if (btn.dataset.letra === correctLetter) addClass(btn, Classes.CORRECT);
            if (btn.dataset.letra === state.selectedOption && btn.dataset.letra !== correctLetter) {
                addClass(btn, Classes.WRONG);
            }
        });
    }

    // =============================================================================
    // ACTIONS - User interactions
    // =============================================================================

    function confirmAnswer() {
        if (state.hasAnswered || state.selectedOption === null) return;

        state.hasAnswered = true;
        const question = state.questions[state.currentIndex];
        const isCorrect = question.resposta === state.selectedOption;

        if (isCorrect) {
            state.score++;
            updateScore();
        }

        // Lock options & show feedback
        lockOptions(question.resposta, state.selectedOption);

        // Build and speak result
        const correctOption = state.questions[state.currentIndex].opcoes.find(o => o.letra === state.questions[state.currentIndex].resposta);
        const speechText = state.selectedOption === state.questions[state.currentIndex].resposta
            ? `Correto! A alternativa ${state.questions[state.currentIndex].resposta}: ${correctOption.texto}. ${state.questions[state.currentIndex].explicacao}`
            : `Incorreto. A resposta certa é a alternativa ${state.questions[state.currentIndex].resposta}: ${correctOption.texto}. ${state.questions[state.currentIndex].explicacao}`;

        // Show visual explanation
        const explanation = state.questions[state.currentIndex].explicacao;
        showExplanation(state.selectedOption === state.questions[state.currentIndex].resposta, explanation);

        // Speak result
        setCurrentTtsText(speechText);
        playAudio(speechText);

        // Toggle buttons
        hideConfirmButton();
        showNextNavButton();
        setElementFocus(dom.btnNextNav);
    }

    function nextQuestion() {
        state.currentIndex++;
        render();
    }

    function prevQuestion() {
        if (state.currentIndex > 0) {
            state.currentIndex--;
            render();
        }
    }

    function nextQuestionNav() {
        if (state.currentIndex < state.questions.length - 1) {
            state.currentIndex++;
            render();
        }
    }

    function goToQuestion(newIdx) {
        if (newIdx >= 0 && newIdx < state.questions.length) {
            state.currentIndex = newIdx;
            render();
        }
    }

    function prevQuestionAction() {
        if (state.currentIndex > 0) {
            state.currentIndex--;
            render();
        }
    }

    function nextQuestionNavAction() {
        if (state.currentIndex < state.questions.length - 1) {
            state.currentIndex++;
            render();
        }
    }

    function goToQuestionAction(newIdx) {
        if (newIdx >= 0 && newIdx < state.questions.length) {
            state.currentIndex = newIdx;
            render();
        }
    }

    function restart() {
        resetQuizState();
        updateScore();
        render();
    }

    // =============================================================================
    // RENDER - Main render function
    // =============================================================================

    function render() {
        if (state.currentIndex >= state.questions.length) {
            return showResultsScreen();
        }

        const question = state.questions[state.currentIndex];
        resetQuestionState();
        state.currentTtsText = question.pergunta;

        // Show quiz UI
        showQuiz();
        updateNavigationUI();
        setConfirmButtonState(true); // disabled = true
        showConfirmButton();
        hideNextNavButton();

        // Build and render question HTML
        const html = buildQuestionHtml(state.questions[state.currentIndex], state.currentIndex, state.questions.length);
        dom.quiz.innerHTML = buildQuestionHtml(state.questions[state.currentIndex], state.currentIndex, state.questions.length);
        renderKaTeX(dom.quiz);

        // Bind option clicks (event delegation)
        bindOptionClicks();

        updateProgress();
    }

    function bindOptionClicks() {
        const optionsList = document.getElementById("optionsList");
        if (!optionsList) return;

        // Event delegation - single listener
        optionsList.onclick = (e) => {
            const btn = e.target.closest(`.${Classes.OPTION_BTN}`);
            if (btn && !state.hasAnswered) {
                selectOption(btn.dataset.letra);
            }
        };
    }

    function updateProgress() {
        const pct = (state.currentIndex / state.questions.length) * 100;
        if (dom.progressFill) dom.progressFill.style.width = `${pct}%`;
        if (dom.progressText) dom.progressText.textContent = `Questão ${state.currentIndex + 1} de ${state.questions.length}`;
    }

    function showResultsScreen() {
        const total = state.questions.length;
        const pct = Math.round((state.score / total) * 100);

        let msg;
        if (pct === 100) msg = "🏆 Perfeito! Você dominou todas as questões!";
        else if (pct >= 70) msg = "👏 Muito bem! Você tem um bom domínio do assunto.";
        else if (pct >= 40) msg = "📚 Continue estudando, você está no caminho certo!";
        else msg = "💪 Não desista! Revise o conteúdo e tente novamente.";

        const html = `
            <div class="category">Resultado Final</div>
            <div class="big-score"><span>${state.score}</span>/${state.questions.length}</div>
            <div class="label">${pct}% de acerto</div>
            <div class="message">${msg}</div>
            <button class="btn btn-primary" onclick="QuizApp.restart()" style="margin:0 auto">
                🔄 Reiniciar Quiz
            </button>
        `;

        hideElement(dom.quiz);
        hideElement(dom.toolbar);
        hideElement(dom.hint);
        showElement(dom.results, Display.BLOCK);
        setElementStyleWidth(dom.progressFill, "100%");
        setElementText(dom.progressText, "Concluído!");
        dom.results.innerHTML = html;
    }

    // =============================================================================
    // KEYBOARD HANDLING
    // =============================================================================

    function handleKeydown(e) {
        // Ignore input fields
        if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

        const key = e.key.toUpperCase();

        // Option selection
        if (Keys.OPTIONS.includes(key) && !state.hasAnswered) {
            e.preventDefault();
            selectOption(key);
            return;
        }

        // Speak
        if (Keys.SPEAK.includes(key)) {
            e.preventDefault();
            if (state.currentTtsText) playAudio(state.currentTtsText);
            return;
        }

        // Enter - confirm or next
        if (key === Keys.CONFIRM) {
            e.preventDefault();
            if (state.hasAnswered) nextQuestion();
            else confirmAnswer();
            return;
        }

        // Arrow keys - navigation
        if (Keys.PREV.includes(key)) {
            e.preventDefault();
            prevQuestionAction();
            return;
        }
        if (Keys.NEXT.includes(key)) {
            e.preventDefault();
            nextQuestionNavAction();
            return;
        }
    }

    // =============================================================================
    // EVENT BINDING
    // =============================================================================

    function bindEvents() {
        // Keyboard
        document.addEventListener("keydown", handleKeydown);

        // Buttons
        dom.btnSpeak.addEventListener("click", () => {
            if (state.currentTtsText) playAudio(state.currentTtsText);
        });
        dom.btnStop.addEventListener("click", stopAudio);
        dom.btnConfirm.addEventListener("click", confirmAnswer);
        dom.btnPrev.addEventListener("click", prevQuestionAction);
        dom.btnNextNav.addEventListener("click", nextQuestionNavAction);
        dom.questionSelect.addEventListener("change", (e) => goToQuestionAction(parseInt(e.target.value, 10)));
    }

    // =============================================================================
    // INITIALIZATION
    // =============================================================================

    async function init() {
        try {
            console.log('[QuizApp] Initializing...');
            // Cache DOM elements first
            cacheDomElements();
            console.log('[QuizApp] DOM elements cached');
            console.log('[QuizApp] dom.loading:', dom.loading);
            console.log('[QuizApp] dom.quiz:', dom.quiz);
            console.log('[QuizApp] dom.results:', dom.results);
            console.log('[QuizApp] dom.toolbar:', dom.toolbar);
            console.log('[QuizApp] dom.hint:', dom.hint);
            console.log('[QuizApp] dom.btnConfirm:', dom.btnConfirm);
            console.log('[QuizApp] dom.btnNextNav:', dom.btnNextNav);
            console.log('[QuizApp] dom.btnPrev:', dom.btnPrev);
            console.log('[QuizApp] dom.btnNextNav:', dom.btnNextNav);
            console.log('[QuizApp] dom.questionSelect:', dom.questionSelect);
            console.log('[QuizApp] dom.audio:', dom.audio);
            console.log('[QuizApp] dom.optionsList:', dom.optionsList);
            console.log('[QuizApp] dom.explanation:', dom.explanation);
            // Bind events
            bindEvents();
            console.log('[QuizApp] Events bound');

            // Load questions
            console.log('[QuizApp] Fetching questions from:', Config.API.QUESTOES);
            const response = await fetch(Config.API.QUESTOES);
            console.log('[QuizApp] Fetch response status:', response.status, response.ok);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            state.questions = await response.json();
            console.log('[QuizApp] Questions loaded:', state.questions.length);

            // Populate question selector
            populateQuestionSelector();

            // Initial render
            updateScore();
            render();
        } catch (err) {
            if (dom.loading) {
                dom.loading.innerHTML = `❌ Falha ao carregar questões: ${err.message}`;
            }
            console.error("Quiz init error:", err);
        }
    }

    // =============================================================================
    // UTILITIES
    // =============================================================================

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // =============================================================================
    // PUBLIC API
    // =============================================================================
    return Object.freeze({
        init,
        restart,
        nextQuestion: nextQuestion,
        prevQuestion: prevQuestionAction,
        nextQuestionNav: nextQuestionNavAction,
        goToQuestion: goToQuestionAction,
        confirmAnswer,
        selectOption,
        // Expose for inline handlers
        restart,
    };
})();

// =============================================================================
// INITIALIZATION
// =============================================================================
document.addEventListener("DOMContentLoaded", () => {
    QuizApp.init();
});

// Export for inline handlers (restart button)
window.QuizApp = QuizApp;