import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class LiveBuildConfigTests(unittest.TestCase):
    def test_shell_syntax(self):
        for path in (ROOT/'iso/build.sh', ROOT/'iso/overlays/usr/local/bin/aevonyr-android-setup'):
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
        self.assertIn('plymouth-set-default-theme -R breeze', (ROOT/'iso/hooks/normal/0100-aevonyr-splash.hook.chroot').read_text())

    def test_desktop_files(self):
        files = ROOT/'iso/overlays'
        self.assertIn('Exec=/usr/local/bin/aevonyr',(files/'etc/xdg/autostart/aevonyr-os.desktop').read_text())
        self.assertIn('Exec=pkexec /usr/bin/calamares',(files/'usr/share/applications/aevonyr-install.desktop').read_text())

if __name__=='__main__':
    unittest.main()
