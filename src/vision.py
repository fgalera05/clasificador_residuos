from google import genai
from google.genai import types
import streamlit as st
import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from PIL import Image
import io
import base64
from huggingface_hub import InferenceClient

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

@st.cache_resource
def _cargar_modelo_vision_local():
    """
    Carga el procesador y el modelo local de forma cacheada para evitar
    recargar en memoria en cada interacción/rerun de Streamlit.
    """
    # Determinar el dispositivo
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
        
    model_id = "Qwen/Qwen2-VL-2B-Instruct"
    
    # Reducir píxeles para evitar que MPS (Metal) intente reservar búferes gigantes (e.g. 22 GiB)
    # y para acelerar la inferencia en general.
    min_pixels = 256 * 28 * 28
    max_pixels = 512 * 28 * 28
    
    # Cargar procesador con límites de tamaño de imagen
    processor = AutoProcessor.from_pretrained(
        model_id,
        min_pixels=min_pixels,
        max_pixels=max_pixels
    )
    
    model_kwargs = {
        "torch_dtype": torch.bfloat16 if device != "cpu" else torch.float32,
        "device_map": device
    }
    
    # Solución para bug de MPS (Metal Performance Shaders) en macOS que causa asignaciones de memoria gigantes
    if device == "mps":
        model_kwargs["attn_implementation"] = "eager"
        
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_id,
        **model_kwargs
    )
    
    return model, processor, device

def analizar_imagen_local(image_bytes: bytes) -> str:
    """
    Analiza la imagen utilizando un modelo Qwen2-VL local de forma cacheada y
    con tensores de PyTorch.
    """
    model, processor, device = _cargar_modelo_vision_local()
    
    # Convertir bytes a imagen de PIL
    raw_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    prompt = (
        "Sos un asistente de clasificación de residuos para reciclaje en Argentina. "
        "Analizá esta imagen y describí en UNA oración corta qué tipo de residuo es. "
        "Sé específico con el material y el objeto. "
        "Respondé SOLO con la descripción, sin explicaciones adicionales."
    )
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt}
            ]
        }
    ]
    
    # Generar prompt con el formato del chat
    text_prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    
    # Preparar entradas como tensores de PyTorch y enviarlos al dispositivo
    inputs = processor(
        text=[text_prompt],
        images=[raw_image],
        padding=True,
        return_tensors="pt"
    ).to(device)
    
    # Inferencia local con tensores
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=50
        )
    
    # Recortar entrada de los resultados generados
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    
    # Decodificar el resultado a texto
    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )
    resultado = output_text[0].strip()
    
    # Imprimir en la terminal detalles completos del procesamiento
    print("\n" + "="*50)
    print("🤖 [HF MODEL] PROCESAMIENTO DE IMAGEN")
    print(f"• Dispositivo: {device}")
    print("• Modelo: Qwen/Qwen2-VL-2B-Instruct")
    print(f"• Prompt original:\n  {prompt}")
    print(f"• Prompt formateado:\n  {text_prompt}")
    print(f"• Texto reconocido:\n  >> {resultado} <<")
    print("="*50 + "\n")
    
    return resultado

def analizar_imagen_hf_api(image_bytes: bytes, hf_token: str = None) -> str:
    # Intentamos obtener un token válido desde la UI o los secrets.
    # Si viene vacío, usamos False para desactivar por completo la autenticación y forzar petición anónima.
    token = hf_token if hf_token else st.secrets.get("HF_TOKEN")
    if not token:
        token = False

    client = InferenceClient(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct",
        token=token
    )

    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    prompt = (
        "Sos un asistente de clasificación de residuos para reciclaje en Argentina. "
        "Analizá esta imagen y describí en UNA oración corta qué tipo de residuo es. "
        "Sé específico con el material y el objeto. "
        "Respondé SOLO con la descripción, sin explicaciones adicionales."
    )

    try:
        respuesta = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=50
        )
        resultado = respuesta.choices[0].message.content.strip()
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Invalid username or password" in error_msg:
            raise ValueError(
                "🔑 El Token de Hugging Face configurado es inválido o no tiene permisos. "
                "Por favor, verificá que esté bien escrito o generá uno nuevo con permisos de lectura en huggingface.co/settings/tokens."
            )
        
        print(f"Error con Llama-3.2-11B-Vision-Instruct: {e}. Intentando con Salesforce/blip-image-captioning...")
        # Fallback a un modelo de image-to-text clásico
        client.model = "Salesforce/blip-image-captioning"
        respuesta = client.image_to_text(image_bytes)
        resultado = respuesta.generated_text if hasattr(respuesta, 'generated_text') else str(respuesta)

    # Imprimir en la terminal detalles completos del procesamiento
    print("\n" + "="*50)
    print("☁️ [HF API] PROCESAMIENTO DE IMAGEN")
    print(f"• Modelo: {client.model}")
    print(f"• Prompt original:\n  {prompt}")
    print(f"• Texto reconocido:\n  >> {resultado} <<")
    print("="*50 + "\n")

    return resultado
