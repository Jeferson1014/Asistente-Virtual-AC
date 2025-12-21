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
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from youtubesearchpython import VideosSearch

from .models import Usuario, Tarea
from .serializers import UsuarioSerializer, TareaSerializer

# ==============================================================================
# 2. CONFIGURACIÓN GROQ (PLAN B)
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
print(f"🔍 Buscando archivo .env en: {dotenv_path}")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print("✅ Archivo .env encontrado y cargado.")
else:
    print("⚠️ ADVERTENCIA: No encuentro el archivo .env en esa ruta.")

# 🔴 PEGA AQUÍ TU CLAVE DE GROQ (Empieza por 'gsk_')
MI_CLAVE_GROQ = os.getenv("GROQ_API_KEY")

load_dotenv()

print("\n🚀 --- INICIANDO MOTOR GROQ (LLAMA 3) ---")
client = None

if not MI_CLAVE_GROQ:
    print("❌ ERROR CRÍTICO: No se encontró la variable GROQ_API_KEY.")
    print("   -> Asegúrate de haber creado el archivo .env")
    print("   -> Copia el contenido de .env.example y pide la clave al admin.")
else:
    try:
        client = Groq(api_key=MI_CLAVE_GROQ)
        print("✅ Cliente Groq listo.")
    except Exception as e:
        print(f"❌ Error iniciando Groq: {e}")

# Usamos Llama 3.3 (La más inteligente y rápida actualmente)
MODELO_ID = "llama-3.3-70b-versatile"

# ==============================================================================
# 3. HERRAMIENTAS DEL SISTEMA
# ==============================================================================

PATH_BRAVE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
if not os.path.exists(PATH_BRAVE):
    PATH_BRAVE = os.path.join(os.path.expanduser("~"), r"AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")

APLICACIONES_RUTAS = {
    "word": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk",
    "excel": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk",
    "powerpoint": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "brave": PATH_BRAVE,
    "calculadora": "calc.exe",
    "bloc de notas": "notepad.exe",
}

PROCESOS_MAP = {
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "chrome": "chrome.exe",
    "brave": "brave.exe",
    "calculadora": ["CalculatorApp.exe", "calc.exe"],
    "bloc de notas": "notepad.exe",
}

def tool_abrir_aplicacion(nombre_app):
    print(f"📂 Abrir: {nombre_app}")
    path = APLICACIONES_RUTAS.get(nombre_app.lower())
    if path and os.path.exists(path):
        subprocess.Popen(f'"{path}"', shell=True)
        return f"Abriendo {nombre_app}..."
    
    cmds = {"calculadora": "calc", "bloc": "notepad", "navegador": "start chrome", "word": "start winword"}
    for k, v in cmds.items():
        if k in nombre_app.lower():
            subprocess.Popen(v, shell=True)
            return f"Ejecutando {k}..."
    return f"No encontré {nombre_app}."

def tool_detectar_apps(dummy):
    try:
        tasks = subprocess.check_output('tasklist', shell=True).decode('latin-1', 'ignore').lower()
        abiertas = []
        for nombre, exes in PROCESOS_MAP.items():
            lista = exes if isinstance(exes, list) else [exes]
            for x in lista:
                if x.lower() in tasks and nombre not in abiertas:
                    abiertas.append(nombre)
        return f"Abierto: {', '.join(abiertas)}." if abiertas else "Nada importante abierto."
    except: return "Error leyendo procesos."

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
    print(f"🎵 Buscando video y TÍTULO REAL para: '{busqueda}'")
    
    url_final = ""
    # Por defecto usamos la búsqueda, por si falla el título
    titulo_a_leer = f"Resultados de {busqueda}" 

    try:
        # 1. Preparar búsqueda
        query_string = urllib.parse.quote(busqueda)
        url_busqueda = f"https://www.youtube.com/results?search_query={query_string}"
        
        # 2. Descargar código HTML de YouTube (fingiendo ser un humano)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url_busqueda, headers=headers)
        response_data = urllib.request.urlopen(req).read().decode()
        
        # 3. EXTRAER ID DEL VIDEO (Regex)
        video_ids = re.findall(r"watch\?v=(\S{11})", response_data)
        
        # 4. EXTRAER TÍTULO REAL (Regex Avanzado)
        # Buscamos el patrón JSON donde YouTube guarda el título del primer resultado
        # El patrón suele ser: "title":{"runs":[{"text":"TITULO DEL VIDEO"}]}
        titulos = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', response_data)

        if video_ids:
            video_id = video_ids[0]
            url_final = f"https://www.youtube.com/watch?v={video_id}"
            
            # Intentamos sacar el título, si existe
            if titulos:
                # El primer título suele corresponder al primer video
                titulo_crudo = titulos[0]
                # Limpiamos caracteres raros (ej: convierte &amp; en &)
                titulo_a_leer = html.unescape(titulo_crudo)
                print(f"✅ Título detectado: {titulo_a_leer}")
            else:
                titulo_a_leer = f"Video de {busqueda}"
                
        else:
            print("⚠️ No encontré ID, abriendo búsqueda general.")
            url_final = url_busqueda

    except Exception as e:
        print(f"❌ Error scraping: {e}")
        url_final = f"https://www.youtube.com/results?search_query={urllib.parse.quote(busqueda)}"

    # 5. Ejecutar Navegador
    try:
        if os.path.exists(PATH_BRAVE):
            subprocess.Popen([PATH_BRAVE, url_final])
        else:
            webbrowser.open(url_final)
            
        # ESTE ES EL TEXTO QUE LEERÁ TU ASISTENTE EN VOZ ALTA
        return f"Reproduciendo: {titulo_a_leer}"
        
    except Exception as e:
        return f"Error abriendo navegador: {e}"
    
