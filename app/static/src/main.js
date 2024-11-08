import Alpine from 'alpinejs';
import { chartStore } from './chartStore';
import formValidation from './formValidation';

Alpine.store('chart', chartStore);
Alpine.data('formValidationManagement', (minDate, maxDate) => formValidation(minDate, maxDate));

Alpine.start()