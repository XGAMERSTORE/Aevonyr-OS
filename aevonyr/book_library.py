"""Persistent local bookshelf, independent of graphical libraries."""
from pathlib import Path
import os
import sqlite3

class Library:
    def __init__(self, directory=None):
        directory = Path(directory or Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))/'bookish')
        directory.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(directory/'library.sqlite3')
        self.db.execute('CREATE TABLE IF NOT EXISTS books (path TEXT PRIMARY KEY, title TEXT, progress INTEGER DEFAULT 0, notes TEXT DEFAULT "", updated INTEGER DEFAULT 0)')
        self.db.commit()

    def add(self, filename):
        path = Path(filename).resolve()
        if not path.is_file() or path.suffix.lower() not in {'.epub', '.pdf', '.txt'}:
            raise ValueError('Choose an EPUB, PDF or TXT file.')
        self.db.execute('INSERT OR IGNORE INTO books(path,title) VALUES (?,?)', (str(path), path.stem))
        self.db.commit()

    def all(self):
        return self.db.execute('SELECT path,title,progress,notes FROM books ORDER BY updated DESC, title COLLATE NOCASE').fetchall()

    def save(self, path, progress, notes):
        progress = int(progress)
        if not 0 <= progress <= 100: raise ValueError('Reading progress must be between 0 and 100.')
        self.db.execute('UPDATE books SET progress=?,notes=?,updated=unixepoch() WHERE path=?', (progress, notes, path))
        self.db.commit()