# ==============================================================================
# 4. ENDPOINTS API
# ==============================================================================

@api_view(['POST'])
def lenguaje_natural(request):
    print(f"\n🎧 MSG: {request.data}")
    mensaje = request.data.get('mensaje', '')
    if not mensaje: return Response({'message': 'Silencio.'})
    
    if not client: return Response({'message': 'Error cliente Groq.'}, status=500)

    try:
        # Prompt del Sistema
        system_prompt = """
        Eres un asistente de sistema operativo. Tu trabajo es identificar la intención del usuario y devolver UNICAMENTE un objeto JSON.
        
        TUS HERRAMIENTAS:
        1. Si pide abrir algo -> { "intencion": "abrir", "parametro": "nombre_app" }
           (Soporta: word, excel, powerpoint, chrome, brave, calculadora, bloc de notas)
        2. Si pide cerrar algo -> { "intencion": "cerrar", "parametro": "nombre_app o todo" }
        3. Si pregunta qué hay abierto -> { "intencion": "detectar", "parametro": "null" }
        4. Si pide música/video -> { "intencion": "musica", "parametro": "términos de busqueda" }
        5. Cualquier otra cosa (charla, preguntas) -> { "intencion": "chat", "parametro": "tu respuesta breve y amable" }
        """

        # LLAMADA A GROQ
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje}
            ],
            model=MODELO_ID,
            temperature=0, # Cero creatividad = Máxima precisión
            response_format={"type": "json_object"} # FORZAMOS JSON PURO
        )

        # Procesar respuesta
        respuesta_raw = chat_completion.choices[0].message.content
        print(f"⚡ GROQ: {respuesta_raw}")
        
        data = json.loads(respuesta_raw)
        i, p = data.get('intencion'), data.get('parametro')
        
        # Ejecutar herramienta
        if i == 'abrir': res = tool_abrir_aplicacion(p)
        elif i == 'cerrar': res = tool_cerrar_aplicacion(p)
        elif i == 'detectar': res = tool_detectar_apps(None)
        elif i == 'musica': res = tool_reproducir_musica(p)
        else: res = p # Caso chat

        return Response({'message': res})

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return Response({'message': f'Error: {str(e)}'}, status=500)

@api_view(['POST'])
def assistant_psycology(request):
    print(f"\n🧠 CONSULTA PSI: {request.data}")
    mensaje = request.data.get('mensaje', '')
    
    # Si el usuario no dice nada, saludamos
    if not mensaje: 
        return Response({'message': 'Hola. Estoy aquí para escucharte. ¿Cómo te sientes hoy?'})
    
    if not client: 
        return Response({'message': 'Error: El cerebro de la IA no está conectado.'}, status=500)

    try:
        # --- PERSONALIDAD DEL PSICÓLOGO ---
        system_prompt = """
        Eres un asistente de apoyo emocional empático, cálido y profesional basado en Terapia Cognitivo-Conductual (TCC).
        
        TUS REGLAS:
        1. Valida siempre los sentimientos del usuario (ej: "Entiendo que te sientas así...").
        2. No des diagnósticos médicos.
        3. Haz preguntas abiertas que inviten a la reflexión.
        4. Sé conciso pero amable (máximo 3 o 4 oraciones).
        5. Si el usuario menciona suicidio o autolesiones, responde ÚNICAMENTE sugiriendo llamar a emergencias o líneas de ayuda locales con urgencia.
        """

        # --- LLAMADA A GROQ (MODO TEXTO, NO JSON) ---
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje}
            ],
            model="llama-3.3-70b-versatile", # Usamos el modelo grande para mejor razonamiento
            temperature=0.6, # Un poco de creatividad para que suene humano
        )

        respuesta_ia = chat_completion.choices[0].message.content
        print(f"🧠 RESPUESTA: {respuesta_ia}")

        return Response({'message': respuesta_ia})

    except Exception as e:
        print(f"❌ ERROR PSI: {e}")
        return Response({'message': 'Lo siento, estoy teniendo problemas para procesar eso ahora mismo.'}, status=500)
@api_view(['GET'])
def api_overview(request): return JsonResponse({"status": "OK"})

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer
@api_view(['POST', 'GET'])
def usuario_tarea(request): return JsonResponse({'msg': 'OK'})