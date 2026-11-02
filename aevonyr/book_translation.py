"""Explicit, opt-in translation through a user-selected LibreTranslate service."""
import json
import queue
import threading
import urllib.request
import urllib.parse
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


def api(endpoint, operation, payload=None):
    url = urllib.parse.urlsplit(endpoint.strip())
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError('Zadej HTTPS adresu služby LibreTranslate bez hesla či parametrů v adrese.')
    request = urllib.request.Request(endpoint.rstrip('/')+'/'+operation,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={'Content-Type':'application/json', 'Accept':'application/json'})
    with urllib.request.urlopen(request,timeout=90) as response:
        raw=response.read(4*1024*1024+1)
    if len(raw)>4*1024*1024:raise ValueError('Odpověď služby je příliš velká.')
    data=json.loads(raw)
    if isinstance(data,dict) and data.get('error'):raise ValueError(data['error'])
    return data


def chunks(text, limit=2000):
    # Preserve all input, including paragraph breaks, in ordered chunks.
    for start in range(0,len(text),limit):yield text[start:start+limit]


def translation_window(parent):
    win=tk.Toplevel(parent);win.title('Bookish · Překlad textu');win.geometry('620x540');win.configure(bg='#f5efe5')
    def label(text):tk.Label(win,text=text,bg='#f5efe5',fg='#382e29',wraplength=560,justify='left').pack(anchor='w',padx=24,pady=6)
    label('Překlad knihy / textu · LibreTranslate')
    label('Vyber TXT v UTF-8 (např. text exportovaný z Calibre). Originál zůstane beze změny. Služba může vyžadovat placený API klíč. Jazyková nabídka a kvalita závisí na poskytovateli; nejde o zaručený literární překlad.')
    label('HTTPS adresa služby');endpoint=tk.Entry(win);endpoint.pack(fill='x',padx=24)
    label('API klíč (jen pro toto okno; neukládá se)');key=tk.Entry(win,show='•');key.pack(fill='x',padx=24)
    label('Cílový jazyk – načti nabídku služby');language=tk.StringVar();menu=tk.OptionMenu(win,language,'');menu.pack(anchor='w',padx=24)
    status=tk.Label(win,text='',bg='#f5efe5',wraplength=560);status.pack(padx=24,pady=12)
    events=queue.Queue();busy=False;codes={}
    def launch(job):
        nonlocal busy
        if busy:return
        busy=True
        def work():
            try:job()
            except Exception as exc:events.put(('error',str(exc)))
        threading.Thread(target=work,daemon=True).start()
    def languages():
        address=endpoint.get()
        launch(lambda:events.put(('languages',api(address,'languages'))))
    tk.Button(win,text='Načíst jazyky',command=languages).pack(anchor='w',padx=24)
    def translate():
        if busy:return
        target=codes.get(language.get())
        if not target:messagebox.showerror('Bookish','Nejprve načti a vyber jazyk.',parent=win);return
        source=filedialog.askopenfilename(parent=win,filetypes=[('Text UTF-8','*.txt')])
        if not source:return
        try:
            if Path(source).stat().st_size>5*1024*1024:raise ValueError('Limit je 5 MB textu. Rozděl knihu na kapitoly.')
            text=Path(source).read_text(encoding='utf-8')
        except (OSError,UnicodeError,ValueError) as exc:messagebox.showerror('Bookish',str(exc),parent=win);return
        address=endpoint.get();secret=key.get()
        if not messagebox.askyesno('Odeslat text?',f'Celý vybraný text bude odeslán službě {address}. Pokračovat?',parent=win):return
        def work():
            translated=[];parts=list(chunks(text))
            for index,part in enumerate(parts):
                events.put(('progress',f'Překládám část {index+1}/{len(parts)}…'))
                data=api(address,'translate',{'q':part,'source':'auto','target':target,'format':'text','api_key':secret})
                if not isinstance(data,dict) or not isinstance(data.get('translatedText'),str):raise ValueError('Služba nevrátila přeložený text.')
                translated.append(data['translatedText'])
            events.put(('done',(''.join(translated),source)))
        launch(work)
    tk.Button(win,text='Vybrat text a přeložit',command=translate,bg='#b9c6a4').pack(anchor='w',padx=24,pady=12)
    def poll():
        nonlocal busy
        try:
            while True:
                kind,value=events.get_nowait()
                if kind=='progress':status.config(text=value);continue
                busy=False
                if kind=='languages':
                    codes.clear();menu['menu'].delete(0,'end')
                    for item in value:
                        name=item['name'];codes[name]=item['code'];menu['menu'].add_command(label=name,command=lambda n=name:language.set(n))
                    language.set(next(iter(codes),''));status.config(text=f'Dostupných jazyků: {len(codes)}')
                elif kind=='error':status.config(text=value)
                else:
                    result,source=value
                    destination=filedialog.asksaveasfilename(parent=win,initialfile=Path(source).stem+'-preklad.txt',defaultextension='.txt')
                    if destination:
                        if Path(destination).resolve()==Path(source).resolve():status.config(text='Originál nepřepisujeme. Spusť překlad znovu a zvol jiný soubor.');continue
                        try:Path(destination).write_text(result,encoding='utf-8');status.config(text='Překlad uložen. Zkontroluj význam, jména a styl.')
                        except OSError as exc:status.config(text=str(exc))
        except queue.Empty:pass
        if win.winfo_exists():win.after(150,poll)
    win.after(150,poll)
    def close():
        if busy:messagebox.showinfo('Bookish','Nejprve počkej na dokončení požadavku.',parent=win)
        else:win.destroy()
    win.protocol('WM_DELETE_WINDOW',close)
