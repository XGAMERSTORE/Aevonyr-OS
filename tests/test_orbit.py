import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from aevonyr.apphub import App
from aevonyr.launcher import matching_apps

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('orbit_setup', str(ROOT / 'iso/overlays/usr/local/bin/aevonyr-orbit-layout'))
spec = importlib.util.spec_from_loader(loader.name, loader)
setup = importlib.util.module_from_spec(spec)
loader.exec_module(setup)

class SearchTests(unittest.TestCase):
    def test_multiword_source_and_name(self):
        apps = [App('Flatpak', 'Visual Studio Code', 'one'), App('Linux', 'Code', 'two')]
        self.assertEqual(matching_apps(apps, 'flatpak code'), apps[:1])
        self.assertEqual(matching_apps(apps, 'not installed'), [])
    def test_exact_and_prefix_rank_before_substring(self):
        apps = [App('Linux', 'A Code Tool', 'a'), App('Linux', 'Code Editor', 'b'), App('Linux', 'Code', 'c')]
        self.assertEqual([a.identifier for a in matching_apps(apps, 'CODE')], ['c', 'b', 'a'])

class LayoutSafetyTests(unittest.TestCase):
    def test_existing_users_not_migrated_automatically(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(setup.os, 'geteuid', return_value=1000), patch.object(setup.Path, 'home', return_value=Path(tmp)), patch.dict(setup.os.environ, {'XDG_CONFIG_HOME':tmp+'/config','XDG_STATE_HOME':tmp+'/state'}), patch('sys.argv', ['setup', '--auto']), patch.object(setup.subprocess, 'run') as run:
            self.assertEqual(setup.main(), 0)
            run.assert_not_called()
    def test_restore_failure_to_stop_never_overwrites_config(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            config=Path(tmp)/'config';config.mkdir()
            state=Path(tmp)/'state/aevonyr';state.mkdir(parents=True)
            rc=config/'plasma-org.kde.plasma.desktop-appletsrc';rc.write_text('current')
            (state/'pre-orbit-appletsrc').write_text('previous')
            with patch.object(setup.os, 'geteuid', return_value=1000), patch.dict(setup.os.environ, {'XDG_CONFIG_HOME':str(config),'XDG_STATE_HOME':tmp+'/state'}), patch('sys.argv', ['setup','restore']), patch.object(setup.subprocess, 'run', side_effect=subprocess.CalledProcessError(1,'systemctl')):
                with self.assertRaises(subprocess.CalledProcessError): setup.main()
            self.assertEqual(rc.read_text(), 'current')
    def test_restore_clears_autostart_token_and_keeps_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            config=Path(tmp)/'config';(config/'aevonyr').mkdir(parents=True)
            state=Path(tmp)/'state/aevonyr';state.mkdir(parents=True)
            backup=state/'pre-orbit-appletsrc';backup.write_text('previous')
            (state/'orbit-layout-v1').touch();(config/'aevonyr/orbit-first-login').touch()
            with patch.object(setup.os, 'geteuid', return_value=1000), patch.dict(setup.os.environ, {'XDG_CONFIG_HOME':str(config),'XDG_STATE_HOME':tmp+'/state'}), patch('sys.argv', ['setup','restore']), patch.object(setup.subprocess, 'run') as run:
                self.assertEqual(setup.main(),0)
                self.assertEqual(run.call_count,2)
            self.assertEqual((config/'plasma-org.kde.plasma.desktop-appletsrc').read_text(),'previous')
            self.assertTrue(backup.exists())
            self.assertFalse((config/'aevonyr/orbit-first-login').exists())
