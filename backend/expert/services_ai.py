from typing import Dict, Any, List

from django.conf import settings
from google import genai


_client = None


def _get_gemini_client():
    """
    Crea (y reutiliza) un cliente de Gemini usando la API key del settings.
    """
    global _client
    if _client is None:
        api_key = getattr(settings, "AI_API_KEY", None)
        if not api_key:
            raise ValueError(
                "No se encontró AI_API_KEY en settings. "
                "Configura AI_API_KEY en el archivo .env."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def generar_ruta_mejora_con_ia(
    riesgo: str,
    recomendaciones: List[str],
    reglas_activadas: List[Dict[str, Any]],
) -> str:
    """
    Usa la librería oficial google-genai para generar una ruta de mejora
    a partir del diagnóstico del sistema experto.
    """

    model = getattr(settings, "AI_MODEL", "gemini-2.5-flash")

    texto_recomendaciones = (
        "\n- ".join(recomendaciones) if recomendaciones else "Sin recomendaciones."
    )
    texto_reglas = (
        "\n".join(
            [
                f"- {r['nombre']} (diagnóstico: {r['diagnostico']}, peso: {r['peso']})"
                for r in reglas_activadas
            ]
        )
        or "No se activaron reglas."
    )

    prompt = f"""
Eres un consultor experto en seguridad de la información.

Con base en este diagnóstico generado por un sistema experto, diseña una RUTA DE IMPLEMENTACIÓN DE MEJORAS
organizada por fases (corto, mediano y largo plazo).
Incluye acciones concretas y responsables sugeridos (Área TI, Dirección, Usuarios, etc.).

RIESGO DETECTADO: {riesgo}

RECOMENDACIONES DEL SISTEMA EXPERTO:
{texto_recomendaciones}

REGLAS ACTIVADAS:
{texto_reglas}

Responde en español, con una estructura clara y usando listas y pasos numerados cuando sea útil.
"""

    try:
        client = _get_gemini_client()
        resp = client.models.generate_content(
            model=model,
            contents=prompt.strip(),
        )

        # La librería expone el texto ya “planchado”
        texto = getattr(resp, "text", None)
        if not texto:
            return "La IA no devolvió contenido utilizable."

        return texto.strip()

    except Exception as e:
        # Para depuración / fallback
        return f"Ocurrió un error al llamar a la API de IA: {e}"
