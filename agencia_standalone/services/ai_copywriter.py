import os
import json
import httpx

async def generar_textos_persuasivos(nombre: str, rubro: str, ciudad: str, custom_prompt: str = None) -> dict:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("[AI] Falta la DEEPSEEK_API_KEY en el .env")
        return None

    url = "https://api.deepseek.com/chat/completions"
    
    instrucciones_extra = f"\nDirectivas adicionales de diseño y enfoque del usuario:\n'{custom_prompt}'" if custom_prompt else ""
    
    prompt = f"""
    Escribe el contenido de respuesta directa y marketing persuasivo para una landing page ultra profesional de este negocio:
    
    Nombre del negocio: {nombre}
    Rubro / Categoría: {rubro}
    Ciudad / Ubicación: {ciudad}
    {instrucciones_extra}
    
    Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta sin texto adicional:
    {{
        "titulo_principal": "Título impacto y gancho comercial irresistible (máx 9 palabras)",
        "subtitulo": "Propuesta de valor clara que resuelve el dolor del cliente (máx 18 palabras)",
        "beneficio_1_titulo": "Título de beneficio 1",
        "beneficio_1_desc": "Explicación breve del beneficio 1",
        "beneficio_2_titulo": "Título de beneficio 2",
        "beneficio_2_desc": "Explicación breve del beneficio 2",
        "beneficio_3_titulo": "Título de beneficio 3",
        "beneficio_3_desc": "Explicación breve del beneficio 3",
        "testimonio_1_nombre": "Nombre cliente satisfecho 1",
        "testimonio_1_texto": "Reseña positiva sobre la atención y calidad del servicio",
        "testimonio_2_nombre": "Nombre cliente satisfecho 2",
        "testimonio_2_texto": "Reseña positiva destacando la rapidez y garantía",
        "faq_1_preg": "Pregunta frecuente 1 sobre el servicio",
        "faq_1_resp": "Respuesta clara a la pregunta frecuente 1",
        "faq_2_preg": "Pregunta frecuente 2 sobre precios y reservas",
        "faq_2_resp": "Respuesta clara a la pregunta frecuente 2",
        "cta": "Texto de llamado a la acción (ej: Reservar / Activar Web)",
        "categoria_imagen": "Elige estrictamente UNA de estas opciones que mejor represente al negocio: musica, gastronomia, automotriz, tecnologia, logistica, salud_belleza, retail, corporativo"
    }}
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Eres un copywriter de respuesta directa galardonado. Responde estrictamente en formato JSON puro sin formato markdown o bloques de código."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    print(f"[IA DeepSeek] Generando copy profesional para: {nombre} ({rubro})...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"].strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            return json.loads(raw_text)
        except Exception as e:
            print(f"[AI] Error invocando DeepSeek API: {e}")
            return None
