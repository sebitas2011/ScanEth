import time
import serial
import pandas as pd
import folium
import random
import json
import os
import glob
from datetime import datetime
from folium import Icon, Marker, Element

# Configuración
PUERTO_SERIAL = "COM4"
VELOCIDAD_BAUDIOS = 115200  
SIMULACION = False
TEMPLATE_HTML = "WEB_template.html"
HTML_FINAL = "WEB.html"

def conservar_ultimos_archivos(patron, cantidad=3):
    archivos = sorted(glob.glob(patron), key=os.path.getmtime, reverse=True)
    for archivo in archivos[cantidad:]:
        try:
            os.remove(archivo)
            print(f"🗑️ Eliminado: {archivo}")
        except Exception as e:
            print(f"⚠️ Error al eliminar {archivo}: {e}")

class ESP32Reader:
    def __init__(self, simulacion=False):
        self.simulacion = simulacion

    def obtener_datos(self):
        return self._datos_simulados() if self.simulacion else self._datos_reales()

    def _datos_reales(self):
        datos = []
        try:
            with serial.Serial(PUERTO_SERIAL, VELOCIDAD_BAUDIOS, timeout=5) as esp:
                print("📱 Conectado al ESP32...")
                while True:
                    linea = esp.readline().decode('utf-8', errors='ignore').strip()
                    if not linea:
                        continue
                    print(f"🧾 Línea: {linea}")
                    try:
                        data = json.loads(linea)
                        rssi = data.get("rssi", -100)
                        data["timestamp"] = datetime.now().isoformat()
                        data["calidad"] = self._clasificar_calidad(rssi)
                        data["color"] = self._asignar_color(rssi)
                        datos.append(data)
                        print(f"✅ Datos: {data}")
                    except json.JSONDecodeError:
                        continue
        except KeyboardInterrupt:
            print("🚫 Lectura interrumpida por el usuario.")
        except serial.SerialException as e:
            print(f"❌ Error de conexión: {e}")
        return datos

    def _datos_simulados(self):
        datos = []
        for _ in range(30):
            rssi = random.randint(-90, -30)
            calidad = self._clasificar_calidad(rssi)
            color = self._asignar_color(rssi)
            dato = {
                "ssid": "SimuladaNet",
                "rssi": rssi,
                "mac": "00:11:22:33:44:55",
                "lat": round(random.uniform(-12.019, -12.0135), 6),
                "lng": round(random.uniform(-77.052, -77.045), 6),
                "alt": round(random.uniform(100, 150), 2),
                "hdop": round(random.uniform(0.5, 2.5), 2),
                "sat": random.randint(5, 10),
                "calidad": calidad,
                "color": color,
                "timestamp": datetime.now().isoformat()
            }
            datos.append(dato)
            print(f"🧪 Simulado: {dato}")
            time.sleep(0.4)
        return datos

    def _clasificar_calidad(self, rssi):
        return "Buena" if rssi >= -69 else "Intermedia" if rssi >= -79 else "Mala"

    def _asignar_color(self, rssi):
        return "green" if rssi >= -69 else "orange" if rssi >= -79 else "red"

class DataSaver:
    def guardar_csv(self, datos, archivo):
        if not datos:
            print("⚠️ No hay datos para guardar.")
            return
        pd.DataFrame(datos).to_csv(archivo, index=False)
        print(f"📁 CSV guardado: {archivo}")

from folium.plugins import MarkerCluster

class WiFiMapper:
    def crear_mapa(self, datos, archivo):
        if not datos:
            print("⚠️ No hay datos para el mapa.")
            return

        df = pd.DataFrame(datos)
        mapa = folium.Map(
            location=[df["lat"].mean(), df["lng"].mean()],
            zoom_start=17,
            min_zoom=1,
            max_zoom=25,
            control_scale=True,
            prefer_canvas=True,
            zoom_control=True,
            max_bounds=False
        )

        folium.TileLayer("OpenStreetMap", name="Redes", control=True).add_to(mapa)

        # Crear clústers por categoría de calidad
        clusters = {
            "Buena": MarkerCluster(name="🟢 Buena"),
            "Intermedia": MarkerCluster(name="🟠 Intermedia"),
            "Mala": MarkerCluster(name="🔴 Mala")
        }

        cont = {"Buena": 0, "Intermedia": 0, "Mala": 0}
        for _, row in df.iterrows():
            calidad = row["calidad"]
            cont[calidad] += 1
            popup_html = f"""<b>📶 SSID:</b> {row['ssid']}<br>
            <b>RSSI:</b> {row['rssi']} dBm<br>
            <b>MAC:</b> {row['mac']}<br>
            <b>Satélites:</b> {row['sat']}<br>
            <b>Calidad:</b> {row['calidad']}<br>
            <b>🕒</b> {row['timestamp']}"""

            Marker(
                location=[row["lat"], row["lng"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=Icon(color=row["color"], icon="wifi", prefix="fa")
            ).add_to(clusters[calidad])

        # Añadir todos los clusters al mapa
        for cluster in clusters.values():
            cluster.add_to(mapa)

        folium.LayerControl(collapsed=False).add_to(mapa)

        leyenda = f"""
        <div style="position: fixed; bottom: 30px; left: 30px; z-index:9999;
        background: white; border: 2px solid #ccc; border-radius: 10px; padding: 10px">
        <b>📊 Calidad de señal</b><br>
        🟢 Buena: {cont['Buena']}<br>
        🟠 Intermedia: {cont['Intermedia']}<br>
        🔴 Mala: {cont['Mala']}<br>
        </div>"""
        mapa.get_root().html.add_child(Element(leyenda))
        

        mapa.save(archivo)
        print(f"🗘️ Mapa guardado: {archivo}")

def generar_html_final(csv_file, mapa_file, plantilla=TEMPLATE_HTML, salida=HTML_FINAL):
    if not os.path.exists(plantilla):
        print(f"❌ Plantilla no encontrada: {plantilla}")
        print("⛔ WEB.html NO se sobrescribió para evitar perder contenido anterior.")
        return

    with open(plantilla, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{CSV_FILENAME}}", csv_file)
    html = html.replace("{{MAPA_HTML}}", mapa_file)

    with open(salida, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML generado correctamente: {salida}")

if __name__ == "__main__":
    print("🚀 Iniciando escaneo Wi-Fi...")

    conservar_ultimos_archivos("datos_wifi_*.csv", cantidad=3)
    conservar_ultimos_archivos("mapa_wifi_*.html", cantidad=3)

    lector = ESP32Reader(simulacion=SIMULACION)
    datos = lector.obtener_datos()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_csv = f"datos_wifi_{timestamp}.csv"
    archivo_html = f"mapa_wifi_{timestamp}.html"

    DataSaver().guardar_csv(datos, archivo_csv)
    WiFiMapper().crear_mapa(datos, archivo_html)
    generar_html_final(archivo_csv, archivo_html)
    