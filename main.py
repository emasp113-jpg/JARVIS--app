# ============================================================
# J.A.R.V.I.S. - Versión App (GUI + Voz)
# ============================================================

import urllib.request
import json
import os
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Librerías de voz
try:
    import speech_recognition as sr
    from gTTS import gTTS
    import pygame
    VOZ_OK = True
except:
    VOZ_OK = False

# ---------- CONFIGURACIÓN ----------
API_KEY = "AQ.Ab8RN6LdklC_HI9tBOWJi3lc9sMvk-crFAzjWfjDorXxxnNmew"
ARCHIVO_MEMORIA = "jarvis_memoria.json"

MODELOS = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite"
]

# ---------- MEMORIA ----------
def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        try:
            with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_memoria(memoria):
    with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

def recordar(clave, valor):
    memoria = cargar_memoria()
    memoria[clave.lower().strip()] = valor.strip()
    guardar_memoria(memoria)
    return f"Entendido. Recordaré que {clave} es {valor}."

# ---------- VOZ ----------
def hablar(texto):
    if not VOZ_OK:
        return
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
        archivo = "voz_temp.mp3"
        tts.save(archivo)
        pygame.mixer.init()
        pygame.mixer.music.load(archivo)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        os.remove(archivo)
    except Exception as e:
        print("Error voz:", e)

def escuchar():
    if not VOZ_OK:
        return None
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=6, phrase_time_limit=8)
            return r.recognize_google(audio, language="es-ES")
    except:
        return None

# ---------- CEREBRO ----------
def consultar_ia(prompt, memoria):
    contexto = "Eres Jarvis, asistente personal inteligente y leal. Responde natural y conciso en español.\n"
    if memoria:
        contexto += "Sabes del usuario:\n"
        for k, v in memoria.items():
            contexto += f"- {k}: {v}\n"
    prompt_completo = contexto + "\nUsuario: " + prompt

    for modelo in MODELOS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={API_KEY}"
        data = {"contents": [{"parts": [{"text": prompt_completo}]}]}
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                res = json.loads(resp.read().decode())
                return res["candidates"][0]["content"]["parts"][0]["text"]
        except:
            continue
    return "No pude conectarme ahora."

# ---------- INTERFAZ ----------
class JarvisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S.")
        self.root.geometry("400x650")
        self.root.configure(bg="#0f0f0f")

        # Título
        titulo = tk.Label(root, text="J.A.R.V.I.S.", font=("Arial", 20, "bold"),
                          fg="#00ffcc", bg="#0f0f0f")
        titulo.pack(pady=10)

        # Área de chat
        self.chat = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12),
                                              bg="#1a1a1a", fg="white",
                                              insertbackground="white")
        self.chat.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.chat.config(state=tk.DISABLED)

        # Colores de mensajes
        self.chat.tag_config("usuario", foreground="#00bfff")
        self.chat.tag_config("jarvis", foreground="#00ff99")
        self.chat.tag_config("sistema", foreground="#aaaaaa")

        # Entrada de texto
        frame_entrada = tk.Frame(root, bg="#0f0f0f")
        frame_entrada.pack(fill=tk.X, padx=10, pady=5)

        self.entrada = tk.Entry(frame_entrada, font=("Arial", 13), bg="#2a2a2a",
                                fg="white", insertbackground="white")
        self.entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.entrada.bind("<Return>", lambda e: self.enviar_texto())

        btn_enviar = tk.Button(frame_entrada, text="Enviar", command=self.enviar_texto,
                               bg="#00ffcc", fg="black", font=("Arial", 11, "bold"))
        btn_enviar.pack(side=tk.RIGHT, padx=(5, 0))

        # Botones de voz
        frame_voz = tk.Frame(root, bg="#0f0f0f")
        frame_voz.pack(pady=8)

        self.btn_hablar = tk.Button(frame_voz, text="🎤 Hablarle", command=self.hablarle,
                                    bg="#ff5555", fg="white", font=("Arial", 12, "bold"),
                                    width=12, height=1)
        self.btn_hablar.pack(side=tk.LEFT, padx=5)

        btn_salir = tk.Button(frame_voz, text="Salir", command=root.destroy,
                              bg="#555555", fg="white", font=("Arial", 11))
        btn_salir.pack(side=tk.LEFT, padx=5)

        # Saludo inicial
        self.mostrar("sistema", "Jarvis iniciado. Puedes escribir o usar el botón de voz.")
        memoria = cargar_memoria()
        nombre = memoria.get("nombre") or memoria.get("mi nombre")
        if nombre:
            saludo = f"¡Hola de nuevo, {nombre}! ¿En qué te ayudo?"
        else:
            saludo = "¡Hola! Soy Jarvis. Aún no sé tu nombre. ¿Me lo dices?"
        self.responder(saludo)

    def mostrar(self, quien, texto):
        self.chat.config(state=tk.NORMAL)
        if quien == "usuario":
            self.chat.insert(tk.END, f"Tú: {texto}\n\n", "usuario")
        elif quien == "jarvis":
            self.chat.insert(tk.END, f"Jarvis: {texto}\n\n", "jarvis")
        else:
            self.chat.insert(tk.END, f"{texto}\n\n", "sistema")
        self.chat.config(state=tk.DISABLED)
        self.chat.see(tk.END)

    def responder(self, texto):
        self.mostrar("jarvis", texto)
        threading.Thread(target=hablar, args=(texto,), daemon=True).start()

    def enviar_texto(self):
        texto = self.entrada.get().strip()
        if not texto:
            return
        self.entrada.delete(0, tk.END)
        self.mostrar("usuario", texto)
        self.procesar(texto)

    def hablarle(self):
        self.btn_hablar.config(text="Escuchando...", state=tk.DISABLED)
        self.mostrar("sistema", "Te estoy escuchando...")

        def tarea():
            texto = escuchar()
            self.root.after(0, lambda: self.btn_hablar.config(text="🎤 Hablarle", state=tk.NORMAL))
            if texto:
                self.root.after(0, lambda: self.mostrar("usuario", texto))
                self.root.after(0, lambda: self.procesar(texto))
            else:
                self.root.after(0, lambda: self.mostrar("sistema", "No te escuché. Intenta de nuevo o escribe."))

        threading.Thread(target=tarea, daemon=True).start()

    def procesar(self, texto):
        if texto.lower() in ["salir", "adios", "bye", "exit"]:
            self.responder("Hasta luego. Todo queda guardado.")
            self.root.after(2000, self.root.destroy)
            return

        if texto.lower().startswith("recuerda que "):
            resto = texto[13:].strip()
            if " es " in resto:
                clave, valor = resto.split(" es ", 1)
                resp = recordar(clave, valor)
            else:
                resp = "Usa: Recuerda que [cosa] es [valor]"
            self.responder(resp)
            return

        memoria = cargar_memoria()
        def consultar():
            resp = consultar_ia(texto, memoria)
            self.root.after(0, lambda: self.responder(resp))
        threading.Thread(target=consultar, daemon=True).start()

# ---------- INICIO ----------
if __name__ == "__main__":
    if "PEGA_AQUI" in API_KEY:
        print("Pon tu API Key primero")
    else:
        root = tk.Tk()
        app = JarvisApp(root)
        root.mainloop()
