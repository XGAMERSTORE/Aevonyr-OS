import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class LiveBuildConfigTests(unittest.TestCase):
    def test_shell_syntax(self):
        for path in (ROOT/'iso/build.sh', ROOT/'iso/overlays/usr/local/bin/aevonyr-android-setup', ROOT/'iso/overlays/usr/local/bin/aevonyr-installer', ROOT/'iso/overlays/usr/local/bin/aevonyr-colorscheme-init', ROOT/'scripts/qemu-screenshots.sh', ROOT/'iso/hooks/normal/0100-aevonyr-splash.hook.chroot'):
            subprocess.run(['bash','-n',str(path)],check=True)
    def test_package_list(self):
        lines = (ROOT/'iso/package-lists/desktop.list.chroot').read_text().splitlines()
        packages = [x.strip() for x in lines if x.strip() and not x.lstrip().startswith('#')]
        required = {'linux-image-amd64','task-kde-desktop','network-manager','firefox-esr','wine','waydroid','calamares-settings-debian','python3-tk','flatpak','plasma-discover-backend-flatpak','timeshift','backintime-qt','btrfs-progs','fwupd','plasma-discover-backend-fwupd','packagekit','kdeconnect','plasma-systemmonitor'}
        self.assertTrue(required.issubset(set(packages)))
        self.assertEqual(len(packages),len(set(packages)))
    def test_branding(self):
        root = ROOT/'iso/overlays'
        self.assertIn('sddm.login(', (root/'usr/share/sddm/themes/aevonyr/Main.qml').read_text())
        self.assertIn('Current=aevonyr', (root/'etc/sddm.conf.d/20-aevonyr.conf').read_text())
        self.assertIn('plasma-apply-wallpaperimage', (root/'usr/local/bin/aevonyr-wallpaper-init').read_text())
        self.assertIn('quiet splash', (ROOT/'iso/build.sh').read_text())
        self.assertIn('plymouth-set-default-theme -R aevonyr', (ROOT/'iso/hooks/normal/0100-aevonyr-splash.hook.chroot').read_text())

    def test_aevonyr_splash_wired_into_build(self):
        root = ROOT/'iso/overlays/usr/share/plymouth/themes/aevonyr'
        self.assertIn('ModuleName=script',(root/'aevonyr.plymouth').read_text())
        script=(root/'aevonyr.script').read_text()
        self.assertIn('Plymouth.SetRefreshFunction',script)
        self.assertIn('Plymouth.SetDisplayPasswordFunction',script)
        self.assertIn('cp -a "$ROOT/iso/hooks/normal/." config/hooks/normal/',
                      (ROOT/'iso/build.sh').read_text())
        self.assertIn('plymouth-themes',(ROOT/'iso/package-lists/desktop.list.chroot').read_text())

    def test_installer_confirmation(self):
        text=(ROOT/'iso/overlays/usr/local/bin/aevonyr-installer').read_text()
        self.assertIn('kdialog --title',text)
        self.assertIn('exec pkexec /usr/bin/calamares',text)

    def test_app_hub_restore_and_color_scheme(self):
        root = ROOT/'iso/overlays'
        for name, cli in (('aevonyr-launcher.desktop', '--launcher'),
                          ('aevonyr-app-hub.desktop', '--app-hub'),
                          ('aevonyr-restore.desktop', '--restore')):
            self.assertIn('Exec=/usr/local/bin/aevonyr ' + cli,
                          (root/'usr/share/applications'/name).read_text())
        self.assertIn('Name=Aevonyr Eclipse',
                      (root/'usr/share/color-schemes/AevonyrEclipse.colors').read_text())
        self.assertIn('plasma-apply-colorscheme AevonyrEclipse',
                      (root/'usr/local/bin/aevonyr-colorscheme-init').read_text())
        self.assertIn('Aevonyr-OS-1.0.0-Eclipse-Live-amd64.iso', (ROOT/'iso/build.sh').read_text())

    def test_first_run_updates_phone_launchers(self):
        applications = ROOT/'iso/overlays/usr/share/applications'
        for filename, command in (
            ('aevonyr-welcome.desktop','--welcome'),
            ('aevonyr-updates.desktop','--updates'),
            ('aevonyr-phone.desktop','--phone'),
        ):
            content=(applications/filename).read_text()
            self.assertIn('Exec=/usr/local/bin/aevonyr ' + command,content)
        packages=(ROOT/'iso/package-lists/desktop.list.chroot').read_text()
        self.assertIn('kdeconnect',packages)
        self.assertIn('plasma-discover-backend-fwupd',packages)
        self.assertIn('fwupd',packages)

    def test_onboarding_wired_to_desktop(self):
        cli = (ROOT/'aevonyr/__main__.py').read_text()
        for flag in ('--welcome','--updates','--phone'):
            self.assertIn(flag,cli)
        ui=(ROOT/'aevonyr/ui.py').read_text()
        self.assertIn('self.after(750, self._maybe_welcome)',ui)
        self.assertIn('WelcomeWizard(self)',ui)
        self.assertIn('self.nav_canvas',ui)

    def test_release_iso_and_verifier(self):
        config=(ROOT/'.github/workflows/build-linux-iso.yml').read_text()
        self.assertIn('Aevonyr-OS-1.0.0-Eclipse-Live-amd64.iso',config)
        self.assertIn('xorriso -indev "$iso" -ls /live',config)
        self.assertIn('El Torito boot img.*BIOS',config)
        self.assertIn('El Torito boot img.*UEFI',config)
        self.assertIn('grep -Eq "[.]squashfs"',config)
        self.assertNotIn(' -print ',config)
        self.assertIn('Experimental BIOS and UEFI QEMU screenshots',config)
        self.assertIn('continue-on-error: true',config)

    def test_pulse_app(self):
        desktop=(ROOT/'iso/overlays/usr/share/applications/aevonyr-pulse.desktop').read_text()
        self.assertIn('Exec=/usr/local/bin/aevonyr --pulse',desktop)
        self.assertIn('PulsePanel(self.body, self.t)', (ROOT/'aevonyr/ui.py').read_text())

    def test_desktop_files(self):
        files = ROOT/'iso/overlays'
        self.assertIn('Exec=/usr/local/bin/aevonyr',(files/'etc/xdg/autostart/aevonyr-os.desktop').read_text())
        self.assertIn('Exec=/usr/local/bin/aevonyr-installer',(files/'usr/share/applications/aevonyr-install.desktop').read_text())

if __name__=='__main__':
    unittest.main()
