/** @type {import('tailwindcss').Config} */
import daisyui from 'daisyui';

export const darkMode = 'selector';
export const content = ['./app/templates/**/*.jinja'];
export const theme = {
  extend: {},
};
export const plugins = [daisyui];
export const daisyui = {
  themes: [
    {
      light: {
        'primary': '#10b981',
        'secondary': '#854d0e',
        'accent': '#0c4a6e',
        'neutral': '#3f3f46',
        'base-100': '#ffffff',
        'info': '#0ea5e9',
        'success': '#22c55e',
        'warning': '#f97316',
        'error': '#ef4444'
      },
      dark: {
        'primary': '#10b981',
        'secondary': '#57534e',
        'accent': '#0369a1',
        'neutral': '#d4d4d8',
        'base-100': '#27272a',
        'info': '#38bdf8',
        'success': '#4ade80',
        'warning': '#fb923c',
        'error': '#f87171'
      }
    }
  ]
};
