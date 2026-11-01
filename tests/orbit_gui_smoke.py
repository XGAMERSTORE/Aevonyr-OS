"""Actual Orbit windows under Xvfb. Demo app names are test fixtures, not OS evidence."""
import sys
from pathlib import Path
import time
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from aevonyr.apphub import App
from aevonyr.launcher import AevonyrLauncher
from PIL import ImageGrab

apps=[App('Linux',name, '/tmp/test-'+str(i)+'.desktop') for i,name in enumerate(
    ['Aevonyr Control', 'Firefox ESR', 'Files', 'Kate', 'Konsole', 'Aevonyr Pulse'])]
Path('dist').mkdir(exist_ok=True)
for w,h in [(1440,900),(1024,768)]:
    with patch('aevonyr.launcher.installed_apps',return_value=apps):
        root=AevonyrLauncher()
        root.attributes('-fullscreen',False)
        root.geometry(f'{w}x{h}+0+0')
        try:
            for _ in range(12):root.update();time.sleep(.03)
            assert len(root.visible_apps)==len(apps)
            root.query.set('firefox');root.update()
            assert len(root.visible_apps)==1
            root.query.set('no-result-for-this');root.update()
            assert not root.visible_apps
            root.move_selection(1)  # Must not fail on empty search.
            root.query.set('');root.update()
            root.move_selection(1)
            assert root.listbox.curselection()==(1,)
            assert root.listbox.winfo_height()>80
            assert root.search.winfo_width()>200
            ImageGrab.grab().crop((0,0,w,h)).save(f'dist/orbit-{w}x{h}.png')
            with patch('aevonyr.launcher.start') as start, patch('aevonyr.launcher.launch_command',return_value=['test-app']), patch.object(root,'destroy') as close:
                root.search.focus_force();root.update();root.launch_selected()
                start.assert_called_once_with(['test-app']);close.assert_called_once()
        finally:root.destroy()
print('Orbit search, empty state, keyboard selection, launch and both sizes passed.')
