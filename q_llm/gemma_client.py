import requests
import json
import threading

def ask_gemma_stream(prompt, callback):
    def _worker():
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "gemma3:4b",
            "prompt": prompt,
            "stream": True
        }

        try:
            with requests.post(url, json=payload, stream=True, timeout=60) as response:
                buffer = b""
                for chunk in response.iter_content(chunk_size=512):
                    if not chunk:
                        continue
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line.decode("utf-8"))
                            text = data.get("response", "")
                            if text:
                                callback(text)
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            # Translated error message
            callback(f"[Connection error] {e}")

    # Start the worker in a background thread
    threading.Thread(target=_worker, daemon=True).start()

def extract_location(prompt: str, log=print) -> str:
    system_prompt = (
        "The user provided a place name to move the map. "
        "Please extract only the place name as a single word. "
        "Example: 'Take me to Seoul' → 'Seoul'"
    )
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\nPlace name:"

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "gemma3:4b",
            "prompt": full_prompt,
            "stream": False
        }).json()

        location = response["response"].strip().split()[0]
        log(f"[📍 Extracted location]: {location}")
        return location
    except Exception as e:
        log(f"[❌ Failed to extract location]: {e}")
        return ""


def get_coordinates_from_osm(location_name: str, log=print):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "QGISGemmaMapper/1.0"}

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if not data:
            log("[❌ Location not found]")
            return None

        lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        log(f"[🌍 Coordinates]: {location_name} → Latitude: {lat}, Longitude: {lon}")
        return lat, lon
    except Exception as e:
        log(f"[❌ Failed to retrieve coordinates]: {e}")
        return None

from qgis.core import QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.utils import iface

def move_canvas_to(lat: float, lon: float, log=print):
    canvas = iface.mapCanvas()
    crs_src = QgsCoordinateReferenceSystem("EPSG:4326")
    crs_dest = canvas.mapSettings().destinationCrs()
    xform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())

    point = xform.transform(QgsPointXY(lon, lat))
    canvas.setCenter(point)
    canvas.refresh()        
    log(f"[🗺️ Map moved] Centered on: Longitude {lon}, Latitude {lat}")
    log("[✅ Done]")

def go_to_location(prompt: str, log=print):
    location = extract_location(prompt, log=log)
    if not location:
        log("[❌ No valid location extracted]")
        return

    coords = get_coordinates_from_osm(location, log=log)
    if coords:
        move_canvas_to(*coords, log=log)
