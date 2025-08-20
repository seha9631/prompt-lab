import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enNav from '../../i18n/locales/en/nav.json';
import koNav from '../../i18n/locales/ko/nav.json';
import enAuth from '../../i18n/locales/en/auth.json';
import koAuth from '../../i18n/locales/ko/auth.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { nav: enNav, auth: enAuth },
      ko: { nav: koNav, auth: koAuth }
    },
    fallbackLng: 'en',
    supportedLngs: ['en', 'ko'],
    ns: ['nav'],
    defaultNS: 'nav',
    detection: {
      order: ['localStorage', 'querystring', 'navigator', 'htmlTag'],
      lookupLocalStorage: 'i18nextLng'
    },
    interpolation: { escapeValue: false },
    returnEmptyString: false
  });

export default i18n;