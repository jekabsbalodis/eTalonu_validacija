import Alpine from 'alpinejs';
import ajax from '@imacrayon/alpine-ajax';
import { chartStore } from './chartStore';
import formValidation from './formValidation';

Alpine.plugin(ajax);

Alpine.store('chart', chartStore);
Alpine.data('formValidationManagement', (minDate, maxDate) => formValidation(minDate, maxDate));

Alpine.start()