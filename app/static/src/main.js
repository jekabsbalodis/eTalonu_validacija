import Alpine from 'alpinejs';
import { chartStore } from './chartStore';
import formValidation from './formValidation';


Alpine.store('darkMode', {
    theme: localStorage.getItem('theme') || 'system',
    isSystemDark: localStorage.getItem('isSystemDark') === 'true',

    init() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        this.isSystemDark = mediaQuery.matches;
        mediaQuery.addEventListener('change', (event) => {
            this.isSystemDark = event.matches;
            if (this.theme === 'system') {
                this.updateTheme();
            }
        });

        this.updateTheme();
    },

    setDark() {
        this.theme = 'dark';
        this.updateTheme();
    },
    setLight() {
        this.theme = 'light';
        this.updateTheme();
    },
    setAuto() {
        this.theme = 'system';
        this.updateTheme();
    },
    updateTheme() {
        let theme = 'light';
        if (this.theme === 'dark' || (this.theme === 'system' && this.isSystemDark)) {
            theme = 'dark';
        }
        localStorage.setItem('theme', this.theme);
        localStorage.setItem('isSystemDark', this.isSystemDark);
        document.documentElement.dataset.theme = theme;
    }
});

Alpine.store('chart', chartStore);
Alpine.data('formValidationManagement', (minDate, maxDate) => formValidation(minDate, maxDate));

Alpine.start()