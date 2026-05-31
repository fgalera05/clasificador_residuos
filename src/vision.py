from google import genai
from google.genai import types

def analizar_imagen_con_gemini(image_bytes: bytes, mime_type: str, api_key: str) -> str:
    """
    Configura Gemini y envía los bytes de la imagen con el prompt 
    para obtener una descripción corta en texto del residuo.
    """
    client = genai.Client(api_key=api_key)

    prompt = (
        "Sos un asistente de clasificación de residuos para reciclaje en Argentina. "
        "Analizá esta imagen y describí en UNA oración corta qué tipo de residuo es. "
        "Sé específico con el material y el objeto. "
        "Respondé SOLO con la descripción, sin explicaciones adicionales."
    )

    respuesta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            prompt
        ]
    )
    resultado = respuesta.text.strip()

    # Imprimir en la terminal detalles completos del procesamiento
    print("\n" + "="*50)
    print("☁️ [GEMINI MODEL] PROCESAMIENTO DE IMAGEN")
    print("• Dispositivo: Nube (API de Gemini)")
    print("• Modelo: gemini-2.5-flash")
    print(f"• Prompt original:\n  {prompt}")
    print(f"• Texto reconocido:\n  >> {resultado} <<")
    print("="*50 + "\n")

    return resultado
