from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import tempfile
import unittest
import subprocess
from aevonyr.packages import package_command, apk_package_id, install_apk, checked
from aevonyr.compat import CompatibilityError

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.which = lambda name: '/usr/bin/' + name
    def file(self, name):
        p = self.path / name
        p.write_bytes(b'test')
        return p
    def result(self, text='', code=0):
        return SimpleNamespace(stdout=text, stderr='', returncode=code)
    def test_windows_and_deb_paths_are_single_arguments(self):
        for suffix in ['EXE', 'msi', 'deb']:
            path = self.file('name $(touch pwned); space.' + suffix)
            command = package_command(path, self.which)
            self.assertEqual(command[-1], str(path))
            self.assertNotIn('sh', command)
        self.assertEqual(command[:2], ('/usr/bin/plasma-discover', '--local-filename'))
    def test_unknown_and_missing_file_do_not_launch(self):
        for path in [self.file('x.txt'), self.path/'missing.exe']:
            with self.assertRaises(CompatibilityError): package_command(path, self.which)
    def test_package_id_validated(self):
        path = self.file('x.apk')
        run = Mock(return_value=self.result("package: name='com.example.demo' versionCode='1'"))
        self.assertEqual(apk_package_id(path, self.which, run), 'com.example.demo')
        run.return_value = self.result("package: name='com.example;evil'")
        with self.assertRaises(CompatibilityError): apk_package_id(path, self.which, run)
    def test_failed_command_reports_error(self):
        with self.assertRaisesRegex(CompatibilityError, 'INSTALL_FAILED'):
            checked(['test'], run=Mock(return_value=self.result('INSTALL_FAILED', 1)))
    def test_timeout_propagates(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            checked(['test'], run=Mock(side_effect=subprocess.TimeoutExpired('test', 1)))
    def test_android_setup_required_without_install(self):
        path=self.file('x.apk')
        run=Mock(return_value=self.result("package: name='com.example.demo'"))
        with patch.dict('os.environ', {'XDG_SESSION_TYPE':'wayland'}), patch('aevonyr.packages.Path.is_file', side_effect=[True, True, False]):
            with self.assertRaisesRegex(CompatibilityError, 'one-time setup'):
                install_apk(path, which=self.which, run=run)
        self.assertEqual(run.call_count, 1)
    def test_android_start_then_install(self):
        path=self.file('x.apk')
        run=Mock(side_effect=[self.result("package: name='com.example.demo'"),
            self.result('Session: STOPPED'),
            self.result('Session: RUNNING\nContainer: RUNNING'),self.result(), self.result('packageName: com.example.demo')])
        popen=Mock()
        with patch.dict('os.environ', {'XDG_SESSION_TYPE':'wayland'}), patch('aevonyr.packages.Path.is_file', return_value=True):
            package=install_apk(path, which=self.which, run=run, popen=popen)
        self.assertEqual(package, 'com.example.demo')
        self.assertEqual(popen.call_args.args[0], ['/usr/bin/waydroid','session','start'])
        self.assertEqual(run.call_args_list[-2].args[0], ['/usr/bin/waydroid','app','install',str(path)])
    def test_install_failure_never_returns_success(self):
        path=self.file('x.apk')
        run=Mock(side_effect=[self.result("package: name='com.example.demo'"),
            self.result('Session: RUNNING'),self.result('Session: RUNNING\nContainer: RUNNING'),
            self.result('INSTALL_FAILED_NO_MATCHING_ABIS', 1)])
        with patch.dict('os.environ', {'XDG_SESSION_TYPE':'wayland'}), patch('aevonyr.packages.Path.is_file', return_value=True):
            with self.assertRaisesRegex(CompatibilityError, 'NO_MATCHING_ABIS'):
                install_apk(path, which=self.which, run=run)

    def test_android_zero_exit_failure_is_not_success(self):
        path=self.file('x.apk')
        run=Mock(side_effect=[self.result("package: name='com.example.demo'"),
            self.result('Session: RUNNING'),self.result('Session: RUNNING\nContainer: RUNNING'),
            self.result('Failure [INSTALL_FAILED_INVALID_APK]')])
        with patch.dict('os.environ', {'XDG_SESSION_TYPE':'wayland'}), patch('aevonyr.packages.Path.is_file', return_value=True):
            with self.assertRaisesRegex(CompatibilityError, 'INVALID_APK'):
                install_apk(path, which=self.which, run=run)
