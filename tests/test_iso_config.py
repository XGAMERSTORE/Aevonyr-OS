import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class LiveBuildConfigTests(unittest.TestCase):
    def test_shell_syntax(self):
        for path in (ROOT/'iso/build.sh', ROOT/'iso/overlays/usr/local/bin/aevonyr-android-setup', ROOT/'iso/overlays/usr/local/bin/aevonyr-installer', ROOT/'iso/hooks/normal/0100-aevonyr-splash.hook.chroot'):
            subprocess.run(['bash','-n',str(path)],check=True)
    def test_package_list(self):
        lines = (ROOT/'iso/package-lists/desktop.list.chroot').read_text().splitlines()
        packages = [x.strip() for x in lines if x.strip() and not x.lstrip().startswith('#')]
        required = {'linux-image-amd64','task-kde-desktop','network-manager','firefox-esr','wine','waydroid','calamares-settings-debian','python3-tk'}
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

    def test_desktop_files(self):
        files = ROOT/'iso/overlays'
        self.assertIn('Exec=/usr/local/bin/aevonyr',(files/'etc/xdg/autostart/aevonyr-os.desktop').read_text())
        self.assertIn('Exec=/usr/local/bin/aevonyr-installer',(files/'usr/share/applications/aevonyr-install.desktop').read_text())

if __name__=='__main__':
    unittest.main()
