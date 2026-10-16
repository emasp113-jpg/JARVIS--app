import asyncio
import os
import edge_tts
import pygame
import speech_recognition as sr

# --- CONFIGURACIÓN DE VOZ ---
# Aquí puedes cambiar el nombre de la voz cuando elijas una nueva
VOZ_ACTUAL = "es-ES-AlvaroNeural"

# --- MEMORIA DE LA CONVERSACIÓN ---
HISTORIAL = [
    {
        "role": "system",
        "content": "Eres JARVIS, un asistente inteligente y atento.",
    }
]


# 1. FUNCIÓN PARA HABLAR (Boca)
async def generar_audio(texto: str, archivo: str = "respuesta.mp3"):
  comunicacion = edge_tts.Communicate(texto, VOZ_ACTUAL)
  await comunicacion.save(archivo)


def hablar(texto: str):
  archivo_temp = "respuesta.mp3"
  asyncio.run(generar_audio(texto, archivo_temp))

  pygame.mixer.init()
  pygame.mixer.music.load(archivo_temp)
  pygame.mixer.music.play()

  while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

  pygame.mixer.quit()
  if os.path.exists(archivo_temp):
    os.remove(archivo_temp)


# 2. FUNCIÓN PARA ESCUCHAR (Oídos)
def escuchar() -> str:
  reconocedor = sr.Recognizer()
  with sr.Microphone() as origen:
    print("\n[JARVIS] Escuchando...")
    reconocedor.adjust_for_ambient_noise(origen, duration=1)
    try:
      audio = reconocedor.listen(origen, timeout=5)
      texto = reconocedor.recognize_google(audio, language="es-ES")
      print(f"Tú dijiste: {texto}")
      return texto
    except sr.WaitTimeoutError:
      print("[JARVIS] No escuché nada.")
      return ""
    except sr.UnknownValueError:
      print("[JARVIS] No entendí lo que dijiste.")
      return ""
    except Exception as e:
      print(f"[JARVIS] Error en el micrófono: {e}")
      return ""


# 3. BUCLE PRINCIPAL DE CONVERSACIÓN
if __name__ == "__main__":
  hablar("Sistemas activados. Hola, te escucho.")

  while True:
    # Escucha tu voz
    mensaje = escuchar()

    if mensaje:
      # Si dices "salir" o "adiós", el sistema se apaga
      if "salir" in mensaje.lower() or "adiós" in mensaje.lower():
        hablar("Desactivando sistemas. Hasta luego.")
        break

      # Procesa y responde
      respuesta = f"Escuché que dijiste: {mensaje}"
      print(f"JARVIS: {respuesta}")
      hablar(respuesta)
