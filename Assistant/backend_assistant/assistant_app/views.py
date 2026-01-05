# ==============================================================================
# 1. IMPORTS
# ==============================================================================
import os
import re
import json
import html
import subprocess
import webbrowser
import urllib.parse
import time
import datetime
import ctypes
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from youtubesearchpython import VideosSearch 

from .models import Usuario, Tarea, Conversacion, Mensaje
from .serializers import UsuarioSerializer, TareaSerializer, ConversacionSerializer, MensajeSerializer

# ==============================================================================
# 2. CONFIGURACIÓN GROQ
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
print(f"🔍 Buscando archivo .env en: {dotenv_path}")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print("✅ Archivo .env encontrado y cargado.")
else:
    print("⚠️ ADVERTENCIA: No encuentro el archivo .env en esa ruta.")

MI_CLAVE_GROQ = os.getenv("GROQ_API_KEY")

print("\n🚀 --- INICIANDO MOTOR GROQ (LLAMA 3) ---")
client = None

if not MI_CLAVE_GROQ:
    print("❌ ERROR CRÍTICO: No se encontró la variable GROQ_API_KEY.")
else:
    try:
        client = Groq(api_key=MI_CLAVE_GROQ)
        print("✅ Cliente Groq listo.")
    except Exception as e:
        print(f"❌ Error iniciando Groq: {e}")

MODELO_ID = "llama-3.3-70b-versatile"

# ==============================================================================
# 3. HERRAMIENTAS DEL SISTEMA
# ==============================================================================

PATH_BRAVE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
if not os.path.exists(PATH_BRAVE):
    PATH_BRAVE = os.path.join(os.path.expanduser("~"), r"AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")

PROCESOS_MAP = {
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "chrome": "chrome.exe",
    "brave": "brave.exe",
    "calculadora": ["CalculatorApp.exe", "calc.exe"],
    "bloc de notas": "notepad.exe",
}

try:
    import pygetwindow as gw
    import pyautogui
except ImportError:
    gw = None
    pyautogui = None

