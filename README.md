# Purificación de Agua Mediante Contacto Indirecto con Plasma

Sistema de generación de plasma frío en aire a presión atmosférica para el tratamiento de agua en un vaso Petri, integrado con un sistema IoT de captura continua, almacenamiento local estructurado y monitoreo térmico en tiempo real para validar la transferencia de energía plasma-agua.

##  Integrantes del Equipo
* **Grupo 2**
* Angelo Fisicaro
* Franco Fisicaro
* Francisco Osorio
* Joaquín Vásquez
* **Asignatura:** TEI201 — Taller de Diseño en Ingeniería (Sección 1, UAI)
* **Profesor:** Camilo Vásquez Wilson | **Ayudante:** Martín Raguileo

##  Problema que Resuelve (Referencia al Avance 1)
Los métodos convencionales de tratamiento hídrico presentan limitaciones críticas frente a microcontaminantes emergentes (fármacos, pesticidas y disruptores endocrinos): la ultrafiltración no retiene compuestos traza, la ósmosis inversa sufre ensuciamiento de membranas con alto consumo energético y los tratamientos biológicos generan lodos residuales. Este proyecto implementa un reactor de plasma no sellado en contacto indirecto con el agua que degrada contaminantes mediante oxidación avanzada, utilizando un sistema de monitoreo térmico continuo para comprobar empíricamente la interacción entre la descarga de plasma y el agua.

##  Componentes Necesarios para Replicar el Hardware
* 1x Microcontrolador Arduino Leonardo.
* 1x Sensor de temperatura digital impermeable DS18B20 (rango -55 °C a 125 °C, precisión ±0,5 °C, protocolo 1-Wire).
* 1x Protoboard, cables jumper y resistencia pull-up / variable.
* 2x Agujas metálicas (electrodos de descarga separados a 4 mm).
* 1x Vaso Petri de vidrio (encaje de 60 mm de diámetro).
* 1x Lámina de cobre (40 × 40 mm con lengüeta lateral) como electrodo pasivo de referencia a tierra (0 V).
* Estructura modular **Modelo Plasma V2** en madera MDF de 5.5 mm (Base de Torre de 80x80x25 mm, Base de Petri de 110x110x20 mm, Puente de Electrodo de 125x30x5 mm y eje vertical de 130 mm con fijaciones desmontables).

## Estructura del Repositorio
- [firmware/](firmware/) — Código fuente en Arduino C++ y dashboard de monitoreo térmico en Python.
- [hardware/](hardware/) — Esquemático eléctrico, lista de materiales con costos (`BOM.xlsx`) y fotos del prototipo.
- [diseno-3D/](diseno-3D/) — Modelo paramétrico en Fusion 360 (`.f3d`), planos técnicos en PDF, corte láser (`.dxf`) y renders.
- [testing/](testing/) — Protocolo experimental, logs cuantitativos de temperatura y análisis de fallas.
- [docs/](docs/) — Informe técnico final en PDF y documentación complementaria.
- [FUENTES.md](FUENTES.md) — Declaración de librerías, código adaptado, bibliografía científica y uso de IA.

##  Instrucciones para Cargar el Firmware y Conectar el Dashboard
1. **Conexión de Hardware:** Conectar el pin de datos del sensor DS18B20 al pin digital 2 del Arduino Leonardo (`SENSOR_PIN 2`), junto con alimentación (VCC), tierra (GND) y su resistencia en la protoboard según el plano en `hardware/esquematico.pdf`.
2. **Carga del Firmware:**
   * Abrir el archivo `firmware/main.ino` en **Arduino IDE**.
   * Instalar las librerías `OneWire` y `DallasTemperature` desde el Gestor de Librerías.
   * Seleccionar la placa **Arduino Leonardo**, elegir el puerto COM correspondiente y subir el código.
3. **Conexión del Dashboard y Repositorio de Datos:**
   * Instalar las dependencias en Python ejecutando en la terminal:
