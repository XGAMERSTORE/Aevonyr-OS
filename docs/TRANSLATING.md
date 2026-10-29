# Localization in Aevonyr OS

English is the default UI language. The 10 built-in languages are at different translation stages. Missing keys fall back to English.

Additional languages are installable JSON files. They contain data, not executable code.
The example language-packs/nl-NL.json has locale, name and strings fields. It demonstrates adding Dutch without modifying Python code.

Install a pack from Settings > Import language pack, or use:

    python3 -m aevonyr --install-language language-packs/nl-NL.json
    python3 -m aevonyr --languages

Installed packs live at XDG_DATA_HOME/aevonyr-os/languages (by default ~/.local/share/aevonyr-os/languages). They load at startup and import applies immediately.
Region and script language codes are accepted (such as pt-BR and zh-Hans), but content requires actual translations.
Validation limits data files to 256 KiB and rejects invalid keys/values.
Do not claim all languages are fully translated. RTL layouts, fonts, plurals and date/number formatting still need engineering and native-speaker QA.
To contribute, translate keys from aevonyr/locales.json English catalog and run the Python tests.
