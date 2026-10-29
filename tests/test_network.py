import subprocess
import unittest
from unittest.mock import Mock
from aevonyr.network import network_status, open_network_settings

class TestNetwork(unittest.TestCase):
    def which(self,name): return "/usr/bin/"+name
    def test_connected(self):
        run=Mock(return_value=Mock(returncode=0,stdout="full\n"))
        self.assertEqual(network_status(which=self.which,run=run),"full")
        run.assert_called_once_with(["/usr/bin/nmcli","-t","-f","CONNECTIVITY","general"],capture_output=True,text=True,timeout=4,check=False)
    def test_offline(self):
        for state in ("none","portal","limited","unknown"):
            r=Mock(returncode=0,stdout=state+"\n")
            self.assertEqual(network_status(which=self.which,run=lambda *a,**k:r),state)
    def test_unavailable(self):
        self.assertEqual(network_status(which=lambda n:None),"unavailable")
        def timeout(*a,**k): raise subprocess.TimeoutExpired("nmcli",4)
        self.assertEqual(network_status(which=self.which,run=timeout),"unavailable")
    def test_editor(self):
        p=Mock();open_network_settings(which=self.which,popen=p)
        p.assert_called_once_with(["/usr/bin/nm-connection-editor"],start_new_session=True)
    def test_editor_fallback(self):
        p=Mock()
        open_network_settings(which=lambda n:"/usr/bin/systemsettings" if n=="systemsettings" else None,popen=p)
        p.assert_called_once_with(["/usr/bin/systemsettings","kcm_networkmanagement"],start_new_session=True)
        with self.assertRaises(RuntimeError):open_network_settings(which=lambda n:None,popen=p)
