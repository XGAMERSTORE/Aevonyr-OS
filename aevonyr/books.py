"""Bookish's local library. Original books are never modified."""
from pathlib import Path
import os
import sqlite3
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


from .book_library import Library


class BookishLibrary(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Bookish OS · Knihovna pro Niki')
        self.geometry('940x680')
        self.minsize(700, 540)
        self.configure(bg='#f5efe5')
        self.library = Library()
        self.current = None
        self.protocol('WM_DELETE_WINDOW', self.close)
        header = tk.Frame(self, bg='#f5efe5'); header.pack(fill='x', padx=30, pady=22)
        tk.Label(header, text='Bookish', font=('DejaVu Serif', 32), fg='#382e29', bg='#f5efe5').pack(anchor='w')
        tk.Label(header, text='Malý svět velkých příběhů.  ·  Pro Niki', fg='#74685e', bg='#f5efe5').pack(anchor='w')
        actions = tk.Frame(self, bg='#f5efe5'); actions.pack(fill='x', padx=30)
        for label, callback in [('Přidat knížku', self.add), ('Čtečka a správa knih', lambda: self.launch(['calibre'])), ('Psát knihu', lambda: self.launch(['libreoffice','--writer'])), ('Soustředit se', lambda: self.launch(['focuswriter'])), ('Překlad', self.translate)]:
            tk.Button(actions,text=label,command=callback,bg='#b9c6a4',fg='#382e29',relief='flat',padx=10,pady=10).pack(side='left',padx=(0,6))
        body = tk.PanedWindow(self, bg='#f5efe5', sashwidth=14); body.pack(fill='both',expand=True,padx=30,pady=20)
        shelf = tk.Frame(body,bg='#e8dfd2'); body.add(shelf, minsize=220)
        tk.Label(shelf,text='MOJE POLIČKA',bg='#e8dfd2',fg='#74685e',pady=14).pack()
        self.list = tk.Listbox(shelf,bg='#e8dfd2',fg='#382e29',selectbackground='#b9c6a4',relief='flat',borderwidth=0,font=('DejaVu Serif',13),exportselection=False)
        self.list.pack(fill='both',expand=True,padx=12,pady=10)
        self.list.bind('<<ListboxSelect>>', self.select)
        detail=tk.Frame(body,bg='#f5efe5');body.add(detail,minsize=350)
        self.title_label=tk.Label(detail,text='Začni svůj další příběh',wraplength=410,justify='left',anchor='w',font=('DejaVu Serif',23),bg='#f5efe5',fg='#382e29');self.title_label.pack(fill='x',pady=(12,18))
        tk.Button(detail,text='Pokračovat ve čtení →',command=self.read,bg='#b9c6a4',fg='#382e29',relief='flat',pady=12).pack(fill='x')
        tk.Label(detail,text='Přečteno (%) · zaznamenáváš ručně',bg='#f5efe5',fg='#74685e').pack(anchor='w',pady=(20,5))
        self.progress=tk.StringVar(value='0');tk.Spinbox(detail,from_=0,to=100,textvariable=self.progress,width=8).pack(anchor='w')
        tk.Label(detail,text='Myšlenky, citáty a poznámky',bg='#f5efe5',fg='#74685e').pack(anchor='w',pady=(18,5))
        self.notes=tk.Text(detail,height=7,bg='#fffaf2',fg='#382e29',wrap='word',relief='flat',font=('DejaVu Serif',12));self.notes.pack(fill='both',expand=True)
        tk.Button(detail,text='Uložit záložku a poznámky',command=self.save,bg='#e5c8c5',relief='flat',pady=10).pack(fill='x',pady=(10,0))
        self.status=tk.Label(self,text='Knihy zůstávají na původním místě. V režimu Live bez persistence se knihovna po restartu neuchová.',bg='#f5efe5',fg='#74685e',wraplength=880);self.status.pack(padx=25,pady=(0,15))
        self.refresh()

    def refresh(self):
        self.rows=self.library.all();self.list.delete(0,'end')
        for _,title,progress,_ in self.rows:self.list.insert('end',f'{title}   ·   {progress}%')

    def save(self):
        if self.current:
            try:self.library.save(self.current,self.progress.get(),self.notes.get('1.0','end-1c'))
            except (ValueError,sqlite3.Error) as exc:messagebox.showerror('Bookish',str(exc));return False
            self.status.config(text='Záložka a poznámky uloženy v tomto uživatelském účtu.')
        return True

    def select(self,event=None):
        selection=self.list.curselection()
        if not selection:return
        row=self.rows[selection[0]]
        if not self.save():return
        row=next(item for item in self.library.all() if item[0]==row[0])
        self.current=row[0];self.title_label.config(text=row[1]);self.progress.set(str(row[2]));self.notes.delete('1.0','end');self.notes.insert('1.0',row[3])

    def add(self):
        if not self.save():return
        files=filedialog.askopenfilenames(filetypes=[('Knihy','*.epub *.pdf *.txt')])
        for file in files:
            try:self.library.add(file)
            except (ValueError,OSError,sqlite3.Error) as exc:messagebox.showerror('Bookish',str(exc))
        self.refresh()

    def launch(self,command):
        try:subprocess.Popen(command,start_new_session=True)
        except OSError as exc:messagebox.showerror('Bookish',str(exc))

    def read(self):
        if not self.current:return
        if not Path(self.current).is_file():messagebox.showerror('Kniha není dostupná','Připoj disk s knihou nebo ji přidej znovu.');return
        self.save();self.launch(['ebook-viewer' if self.current.lower().endswith('.epub') else 'xdg-open',self.current])

    def translate(self):
        from .book_translation import translation_window
        translation_window(self)

    def close(self):
        if self.save():self.library.db.close();self.destroy()
