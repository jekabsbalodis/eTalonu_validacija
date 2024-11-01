export default (minDate, maxDate) => ({
    start_date: '',
    end_date: '',

    init() { this.validateDates(); },

    validateDates() {
        this.validateInput(this.$refs.start_date);
        this.validateInput(this.$refs.end_date);
        this.validateDateRange();
    },

    validateInput(inputRef) {
        const messages = {
            required: 'Lūdzu norādi datumu.',
            range: `Datubāzē pieejami ieraksti no ${minDate} līdz ${maxDate}.`
        };
        if (inputRef.validity.valueMissing) {
            inputRef.setCustomValidity(messages.required);
        }
        else if (inputRef.validity.rangeUnderflow || inputRef.validity.rangeOverflow) {
            inputRef.setCustomValidity(messages.range);
        }
        else {
            inputRef.setCustomValidity('');
        }
    },

    validateDateRange() {
        if (this.$refs.start_date.value && this.$refs.end_date.value) {
            const startDate = new Date(this.$refs.start_date.value);
            const endDate = new Date(this.$refs.end_date.value);
            if (endDate < startDate) {
                const message = 'Beigu datums nedrīkst būt pirms sākuma datuma';
                this.$refs.end_date.setCustomValidity(message);
            }
            else {
                this.$refs.end_date.setCustomValidity('');
            }
        }
    }
});
