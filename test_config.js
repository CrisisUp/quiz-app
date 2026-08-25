
const Config = Object.freeze({
    // API
    API: {
        QUESTOES: '/api/questoes',
        TTS: '/api/tts',
    },

    // Display States
    Display: Object.freeze({
        FLEX: 'flex',
        NONE: 'none',
        INLINE_FLEX: 'inline-flex',
        BLOCK: 'block',
    }),

    // Keyboard Shortcuts
    Keys: Object.freeze({
        OPTIONS: ['A', 'B', 'C', 'D'],
        SPEAK: ['R', ' '],
        CONFIRM: 'ENTER',
        PREV: ['ARROWLEFT', 'LEFT'],
        NEXT: ['ARROWRIGHT', 'RIGHT'],
    }),

    // TTS
    TTS: {
        DELIMITER_REPLACEMENT: ' ',
    },

    // DOM Selectors
    Selectors: Object.freeze({
        LOADING: '#loadingState',
        QUIZ: '#quizState',
    }),

    // CSS Classes
    Classes: Object.freeze({
        OPTION_BTN: 'option-btn',
        SELECTED: 'selected',
    }),

    // Audio
    Audio: {
        MIME_TYPE: 'audio/mpeg',
    },
});

console.log('Config:', Config);
