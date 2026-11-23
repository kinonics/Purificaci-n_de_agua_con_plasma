"""Dashboard de temperatura del agua (DS18B20).

Arduino transmite DATA,milisegundos,temperatura,rele a 4 Hz nominales.
Este programa valida, visualiza y guarda cada lectura, y finaliza el registro
cuando la temperatura cruza el objetivo en la direccion de la medicion.
Controla SOLAMENTE el relé de prueba de banco mediante comandos I/P/H/T:.
Si la temperatura inicial es mayor que el objetivo, mide ENFRIAMIENTO
con el rele apagado; si es menor, mide CALENTAMIENTO con el rele encendido.

Ejecutar: python registro_temperatura_v2.py
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
VELOCIDAD = 115200
INTERVALO_GUI_MS = 100  # Consulta del puerto; NO es la frecuencia del sensor.
TIEMPO_SIN_DATOS_S = 8  # Alerta de pérdida de lecturas válidas.
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


def reached_target(temp, target, mode):
    """Se detiene al cruzar la meta en la direccion adecuada.

    Enfriamiento: temperatura <= meta. Calentamiento: temperatura >= meta.
    """
    if target is None:
        return False
    if mode == 'CALENTAMIENTO':
        return temp >= target
    if mode == 'ENFRIAMIENTO':
        return temp <= target
    return False


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
    """Extrae DATA,ms,temp_C,rele del nuevo Arduino; devuelve (seg,°C,0/1)."""
    try:
        label, ms, value, state = line.strip().split(',')
        if label != 'DATA' or state not in ('0', '1'):
            return None
        t, temp = float(ms) / 1000.0, float(value)
        if not (math.isfinite(t) and math.isfinite(temp) and t >= 0
                and -55 <= temp <= 125):
            return None
        return t, temp, int(state)
    except (ValueError, TypeError):
        return None


def parse_saved_measurement(row):
    """CSV histórico y actual usan 2 columnas: tiempo_s,temperatura_C."""
    if len(row) != 2:
        return None
    try:
        t, temp = float(row[0]), float(row[1])
    except (ValueError, TypeError):
        return None
    if not (math.isfinite(t) and math.isfinite(temp)
            and t >= 0 and -55 <= temp <= 125):
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
            point = parse_saved_measurement(row)
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
        self.configured = False  # Objetivo confirmado por el Arduino.
        self.start_sent = False
        self.started = False  # Confirmación de SESION iniciada (también en enfriamiento).
        self.mode = None  # CALENTAMIENTO o ENFRIAMIENTO, confirmado por Arduino.
        self.last_config_at = 0
        self.sent_start_at = 0
        self.last_heartbeat_at = 0
        self.pending_stop_reason = None
        self.relay_status = tk.StringVar(value='APAGADO')
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
        ttk.Label(target_bar, text='Meta mayor: calentamiento (relé activo). Meta menor: enfriamiento (relé apagado).').pack(side='left')
        ttk.Label(outer, textvariable=self.alert, foreground='#9C4100', wraplength=900).pack(anchor='w')

        # 4.3. Indicadores derivados de cada nueva medición.
        metrics = ttk.Frame(outer)
        metrics.pack(fill='x', pady=(6, 12))
        for col, (caption, variable) in enumerate([('Temperatura', self.temp), ('Tiempo (desde inicio)', self.elapsed), ('Registro', self.count), ('ΔT', self.delta), ('Promedio', self.mean), ('Frecuencia real', self.hz), ('Relé de prueba', self.relay_status)]):
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
        self.relay_status.set('APAGADO')
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
        self.configured = False
        self.start_sent = False
        self.started = False
        self.mode = None
        self.last_config_at = 0
        self.sent_start_at = 0
        self.last_heartbeat_at = 0
        self.pending_stop_reason = None
        self.reset_data()
        self.alert.set(f'Objetivo: {target:.2f} °C. Esperando lecturas.')
        self.save_metadata('En curso')
        self.filename.set(f'Guardando: {self.path}')
        self.status.set('Conectado. Sin generador. Detectando calentamiento o enfriamiento…')
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
    def send_command(self, command):
        """Envía órdenes delimitadas por salto de línea para el sketch de pruebas."""
        if self.ser is None:
            return False
        self.ser.write((command + '\n').encode('ascii'))
        self.ser.flush()
        return True

    # 7. Leer Arduino, negociar objetivo y mantener el latido de la prueba.
    def poll(self):
        """La GUI es solo una interfaz de pruebas; Arduino decide el apagado."""
        changed = False
        if self.ser is not None:
            try:
                now = time.monotonic()
                # Reenviar objetivo hasta obtener la confirmación del Arduino.
                # Útil si abrir el puerto reinicia el Leonardo.
                if not self.configured and now - self.last_config_at >= 1.0:
                    self.send_command('P')
                    self.send_command(f'T:{self.active_target:.3f}')
                    self.last_config_at = now

                # Con el relé de prueba activo enviamos latidos cada 0,5 s.
                # Arduino desactiva D7 si no los recibe durante 1,5 s.
                if self.started and now - self.last_heartbeat_at >= 0.5:
                    self.send_command('H')
                    self.last_heartbeat_at = now

                self.buffer += self.ser.read(min(self.ser.in_waiting, 65536))
                lines = self.buffer.split(b'\n')
                self.buffer = lines.pop()
                if len(self.buffer) > 4096:
                    self.buffer = b''

                for raw in lines:
                    line = raw.decode('ascii', errors='replace').strip()
                    if not line:
                        continue
                    if line.startswith('# OBJETIVO,'):
                        try:
                            acknowledged = float(line.split(',', 1)[1])
                        except ValueError:
                            self.stop('Objetivo no confirmado por Arduino.')
                            break
                        if abs(acknowledged - self.active_target) > 0.01:
                            self.stop('Objetivo devuelto por Arduino no coincide.')
                            break
                        self.configured = True
                        self.status.set('Objetivo confirmado. Esperando medición válida…')
                        continue
                    if line.startswith('# INICIADO,'):
                        # El Arduino decide el modo con la ultima lectura real.
                        mode = line.split(',', 1)[1]
                        if mode not in ('CALENTAMIENTO', 'ENFRIAMIENTO'):
                            self.stop('Modo de medición desconocido.')
                            break
                        self.mode = mode
                        self.started = True
                        self.relay_status.set('ENCENDIDO (PRUEBA)' if mode == 'CALENTAMIENTO'
                                              else 'APAGADO (ENFRIAMIENTO)')
                        self.status.set(f'Sesión de {mode.lower()} activa. Guardando CSV y gráfico…')
                        self.last_heartbeat_at = 0
                        continue
                    if line.startswith('# FINALIZADO,'):
                        # Arduino comunica fin ANTES del dato final; esperamos muestra.
                        self.relay_status.set('APAGADO')
                        self.pending_stop_reason = 'Arduino finalizó la sesión: ' + line.split(',', 1)[1]
                        continue
                    if line.startswith('# ERROR_SENSOR') or line.startswith('# INICIO_DENEGADO'):
                        self.stop('Arduino informó: ' + line)
                        break
                    if line.startswith('# ERROR,'):
                        self.stop('Arduino informó: ' + line)
                        break
                    if line.startswith('#'):
                        continue  # Mensajes de estado, no son mediciones.

                    point = parse_measurement(line)
                    if point is None:
                        continue
                    t, temp, active_flag = point
                    self.last_valid_at = time.monotonic()
                    self.temp.set(f'{temp:.3f} °C')

                    # Al tener objetivo confirmado Y lectura reciente, iniciar.
                    if self.configured and not self.start_sent:
                        if abs(temp - self.active_target) < 0.0001:
                            self.stop('La temperatura ya es igual al objetivo. Elige otro objetivo.')
                            break
                        self.send_command('I')
                        self.start_sent = True
                        self.sent_start_at = time.monotonic()
                        self.status.set('Solicitud de inicio enviada al Arduino…')
                        continue

                    # No registrar hasta recibir # INICIADO.
                    if not self.started:
                        continue
                    if self.last_raw is not None and t <= self.last_raw:
                        self.stop('El Arduino se reinició o su reloj retrocedió.')
                        break
                    if self.first_time is None:
                        self.first_time = t
                    self.last_raw = t
                    elapsed = t - self.first_time
                    self.writer.writerow((f'{elapsed:.3f}', f'{temp:.4f}'))
                    self.out.flush()
                    self.add_point(elapsed, temp)
                    self.relay_status.set('ENCENDIDO (PRUEBA)' if active_flag
                                          else ('APAGADO (ENFRIAMIENTO)' if self.mode == 'ENFRIAMIENTO'
                                                else 'APAGADO'))
                    changed = True
                    # En ENFRIAMIENTO el rele apagado es lo CORRECTO.
                    if self.pending_stop_reason:
                        self.stop(self.pending_stop_reason)
                        break
                    if self.mode == 'CALENTAMIENTO' and active_flag == 0:
                        self.stop('El relé se desactivó durante el calentamiento.')
                        break
                    if self.mode == 'ENFRIAMIENTO' and active_flag == 1:
                        self.stop('Estado inesperado: relé activo en enfriamiento.')
                        break
                    if reached_target(temp, self.active_target, self.mode):
                        self.stop(f'Objetivo alcanzado: {temp:.2f} °C. Medición finalizada.')
                        break
                    diferencia = abs(self.active_target - temp)
                    self.alert.set(f'{self.mode.capitalize()}: faltan {diferencia:.2f} °C para el objetivo.')

                if self.ser is not None:
                    now = time.monotonic()
                    if self.start_sent and not self.started and now - self.sent_start_at >= 2.5:
                        self.stop('Arduino no confirmó el inicio; prueba cancelada.')
                    elif self.pending_stop_reason and now - self.last_valid_at >= 1.0:
                        self.stop(self.pending_stop_reason)
                    elif now - self.last_valid_at >= TIEMPO_SIN_DATOS_S:
                        self.stop('Sin datos válidos. Prueba cancelada y relé apagado.')
            except (OSError, serial.SerialException, ValueError) as e:
                self.stop(f'Comunicación interrumpida: {e}')
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
                    'modo': self.mode,
                    'duracion_s': self.data[-1][0] if self.data else None,
                    'tiempo_hasta_objetivo_s': (self.data[-1][0] if self.data and
                        ('OBJETIVO_ALCANZADO' in reason or 'Objetivo alcanzado' in reason)
                        else None),
                    'motivo': reason, 'mediciones': len(self.data),
                    'delta_T_C': delta, 'promedio_C': mean, 'frecuencia_Hz': hz}
        try:
            self.path.with_name('metadatos.json').write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        except OSError as e:
            self.alert.set(f'No se pudo guardar metadatos: {e}')

    def stop(self, reason=None):
        """Solicita apagar el relé de prueba y cierra el CSV y el puerto."""
        if self.ser is None:
            return
        errors = []
        # IMPORTANTE: enviar P ANTES de cerrar el puerto (si sigue abierto).
        try:
            self.send_command('P')
        except (OSError, serial.SerialException) as e:
            errors.append('No pudo enviarse P: ' + str(e))
        self.relay_status.set('APAGADO (ORDEN ENVIADA)')
        self.started = False
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
        self.mode = None
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
            self.mode = metadata.get('modo')
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
        self.status.set(f'Experimento recuperado ({self.mode or "modo no guardado"}). {len(data)} mediciones. No se necesita Arduino.')

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
