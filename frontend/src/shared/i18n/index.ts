import i18n from "i18next";
import { initReactI18next } from "react-i18next";

i18n.use(initReactI18next).init({
  resources: {
    en: {
      common: {
        save: "Save",
        cancel: "Cancel",
        delete: "Delete",
        edit: "Edit",
        close: "Close",
      },
    },
    ar: {
      common: {
        save: "حفظ",
        cancel: "إلغاء",
        delete: "حذف",
        edit: "تعديل",
        close: "إغلاق",
      },
    },
  },
  lng: "en",
  fallbackLng: "en",
  ns: ["common"],
  defaultNS: "common",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
