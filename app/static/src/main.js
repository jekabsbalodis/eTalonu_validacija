import Alpine from 'alpinejs';
import persist from '@alpinejs/persist'
import { chartStore } from './chartStore';
import formValidation from './formValidation';

Alpine.plugin(persist)

Alpine.store('darkMode', {
    on: Alpine.$persist(null).as('darkMode'),
    isAuto: Alpine.$persist(true).as('isAuto'),

    init() {
        if (localStorage.getItem('isAuto') === null) {
            this.isAuto = true;
        }

        if (this.on === null) {
            this.on = window.matchMedia('(prefers-color-scheme: dark)').matches;
        }

        this.updateTheme();

        window.matchMedia('(prefers-color-scheme: dark)')
            .addEventListener('change', (e) => {
                if (this.isAuto) {
                    this.on = e.matches;
                    this.updateTheme();
                }
            });
    },
    setDark() {
        this.isAuto = false;
        this.on = true;
        this.updateTheme();
    },
    setLight() {
        this.isAuto = false;
        this.on = false;
        this.updateTheme();
    },
    setAuto() {
        this.isAuto = true;
        this.on = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.updateTheme();
    },
    updateTheme() { document.documentElement.dataset.theme = this.on ? 'dark' : 'light' }
});

Alpine.store('chart', chartStore);
Alpine.data('formValidationManagement', (minDate, maxDate) => formValidation(minDate, maxDate));

Alpine.start()