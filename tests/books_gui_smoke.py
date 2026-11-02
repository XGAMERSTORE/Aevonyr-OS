"""Real Bookish window, isolated temporary user data, no fake installed apps."""
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import ImageGrab
with tempfile.TemporaryDirectory() as data:
    os.environ['XDG_DATA_HOME']=data
    from aevonyr.books import BookishLibrary
    root=BookishLibrary()
    sample=Path(data)/'Ukázková kniha.txt';sample.write_text('Ukázkový text pro GUI test.',encoding='utf-8')
    root.library.add(sample);root.refresh();root.list.selection_set(0);root.select()
    root.progress.set('24');root.notes.insert('1.0','Kapitola 3 · místo, kam se ráda vracím.');root.save()
    root.update()
    assert root.library.all()[0][2]==24
    Path('dist').mkdir(exist_ok=True)
    ImageGrab.grab(bbox=(root.winfo_rootx(),root.winfo_rooty(),root.winfo_rootx()+root.winfo_width(),root.winfo_rooty()+root.winfo_height())).save('dist/bookish-library.png')
    root.close()
