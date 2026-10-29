# Aevonyr OS 1.0 Eclipse Edition — český návod 💜

**Jeden systém. Dva světy.**

Aevonyr OS 1.0 je experimentální Linux založený na Debianu 13 a KDE Plasma. Obsahuje vlastní grafické prostředí Aevonyr uvnitř KDE, centrum aplikací, vlastní vzhled Eclipse, možnost použití Wine a Waydroidu a panel výkonu Aevonyr Pulse.

## Stažení

1. Otevři [sestavení Aevonyr 1.0 na GitHubu](https://github.com/XGAMERSTORE/Aevonyr-OS/actions/runs/40967194969).
2. **Jen pokud je sestavení zelené**, dole v části **Artifacts** vyber **aevonyr-os-1.0.0-eclipse-live-amd64**.
3. Stáhni ZIP a rozbal ISO: **Aevonyr-OS-1.0.0-Eclipse-Live-amd64.iso**.
4. Pomocí SHA256SUMS ověř, že stažený soubor není poškozený.

Artefakty GitHub Actions mohou po uplynutí doby uchovávání zmizet, proto si ISO ulož.

## Test ve VirtualBoxu

- Nový VM: **Linux → Debian (64-bit)**.
- Paměť: alespoň 4 GB, ideálně 6 GB.
- CPU: 2 až 4 virtuální jádra.
- Disk: **nový prázdný virtuální disk**, alespoň 40 GB.
- Grafika: VMSVGA, 128 MB videopaměti.
- Povolit EFI, pro první test nechat Secure Boot vypnutý.
- Připojit stažený soubor ISO jako virtuální optický disk a spustit VM.

V Live režimu se změny standardně neuchovávají po restartu. Neinstaluj systém na fyzický disk s důležitými soubory, dokud neprojdeme testy instalace a obnovy.

## Co vyzkoušet

- **Aevonyr Pulse:** sleduj skutečné CPU, RAM, disk a animovaný graf.
- **Welcome:** úvodní průvodce, čeština, síť a nastavení aplikací.
- **App Hub:** Linux/Flatpak, Wine a aplikace Waydroid podle kompatibility.
- **Phone Link:** propojení mobilu pomocí KDE Connect.
- **Updates:** KDE Discover a dostupné aktualizace firmwaru.
- **Restore:** Timeshift pro stav systému a Back In Time pro osobní soubory.

V terminálu můžeš zadat příkazy: aevonyr --pulse, aevonyr --diagnose a aevonyr --launcher.

## Stav vydání

**1.0 je zatím Release Candidate.** Úspěšné sestavení a test grafické aplikace nejsou totéž jako plně otestovaný systém ve VirtualBoxu nebo na skutečném počítači. Windows EXE a Android APK nejsou univerzálně kompatibilní.

Zkušební QEMU screenshoty ukazují pokus o grafický start, ale samotné nemohou potvrdit funkčnost přihlášení nebo instalátoru.