def tool_abrir_aplicacion(nombre_app):
    print(f"📂 Solicitud para abrir: {nombre_app}")
    
    apps = {
        # --- NAVEGADORES ---
        "chrome": {"ruta": r"C:\Program Files\Google\Chrome\Application\chrome.exe", "titulo": "Chrome"},
        "brave": {"ruta": PATH_BRAVE, "titulo": "Brave"},
        "edge": {"ruta": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "titulo": "Edge"},
        "firefox": {"ruta": r"C:\Program Files\Mozilla Firefox\firefox.exe", "titulo": "Firefox"},

        # --- HERRAMIENTAS DE WINDOWS ---
        "calculadora": {"ruta": "calc.exe", "titulo": "Calculadora"},
        "bloc de notas": {"ruta": "notepad.exe", "titulo": "Bloc de notas"},
        "paint": {"ruta": "mspaint.exe", "titulo": "Paint"},
        "explorador": {"ruta": "explorer.exe", "titulo": "Explorador de archivos"},
        "consola": {"ruta": "cmd.exe", "titulo": "Símbolo del sistema"},
        "panel de control": {"ruta": "control.exe", "titulo": "Panel de control"},

        # --- OFFICE ---
        "word": {"ruta": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE", "titulo": "Word"},
        "excel": {"ruta": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE", "titulo": "Excel"},
        "powerpoint": {"ruta": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE", "titulo": "PowerPoint"},

        # --- APPS DE USUARIO ---
        "spotify": {"ruta": os.path.join(os.path.expanduser("~"), r"AppData\Roaming\Spotify\Spotify.exe"), "titulo": "Spotify"},
        "discord": {"ruta": os.path.join(os.path.expanduser("~"), r"AppData\Local\Discord\Update.exe"), "titulo": "Discord"},
        "vscode": {"ruta": os.path.join(os.path.expanduser("~"), r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk"), "titulo": "Visual Studio Code"},
        "whatsapp": {"ruta": os.path.join(os.path.expanduser("~"), r"AppData\Local\WhatsApp\WhatsApp.exe"), "titulo": "WhatsApp"},
    }
    
    nombre_clave = nombre_app.lower().strip()
    app_info = apps.get(nombre_clave)
    
    if app_info:
        ruta = app_info["ruta"]
        titulo_ventana = app_info["titulo"]
        
        try:
            print(f"🚀 Lanzando: {ruta}")
            os.startfile(ruta)
            
            ventana_encontrada = None
            for i in range(10): 
                print(f"🔎 Buscando ventana '{titulo_ventana}' (Intento {i+1}/10)...")
                if gw:
                    ventanas = gw.getWindowsWithTitle(titulo_ventana)
                    if ventanas:
                        candidata = ventanas[0]
                        if candidata.height > 0:
                            ventana_encontrada = candidata
                            break
                time.sleep(1)
            
            if ventana_encontrada and pyautogui:
                print(f"✅ Ventana detectada: {ventana_encontrada.title}")
                if not ventana_encontrada.isMaximized:
                    ventana_encontrada.maximize()
                else:
                    ventana_encontrada.restore()
                try:
                    ventana_encontrada.activate()
                except:
                    pass
                
                click_x = ventana_encontrada.left + 50
                click_y = ventana_encontrada.top + 200 
                pyautogui.click(click_x, click_y)
                
                return f"{nombre_app} está lista en tu pantalla"
            else:
                return f"Abrí {nombre_app}, pero tardó mucho en cargar y perdí el rastro"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return f"Error abriendo {nombre_app}: {e}"
    else:
        return f"No tengo configurada la ruta para {nombre_app}"

def tool_detectar_apps(dummy):
    try:
        tasks = subprocess.check_output('tasklist', shell=True).decode('latin-1', 'ignore').lower()
        abiertas = []
        for nombre, exes in PROCESOS_MAP.items():
            lista = exes if isinstance(exes, list) else [exes]
            for x in lista:
                if x.lower() in tasks and nombre not in abiertas:
                    abiertas.append(nombre)
        return f"Abierto: {', '.join(abiertas)}." if abiertas else "Nada importante abierto"
    except: return "Error leyendo procesos"

def tool_cerrar_aplicacion(nombre_objetivo):
    nombre_objetivo = nombre_objetivo.lower()
    try:
        tasks = subprocess.check_output('tasklist', shell=True).decode('latin-1', 'ignore').lower()
        if "todo" in nombre_objetivo:
            c = 0
            for _, exes in PROCESOS_MAP.items():
                lista = exes if isinstance(exes, list) else [exes]
                for x in lista:
                    if x.lower() in tasks:
                        subprocess.run(f"taskkill /IM {x} /F", shell=True)
                        c += 1
            return f"Cerré {c} aplicaciones."

        encontrado = False
        for nombre, exes in PROCESOS_MAP.items():
            if nombre in nombre_objetivo:
                lista = exes if isinstance(exes, list) else [exes]
                for x in lista:
                    subprocess.run(f"taskkill /IM {x} /F", shell=True)
                encontrado = True
        return f"Cerrando {nombre_objetivo}." if encontrado else f"No sé cerrar {nombre_objetivo}."
    except: return "Error cerrando."

def tool_reproducir_musica(busqueda):
    print(f"🎵 Buscando video: '{busqueda}'")
    try:
        query_string = urllib.parse.quote(busqueda)
        url_busqueda = f"https://www.youtube.com/results?search_query={query_string}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url_busqueda, headers=headers)
        response_data = urllib.request.urlopen(req).read().decode()
        
        video_ids = re.findall(r"watch\?v=(\S{11})", response_data)
        titulos = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', response_data)

        if video_ids:
            video_id = video_ids[0]
            url_final = f"https://www.youtube.com/watch?v={video_id}"
            if titulos:
                titulo_a_leer = html.unescape(titulos[0])
            else:
                titulo_a_leer = f"Video de {busqueda}"
        else:
            url_final = url_busqueda
            titulo_a_leer = f"Resultados para {busqueda}"

        if os.path.exists(PATH_BRAVE):
            subprocess.Popen([PATH_BRAVE, url_final])
        else:
            webbrowser.open(url_final)
            
        return f"Reproduciendo: {titulo_a_leer}"
        
    except Exception as e:
        print(f"❌ Error scraping: {e}")
        return f"Error abriendo YouTube: {e}"

def tool_buscar_google(busqueda):
    print(f"🌐 Googleando: '{busqueda}'")
    try:
        query_string = urllib.parse.quote(busqueda)
        url_busqueda = f"https://www.google.com/search?q={query_string}"
        
        if os.path.exists(PATH_BRAVE):
            subprocess.Popen([PATH_BRAVE, url_busqueda])
        else:
            webbrowser.open(url_busqueda)
            
        return f"Aquí tienes los resultados de: {busqueda}"
    except Exception as e:
        return f"Error al buscar en Google: {e}"

def tool_hora_fecha(dummy):
    now = datetime.datetime.now()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    
    dia_str = dias[now.weekday()]
    mes_str = meses[now.month - 1]
    hora_str = now.strftime("%I:%M %p")
    
    return f"Hoy es {dia_str} {now.day} de {mes_str} y son las {hora_str}."

def tool_bloquear_pantalla(dummy):
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Pantalla bloqueada."
    except:
        return "No pude bloquear la pantalla."

# ==============================================================================
# 4. ENDPOINTS API
# ==============================================================================

# --- A. CONTROL DEL SISTEMA  ---
@api_view(['POST'])
def lenguaje_natural(request):
    print(f"\n🎧 OS COMMAND: {request.data}")
    mensaje = request.data.get('mensaje', '')
    if not mensaje: return Response({'message': 'Silencio.'})
    if not client: return Response({'message': 'Error cliente Groq.'}, status=500)

    try:
        # Prompt actualizado
        system_prompt = """
        Eres un asistente de sistema operativo. Identifica la intención y devuelve JSON.
        HERRAMIENTAS:
        1. abrir -> { "intencion": "abrir", "parametro": "nombre_app" }
        2. cerrar -> { "intencion": "cerrar", "parametro": "nombre_app" }
        3. detectar -> { "intencion": "detectar", "parametro": "null" }
        4. musica -> { "intencion": "musica", "parametro": "busqueda" } (Si menciona 'reproducir', 'video', 'canción', 'youtube')
        5. buscar -> { "intencion": "buscar", "parametro": "busqueda" } (Si dice 'busca', 'googlea', 'investiga', 'quién es', 'qué es')
        6. hora -> { "intencion": "hora", "parametro": "null" } (Si pregunta 'qué hora es', 'fecha')
        7. bloquear -> { "intencion": "bloquear", "parametro": "null" } (Si dice 'bloquea pantalla', 'cerrar sesión')
        8. chat -> { "intencion": "chat", "parametro": "respuesta breve" }
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje}
            ],
            model=MODELO_ID,
            temperature=0,
            response_format={"type": "json_object"}
        )

        data = json.loads(chat_completion.choices[0].message.content)
        i, p = data.get('intencion'), data.get('parametro')
        
        print(f"🤖 Acción: {i} -> {p}")

        if i == 'abrir': res = tool_abrir_aplicacion(p)
        elif i == 'cerrar': res = tool_cerrar_aplicacion(p)
        elif i == 'detectar': res = tool_detectar_apps(None)
        elif i == 'musica': res = tool_reproducir_musica(p)
        elif i == 'buscar': res = tool_buscar_google(p)
        elif i == 'hora': res = tool_hora_fecha(None)
        elif i == 'bloquear': res = tool_bloquear_pantalla(None)
        else: res = p 

        return Response({'message': res})

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return Response({'message': f'Error: {str(e)}'}, status=500)

# --- B. GESTIÓN DE HISTORIAL ---
@api_view(['GET'])
def listar_conversaciones(request):
    chats = Conversacion.objects.all().order_by('-fecha_creacion')
    serializer = ConversacionSerializer(chats, many=True)
    return Response(serializer.data)

@api_view(['GET', 'DELETE'])
def obtener_detalle_conversacion(request, chat_id):
    try:
        chat = Conversacion.objects.get(id=chat_id)
    except Conversacion.DoesNotExist:
        return Response({'error': 'Chat no encontrado'}, status=404)

    if request.method == 'GET':
        mensajes = chat.mensajes.all().order_by('fecha')
        serializer = MensajeSerializer(mensajes, many=True)
        return Response({'id': chat.id, 'titulo': chat.titulo, 'mensajes': serializer.data})
    
    elif request.method == 'DELETE':
        chat.delete()
        return Response({'message': 'Eliminado'}, status=200)

# --- C. ASISTENTE PSICOLÓGICO HÍBRIDO ---
@api_view(['POST'])
def assistant_psycology(request):
    user_message = request.data.get('mensaje', '')
    chat_id = request.data.get('chat_id', None)
    
    if not client: return Response({'response': "Error IA"}, status=500)

    if chat_id:
        try: conversacion = Conversacion.objects.get(id=chat_id)
        except: conversacion = Conversacion.objects.create(titulo="Nueva Conversación")
    else:
        titulo = ' '.join(user_message.split()[:5]) + "..."
        conversacion = Conversacion.objects.create(titulo=titulo)
    
    chat_id = conversacion.id
    Mensaje.objects.create(conversacion=conversacion, remitente='usuario', texto=user_message)

    keywords_humor = ['chiste', 'broma', 'reír', 'gracioso', 'ánimo']
    wants_joke = any(word in user_message.lower() for word in keywords_humor)

    system_content = """
    Eres un Asistente Virtual Híbrido. 
    MODO PSICÓLOGO (Default): Empático, valida emociones, sé breve (máx 40 palabras).
    MODO COMEDIANTE (Si piden chiste/ánimo): Cuenta un chiste directo.
    """
    if wants_joke: system_content += " MODO COMEDIANTE ACTIVO."

    try:
        historial = conversacion.mensajes.order_by('-fecha')[:6]
        msgs = [{"role": "system", "content": system_content}]
        for m in reversed(historial):
            msgs.append({"role": "user" if m.remitente == 'usuario' else "assistant", "content": m.texto})

        chat = client.chat.completions.create(
            messages=msgs,
            model=MODELO_ID,
            temperature=0.7,
            max_tokens=200,
        )
        response_text = chat.choices[0].message.content
        Mensaje.objects.create(conversacion=conversacion, remitente='ia', texto=response_text)

        return Response({'response': response_text, 'chat_id': chat_id, 'titulo': conversacion.titulo})

    except Exception as e:
        return Response({'response': "Error procesando."}, status=500)

# --- D. VISTAS ESTÁNDAR ---
@api_view(['GET'])
def api_overview(request): return JsonResponse({"status": "OK"})
@api_view(['POST', 'GET'])
def usuario_tarea(request): return JsonResponse({'msg': 'OK'})

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer