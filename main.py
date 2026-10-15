import asyncio
import edge_tts
import os
import pygame

# Voz seleccionada (puedes cambiarla después si gustas)
VOZ_ACTUAL = "es-ES-AlvaroNeural"


async def generar_audio(texto: str, archivo_salida: str = "voz.mp3"):
  comunicacion = edge_tts.Communicate(texto, VOZ_ACTUAL)
  await comunicacion.save(archivo_salida)


def hablar(texto: str):
  archivo_temp = "voz.mp3"
  asyncio.run(generar_audio(texto, archivo_temp))

  pygame.mixer.init()
  pygame.mixer.music.load(archivo_temp)
  pygame.mixer.music.play()

  while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

  pygame.mixer.quit()
  if os.path.exists(archivo_temp):
    os.remove(archivo_temp)


if __name__ == "__main__":
  hablar("Hola, soy JARVIS. Sistema de voz neuronal activado.")

  
