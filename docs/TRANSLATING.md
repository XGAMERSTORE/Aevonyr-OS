# Translations

Source language: English. Starter catalogs are stored in aevonyr/locales.json and displayed in Settings.

When a translated string is absent, English is displayed. Several starter catalogs are incomplete and will need translators' review. Please do not mark them as finished.

To add another language:
1. Add its code and display name to aevonyr/i18n.py.
2. Add its dictionary to aevonyr/locales.json.
3. Run unit tests and verify labels on a real desktop.
4. Check diacritics and layout; RTL languages require explicit direction and font support.

All-language support is an architectural goal; it cannot mean perfect translations to every spoken language in the first development version.
