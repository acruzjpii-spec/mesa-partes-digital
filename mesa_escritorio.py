"""Interfaz gráfica local de respaldo. Usa los mismos algoritmos y CSV de la web."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from mesa_consola import (registrar_expediente, consultar_expediente, listar_ordenados,
                          actualizar_estado, ESTADOS)
from app.algoritmos import guardar_csv

ARCHIVO = Path(__file__).resolve().parent / 'datos' / 'respaldo_web.csv'

class MesaApp:
    def __init__(self, root, archivo=ARCHIVO):
        self.root, self.archivo = root, Path(archivo)
        root.title('Mesa de Partes Digital - UPN')
        root.geometry('1000x730')
        root.minsize(760, 580)
        root.configure(bg='#edf2f7')
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TFrame', background='#edf2f7')
        style.configure('TLabel', background='#edf2f7', foreground='#17314a', font=('Segoe UI', 11))
        style.configure('TLabelframe', background='#edf2f7', padding=12)
        style.configure('TLabelframe.Label', background='#edf2f7', foreground='#17314a', font=('Segoe UI', 12, 'bold'))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        style.configure('Treeview', rowheight=30, font=('Segoe UI', 10))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        banner = tk.Frame(root, bg='#17314a', padx=24, pady=18)
        banner.pack(fill='x')
        tk.Label(banner, text='MESA DE PARTES DIGITAL', bg='#17314a', fg='white', font=('Segoe UI', 22, 'bold')).pack(anchor='w')
        tk.Label(banner, text='UPN | Fundamentos de Programación | Demostración local', bg='#17314a', fg='#c6e4ed', font=('Segoe UI', 11)).pack(anchor='w')
        body = ttk.Frame(root, padding=18)
        body.pack(fill='both', expand=True)
        self.asunto, self.remitente, self.dni, self.codigo = [tk.StringVar() for _ in range(4)]
        self.estado = tk.StringVar(value='recibido')
        self.aviso = tk.StringVar(value='Usar datos ficticios. Los cambios se guardan automáticamente.')
        self.total = tk.StringVar()
        top = ttk.Frame(body)
        top.pack(fill='x')
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        reg = ttk.LabelFrame(top, text='1. Registrar expediente')
        reg.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        consulta = ttk.LabelFrame(top, text='2. Buscar y actualizar')
        consulta.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        for parent in (reg, consulta): parent.columnconfigure(0, weight=1)
        for i, (label, var) in enumerate((('Asunto', self.asunto), ('Remitente ficticio', self.remitente), ('DNI opcional (8 dígitos)', self.dni))):
            ttk.Label(reg, text=label).grid(row=i*2, column=0, sticky='w')
            ttk.Entry(reg, textvariable=var).grid(row=i*2+1, column=0, sticky='ew', pady=(0, 8))
        ttk.Button(reg, text='Registrar y guardar', command=self.registrar).grid(row=6, column=0, sticky='ew')
        ttk.Label(consulta, text='Código de expediente').grid(row=0, column=0, sticky='w')
        ttk.Entry(consulta, textvariable=self.codigo).grid(row=1, column=0, sticky='ew', pady=(0,8))
        ttk.Button(consulta, text='Buscar expediente', command=self.buscar).grid(row=2, column=0, sticky='ew')
        ttk.Label(consulta, text='Nuevo estado').grid(row=3, column=0, sticky='w', pady=(10,0))
        ttk.Combobox(consulta, textvariable=self.estado, values=ESTADOS, state='readonly').grid(row=4, column=0, sticky='ew', pady=(0,8))
        ttk.Button(consulta, text='Actualizar estado', command=self.actualizar).grid(row=5, column=0, sticky='ew')
        tools = ttk.Frame(body)
        tools.pack(fill='x', pady=(14, 8))
        ttk.Label(tools, textvariable=self.total, font=('Segoe UI', 12, 'bold')).pack(side='left')
        ttk.Button(tools, text='Exportar CSV', command=self.exportar).pack(side='right')
        ttk.Button(tools, text='Actualizar lista', command=self.refrescar).pack(side='right', padx=8)
        ttk.Label(body, textvariable=self.aviso, wraplength=900).pack(fill='x', pady=(12, 0))
        table = ttk.Frame(body)
        table.pack(fill='both', expand=True)
        cols = ('codigo', 'asunto', 'remitente', 'estado')
        self.tabla = ttk.Treeview(table, columns=cols, show='headings', selectmode='browse')
        for col, label, width in zip(cols, ('Código', 'Asunto', 'Remitente', 'Estado'), (120, 300, 210, 120)):
            self.tabla.heading(col, text=label)
            self.tabla.column(col, width=width, minwidth=75)
        scroll = ttk.Scrollbar(table, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.tabla.pack(fill='both', expand=True)
        self.tabla.bind('<<TreeviewSelect>>', self.seleccionar)
        self.refrescar()

    def refrescar(self):
        filas = listar_ordenados(self.archivo)
        self.tabla.delete(*self.tabla.get_children())
        for e in filas:
            self.tabla.insert('', 'end', values=tuple(e[k] for k in ('codigo','asunto','remitente','estado')))
        self.total.set(f'Expedientes registrados: {len(filas)}')

    def registrar(self):
        try:
            e = registrar_expediente(self.archivo, self.asunto.get(), self.remitente.get(), self.dni.get())
            self.codigo.set(e['codigo'])
            for var in (self.asunto, self.remitente, self.dni): var.set('')
            self.refrescar()
            self.aviso.set('Registro correcto. Código: ' + e['codigo'])
        except (ValueError, OSError) as exc:
            self.aviso.set('Error: ' + str(exc))

    def seleccionar(self, _event=None):
        seleccion = self.tabla.selection()
        if seleccion:
            v = self.tabla.item(seleccion[0], 'values')
            self.codigo.set(v[0]); self.estado.set(v[3])

    def buscar(self):
        e = consultar_expediente(self.archivo, self.codigo.get())
        if e:
            self.estado.set(e['estado'])
            self.aviso.set(f"{e['codigo']} | {e['asunto']} | {e['remitente']} | {e['estado']}")
        else: self.aviso.set('Expediente no encontrado.')

    def actualizar(self):
        try:
            if actualizar_estado(self.archivo, self.codigo.get(), self.estado.get()):
                self.refrescar(); self.aviso.set('Estado actualizado y guardado.')
            else: self.aviso.set('Expediente no encontrado.')
        except (ValueError, OSError) as exc: self.aviso.set('Error: ' + str(exc))

    def exportar(self):
        destino = filedialog.asksaveasfilename(defaultextension='.csv', initialfile='expedientes.csv', filetypes=[('CSV', '*.csv')])
        if destino:
            try:
                guardar_csv(destino, listar_ordenados(self.archivo))
                self.aviso.set('Archivo exportado: ' + destino)
            except OSError as exc: self.aviso.set('Error de exportación: ' + str(exc))

if __name__ == '__main__':
    root = tk.Tk()
    MesaApp(root)
    root.mainloop()
