export default (minDate, maxDate) => ({
    startDateError: '',
    endDateError: '',

    init() { this.validateDates(); },

    validateDates() {
        this.validateInput(this.$refs.start_date, 'start');
        this.validateInput(this.$refs.end_date, 'end');
        this.validateDateRange();
    },

    validateInput(inputRef, type) {
        const messages = {
            required: 'Lūdzu norādi datumu.',
            range: `Datubāzē pieejami ieraksti no ${minDate} līdz ${maxDate}.`
        };

        let errorMessage = '';

        if (inputRef.validity.valueMissing) {
            inputRef.setCustomValidity(messages.required);
            errorMessage = messages.required
        }
        else if (inputRef.validity.rangeUnderflow || inputRef.validity.rangeOverflow) {
            inputRef.setCustomValidity(messages.range);
            errorMessage = messages.range
        }
        else {
            inputRef.setCustomValidity('');
            errorMessage = '';
        }

        if (type == 'start') {
            this.startDateError = errorMessage;
        } else if (type == 'end') {
            this.endDateError = errorMessage;
        }
    },

    validateDateRange() {
        if (this.$refs.start_date.value && this.$refs.end_date.value) {
            const startDate = new Date(this.$refs.start_date.value);
            const endDate = new Date(this.$refs.end_date.value);
            if (endDate < startDate) {
                const message = 'Beigu datums nedrīkst būt pirms sākuma datuma';
                this.$refs.end_date.setCustomValidity(message);
                this.endDateError = message;
            }
            else {
                this.$refs.end_date.setCustomValidity('');
                this.endDateError = '';
            }
        }
    }
});