```bash
pip install pyserial matplotlib

"""Dashboard de temperatura del agua (DS18B20).

Arduino transmite tiempo y temperatura por el puerto serial a 4 Hz nominales.
Este programa valida, visualiza y guarda cada lectura, y finaliza el registro
cuando la temperatura alcanza o supera el objetivo indicado por el operador.
No controla la fuente de alto voltaje ni constituye un sistema de seguridad.

Ejecutar: python registro_temperatura.py
Dependencias: python -m pip install pyserial matplotlib
"""

# 1. Bibliotecas estándar de Python: archivos, cálculos, tiempo e interfaz.
import csv
import math
import json
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Bibliotecas externas: comunicación USB/serial y gráficos de Matplotlib.
import serial
from serial.tools import list_ports
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# 2. Configuración del protocolo y de las carpetas del repositorio.
# El baud rate debe coincidir exactamente con Serial.begin() en Arduino.
VELOCIDAD = 9600
INTERVALO_GUI_MS = 100  # Consulta del puerto; NO es la frecuencia del sensor.
TIEMPO_SIN_DATOS_S = 5  # Alerta de pérdida de lecturas válidas.
HEADER = ('tiempo_s', 'temperatura_C')
# Colocar registro_temperatura.py en la raíz del repositorio.
REPOSITORIO = Path(__file__).resolve().parent
CARPETA_MEDICIONES = REPOSITORIO / 'testing' / 'mediciones'


# 3. Funciones independientes: validación y recuperación de datos.
def parse_target(value):
    """Acepta coma o punto decimal. El objetivo corresponde a agua líquida."""
    target = float(value.strip().replace(',', '.'))
    if not math.isfinite(target) or not 0 <= target <= 100:
        raise ValueError('Introduce una temperatura objetivo entre 0 y 100 °C.')
    return target


def reached_target(temp, target):
    """Se usa >= porque el sensor puede saltarse el valor exacto del objetivo."""
    return target is not None and temp >= target


def indicators(data):
    """Calcula indicadores a partir de las mediciones crudas, sin modificarlas."""
    if not data:
        return None, None, None
    delta = data[-1][1] - data[0][1]
    mean = math.fsum(p[1] for p in data) / len(data)
    dt = data[-1][0] - data[0][0]
    hz = (len(data) - 1) / dt if dt > 0 else None
    return delta, mean, hz



def parse_measurement(line):
    """Descarta encabezados, errores, infinitos y lecturas fuera del rango."""
    try:
        # Arduino transmite dos valores separados por coma: segundos y °C.
        a, b = line.strip().split(',')
        t, temp = float(a), float(b)
    except (ValueError, TypeError):
        return None
    if not (math.isfinite(t) and math.isfinite(temp) and t >= 0 and -55 <= temp <= 125):
        return None
    return t, temp


def load_csv(path):
    """Recupera un registro generado por esta aplicacion."""
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        if tuple(next(reader, [])) != HEADER:
            raise ValueError('El archivo debe tener las columnas tiempo_s,temperatura_C.')
        data = []
        for i, row in enumerate(reader, 2):
            if not row:
                continue
            point = parse_measurement(','.join(row))
            if point is None or (data and point[0] <= data[-1][0]):
                raise ValueError(f'Medición inválida o tiempo no creciente en fila {i}.')
            data.append(point)
        return data


# 4. Aplicación gráfica: mantiene el estado de una sesión y sus controles.
class App:
    def __init__(self, root):
        """Construye la ventana y prepara las variables de medición."""
        self.root = root
        root.title('Registro de temperatura | DS18B20')
        root.geometry('1200x740')
        root.minsize(760, 470)
        # Recursos abiertos únicamente mientras se está registrando.
        self.ser = self.out = self.writer = None
        self.path = None
        self.buffer = b''
        self.first_time = self.last_raw = None
        self.data = []
        self.port_map = {}
        self.folder = CARPETA_MEDICIONES
        self.active_target = None  # Límite fijo durante el experimento.
        self.last_valid_at = None  # Reloj del PC para detectar falta de lecturas.
        self.target = tk.StringVar()  # Sin objetivo por defecto: el usuario lo elige.
        self.delta = tk.StringVar(value='— °C')
        self.mean = tk.StringVar(value='— °C')
        self.hz = tk.StringVar(value='— Hz')
        self.alert = tk.StringVar(value='Sin registro activo.')
        self.port = tk.StringVar()
        self.temp = tk.StringVar(value='— °C')
        self.elapsed = tk.StringVar(value='— s')
        self.count = tk.StringVar(value='0 mediciones')
        self.status = tk.StringVar(value='Selecciona el puerto o abre un experimento anterior.')
        self.filename = tk.StringVar(value='Ningún archivo abierto')

        # 4.1. Encabezado, selector de puerto y botones de control.
        outer = ttk.Frame(root, padding=12)
        outer.pack(fill='both', expand=True)
        header = ttk.Frame(outer)
        header.pack(fill='x', pady=(0, 10))
        ttk.Label(header, text='Registro de temperatura', font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        ttk.Label(header, text='DS18B20  •  Temperatura del agua  •  Adquisición por USB').pack(anchor='w')
        toolbar = ttk.Frame(outer)
        toolbar.pack(fill='x', pady=(0, 7))
        ttk.Label(toolbar, text='Puerto:').pack(side='left')
        self.ports = ttk.Combobox(toolbar, textvariable=self.port, state='readonly', width=23)
        self.ports.pack(side='left', padx=5)
        self.refresh_button = ttk.Button(toolbar, text='Actualizar', command=self.refresh_ports)
        self.refresh_button.pack(side='left', padx=2)
        self.start_button = ttk.Button(toolbar, text='Iniciar y guardar', command=self.start)
        self.start_button.pack(side='left', padx=2)
        self.stop_button = ttk.Button(toolbar, text='Detener', command=self.stop, state='disabled')
        self.stop_button.pack(side='left', padx=2)
        self.open_button = ttk.Button(toolbar, text='Abrir CSV', command=self.open_file)
        self.open_button.pack(side='left', padx=2)
        self.export_button = ttk.Button(toolbar, text='Exportar PNG', command=self.export, state='disabled')
        self.export_button.pack(side='left', padx=2)

        # 4.2. El operador fija la temperatura antes de comenzar.
        target_bar = ttk.Frame(outer)
        target_bar.pack(fill='x', pady=(4, 4))
        ttk.Label(target_bar, text='Temperatura objetivo (°C):').pack(side='left')
        self.target_entry = ttk.Entry(target_bar, textvariable=self.target, width=10)
        self.target_entry.pack(side='left', padx=6)
        ttk.Label(target_bar, text='El registro se detiene al alcanzar o superar el objetivo.').pack(side='left')
        ttk.Label(outer, textvariable=self.alert, foreground='#9C4100', wraplength=900).pack(anchor='w')

        # 4.3. Indicadores derivados de cada nueva medición.
        metrics = ttk.Frame(outer)
        metrics.pack(fill='x', pady=(6, 12))
        for col, (caption, variable) in enumerate([('Temperatura', self.temp), ('Tiempo (desde inicio)', self.elapsed), ('Registro', self.count), ('ΔT', self.delta), ('Promedio', self.mean), ('Frecuencia real', self.hz)]):
            frame = ttk.Frame(metrics, padding=(10, 4))
            frame.grid(row=col // 3, column=col % 3, sticky='ew')
            metrics.columnconfigure(col % 3, weight=1)
            ttk.Label(frame, text=caption).pack(anchor='w')
            ttk.Label(frame, textvariable=variable, font=('Segoe UI', 16, 'bold')).pack(anchor='w')

        # 4.4. Gráfico Matplotlib incrustado y tabla desplazable Tkinter.
        panes = ttk.Panedwindow(outer, orient='horizontal')
        panes.pack(fill='both', expand=True)
        graph = ttk.Frame(panes)
        table = ttk.Frame(panes, padding=(8, 0, 0, 0))
        panes.add(graph, weight=3)
        panes.add(table, weight=1)
        self.figure = Figure(figsize=(6, 4), dpi=100, layout='constrained')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Temperatura en función del tiempo')
        self.ax.set_xlabel('Tiempo (s)')
        self.ax.set_ylabel('Temperatura (°C)')
        self.ax.grid(True, alpha=0.25)
        self.line, = self.ax.plot([], [], color='#087E8B', linewidth=1.7, marker='.', markersize=4)
        # Línea horizontal que muestra el límite configurado en el gráfico.
        self.target_line = self.ax.axhline(0, color='#C44E28', linestyle='--', linewidth=1.2, visible=False)
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph)
        nav = NavigationToolbar2Tk(self.canvas, graph, pack_toolbar=False)
        nav.update()
        nav.pack(side='bottom', fill='x')
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        ttk.Label(table, text='Mediciones', font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(2, 6))
        inner = ttk.Frame(table)
        inner.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(inner, columns=('t', 'temp'), show='headings')
        for col, label in [('t', 'Tiempo (s)'), ('temp', 'Temp. (°C)')]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=100, minwidth=80, anchor='e')
        scroll = ttk.Scrollbar(inner, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        ttk.Label(outer, textvariable=self.filename, wraplength=720).pack(anchor='w', pady=(8, 2))
        ttk.Label(outer, textvariable=self.status, wraplength=720).pack(anchor='w')
        self.refresh_ports()
        self.redraw()
        # 4.5. Tkinter mantiene la interfaz activa sin un bucle bloqueante.
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(INTERVALO_GUI_MS, self.poll)

    def refresh_ports(self):
        """Detecta los puertos COM disponibles sin fijar COM3 para todos los PC."""
        previous = self.port.get()
        self.port_map = {f'{p.device} — {p.description}': p.device for p in list_ports.comports()}
        values = list(self.port_map)
        self.ports['values'] = values
        self.port.set(previous if previous in values else (values[0] if values else ''))

    def set_running(self, running):
        """Bloquea cambios de puerto y objetivo durante una sesión activa."""
        self.target_entry.configure(state='disabled' if running else 'normal')
        self.start_button.configure(state='disabled' if running else 'normal')
        self.stop_button.configure(state='normal' if running else 'disabled')
        self.open_button.configure(state='disabled' if running else 'normal')
        self.refresh_button.configure(state='disabled' if running else 'normal')
        self.ports.configure(state='disabled' if running else 'readonly')

    def reset_data(self):
        """Limpia la interfaz sin borrar los CSV ya guardados."""
        self.delta.set('— °C')
        self.mean.set('— °C')
        self.hz.set('— Hz')
        self.data.clear()
        self.tree.delete(*self.tree.get_children())
        self.temp.set('— °C')
        self.elapsed.set('— s')
        self.count.set('0 mediciones')
        self.export_button.configure(state='disabled')
        self.redraw()

    # 5. Inicio del experimento: validar objetivo, crear CSV y conectar.
    def start(self):
        """Crea una carpeta única por sesión, sin sobrescribir registros previos."""
        if self.ser is not None:
            return
        try:
            target = parse_target(self.target.get())
        except (ValueError, OverflowError):
            messagebox.showwarning('Temperatura objetivo', 'Introduce un número entre 0 y 100 °C (ejemplo: 30,5).')
            return
        port = self.port_map.get(self.port.get())
        if not port:
            messagebox.showwarning('Puerto', 'Conecta el Arduino, pulsa Actualizar y elige el puerto COM.')
            return
        # La fecha y microsegundos evitan colisiones entre experimentos.
        session = CARPETA_MEDICIONES / datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
        path = session / 'temperaturas.csv'
        connection = output = None
        try:
            connection = serial.Serial(port, VELOCIDAD, timeout=0)
            session.mkdir(parents=True, exist_ok=False)
            output = open(path, 'x', encoding='utf-8-sig', newline='')
            writer = csv.writer(output)
            writer.writerow(HEADER)
            output.flush()
        except (OSError, serial.SerialException) as e:
            if connection:
                connection.close()
            if output:
                output.close()
            messagebox.showerror('No se pudo iniciar', f'{e}\n\nCierra el monitor y el plotter serial de Arduino IDE.')
            return
        self.ser, self.out, self.writer = connection, output, writer
        self.path = Path(path)
        self.folder = self.path.parent
        self.buffer = b''
        self.first_time = self.last_raw = None
        self.active_target = target
        self.last_valid_at = time.monotonic()
        self.reset_data()
        self.alert.set(f'Objetivo: {target:.2f} °C. Esperando lecturas.')
        self.save_metadata('En curso')
        self.filename.set(f'Guardando: {self.path}')
        self.status.set('Conectado. Esperando la primera lectura del sensor…')
        self.set_running(True)

    # 6. Transformación de datos: tabla, indicadores y gráfico.
    def add_point(self, t, temp, update=True):
        """Añade una lectura a memoria y actualiza los indicadores visibles."""
        self.data.append((t, temp))
        item = self.tree.insert('', 'end', values=(f'{t:.3f}', f'{temp:.4f}'))
        self.tree.see(item)
        self.temp.set(f'{temp:.4f} °C')
        self.elapsed.set(f'{t:.3f} s')
        self.count.set(f'{len(self.data)} mediciones')
        if update:
            self.update_indicators()
        self.export_button.configure(state='normal')

    def update_indicators(self):
        """ΔT = T actual - T inicial; promedio aritmético; frecuencia observada."""
        delta, mean, hz = indicators(self.data)
        if delta is not None:
            self.delta.set(f'{delta:+.2f} °C')
            self.mean.set(f'{mean:.2f} °C')
            self.hz.set(f'{hz:.2f} Hz' if hz is not None else '— Hz')

    def redraw(self):
        """Actualiza la curva y el objetivo, ajustando automáticamente los ejes."""
        self.target_line.set_visible(self.active_target is not None)
        if self.active_target is not None:
            self.target_line.set_ydata([self.active_target, self.active_target])
        self.line.set_data([p[0] for p in self.data], [p[1] for p in self.data])
        self.ax.relim(visible_only=True)
        self.ax.autoscale_view()
        if not self.data:
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, max(40, (self.active_target or 0) + 2))
            self.ax.set_autoscale_on(True)
        self.canvas.draw_idle()

    # 7. Adquisición: leer puerto sin bloquear, validar y guardar cada dato.
    def poll(self):
        """El reloj de Arduino determina el tiempo real entre las muestras."""
        changed = False
        if self.ser is not None:
            try:
                # Una lectura USB puede incluir varias líneas o una línea incompleta.
                self.buffer += self.ser.read(min(self.ser.in_waiting, 65536))
                lines = self.buffer.split(b'\n')
                self.buffer = lines.pop()
                if len(self.buffer) > 4096:
                    self.buffer = b''
                for raw in lines:
                    line = raw.decode('ascii', errors='replace').strip()
                    if line.startswith('# ERROR'):
                        self.alert.set('Lectura inválida: revisa el sensor. No se guardó un dato falso.')
                        continue
                    point = parse_measurement(line)
                    if point is None:
                        if line and line != ','.join(HEADER):
                            self.alert.set('Lectura inválida recibida; se omitió.')
                        continue
                    t, temp = point
                    if self.last_raw is not None and t <= self.last_raw:
                        self.stop('El Arduino se reinició o su reloj retrocedió. Inicia un nuevo registro.')
                        break
                    # Se toma la primera lectura como t=0, no el encendido de Arduino.
                    if self.first_time is None:
                        self.first_time = t
                    self.last_raw = t
                    elapsed = t - self.first_time
                    # Primero guardamos el dato, incluso si es el que alcanza el límite.
                    self.writer.writerow((f'{elapsed:.3f}', f'{temp:.4f}'))
                    self.out.flush()  # Vacía el búfer de Python hacia el sistema operativo.
                    self.last_valid_at = time.monotonic()
                    self.add_point(elapsed, temp)
                    self.status.set('Registrando y guardando automáticamente…')
                    changed = True
                    # 8. Decisión operativa: alcanzar/superar el objetivo finaliza
                    # el registro. break descarta las lecturas pendientes posteriores.
                    if reached_target(temp, self.active_target):
                        reason = f'Objetivo alcanzado: {temp:.2f} °C ≥ {self.active_target:.2f} °C. Registro finalizado.'
                        self.stop(reason)
                        break
                    self.alert.set(f'Midiendo. Faltan {self.active_target - temp:.2f} °C para el objetivo.')
                # Si no llegan lecturas válidas, no mantener una sesión ciega.
                if self.ser is not None and time.monotonic() - self.last_valid_at >= TIEMPO_SIN_DATOS_S:
                    self.stop('Alerta: 5 s sin lecturas válidas. Registro interrumpido; revisa el sensor.')
            except (OSError, serial.SerialException, ValueError) as e:
                self.stop(f'Registro interrumpido: {e}')
        if changed:
            self.redraw()
        self.root.after(INTERVALO_GUI_MS, self.poll)

    # 9. Finalización y persistencia del resultado.
    def save_metadata(self, reason):
        """Guarda el objetivo y motivo de término aparte del CSV de dos columnas."""
        if self.path is None:
            return
        delta, mean, hz = indicators(self.data)
        metadata = {'temperatura_objetivo_C': self.active_target,
                    'motivo': reason, 'mediciones': len(self.data),
                    'delta_T_C': delta, 'promedio_C': mean, 'frecuencia_Hz': hz}
        try:
            self.path.with_name('metadatos.json').write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        except OSError as e:
            self.alert.set(f'No se pudo guardar metadatos: {e}')

    def stop(self, reason=None):
        """Cierra el puerto y el CSV; no envía órdenes a la fuente de plasma."""
        if self.ser is None:
            return
        errors = []
        for resource in (self.ser, self.out):
            if resource is not None:
                try:
                    resource.close()
                except (OSError, serial.SerialException) as e:
                    errors.append(str(e))
        self.ser = self.out = self.writer = None
        self.set_running(False)
        self.redraw()
        if self.path:
            self.filename.set(f'Archivo: {self.path}')
        if errors:
            result = 'Error al cerrar: ' + '; '.join(errors)
        else:
            result = reason or f'Registro detenido manualmente. {len(self.data)} mediciones guardadas.'
        self.status.set(result)
        self.alert.set(result)
        self.save_metadata(result)

    # 10. Reapertura, exportación y cierre de la aplicación.
    def open_file(self):
        """Reconstruye gráfico, tabla e indicadores sin necesitar el Arduino."""
        path = filedialog.askopenfilename(title='Abrir experimento guardado', initialdir=self.folder if self.folder.exists() else REPOSITORIO,
                                          filetypes=[('CSV', '*.csv'), ('Todos los archivos', '*.*')])
        if not path:
            return
        try:
            data = load_csv(path)
        except (OSError, ValueError, csv.Error) as e:
            messagebox.showerror('Error al abrir', str(e))
            return
        self.path = Path(path)
        self.folder = self.path.parent
        self.active_target = None
        self.target.set('')
        reason = 'Registro histórico (sin metadatos del objetivo).'
        try:
            if self.path.name != 'temperaturas.csv':
                raise ValueError('Formato histórico sin metadatos asociados.')
            metadata = json.loads(self.path.with_name('metadatos.json').read_text(encoding='utf-8'))
            value = metadata.get('temperatura_objetivo_C')
            if value is not None:
                self.active_target = parse_target(str(value))
                self.target.set(str(self.active_target))
            reason = str(metadata.get('motivo', 'Registro histórico.'))
        except (OSError, ValueError, TypeError, AttributeError):
            pass  # Los CSV de versiones anteriores no tienen metadatos.
        self.reset_data()
        for point in data:
            self.add_point(*point, update=False)
        self.update_indicators()
        self.redraw()
        self.filename.set(f'Archivo: {self.path}')
        self.alert.set(reason)
        self.status.set(f'Experimento recuperado. {len(data)} mediciones. No se necesita Arduino.')

    def export(self):
        """Exporta el gráfico de la sesión como PNG para usarlo en un informe."""
        path = filedialog.asksaveasfilename(title='Exportar gráfico', initialdir=self.folder,
                   initialfile=(self.path.stem if self.path else 'temperatura') + '.png',
                   defaultextension='.png', filetypes=[('Imagen PNG', '*.png')])
        if path:
            try:
                self.figure.savefig(path, dpi=200)
            except (OSError, ValueError) as e:
                messagebox.showerror('Error al exportar', str(e))
            else:
                self.status.set(f'Gráfico exportado: {path}')

    def close(self):
        """Si hay una sesión activa, guarda y cierra antes de salir."""
        if self.ser is not None:
            if not messagebox.askyesno('Cerrar', '¿Detener la medición y cerrar? Los datos registrados quedan guardados.'):
                return
            self.stop()
        self.root.destroy()


# 11. Punto de entrada: inicia la ventana solo al ejecutar este archivo.
if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()




