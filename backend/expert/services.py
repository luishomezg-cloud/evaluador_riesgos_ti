from typing import List, Dict, Any
from .models import Regla, Evaluacion, Respuesta, Diagnostico


def _comparar(val_hecho: str, operador: str, valor_regla: str) -> bool:
    """
    Compara el valor del hecho con la condición de la regla.
    Todo se maneja como texto sencillo para mantenerlo simple.
    """
    if val_hecho is None:
        return False

    if operador == "=":
        return val_hecho == valor_regla
    if operador == "!=":
        return val_hecho != valor_regla
    if operador == "IN":
        opciones = [v.strip() for v in valor_regla.split(",")]
        return val_hecho in opciones

    # Intento de comparación numérica para >= y <=
    try:
        vh = float(val_hecho)
        vr = float(valor_regla)
    except ValueError:
        return False

    if operador == ">=":
        return vh >= vr
    if operador == "<=":
        return vh <= vr

    return False



    """
    Motor de inferencia básico:
    - Recorre todas las reglas.
    - Verifica si todas las condiciones se cumplen.
    - Suma pesos de reglas activadas.
    - Determina riesgo según el puntaje total.
    """
    reglas = Regla.objects.select_related("diagnostico").prefetch_related("condiciones")
    puntaje_total = 0
    reglas_activadas = []
    diagnosticos_encontrados = []

    for regla in reglas:
        condiciones_ok = True
        for cond in regla.condiciones.all():
            val_hecho = hechos.get(cond.pregunta_id)
            if not _comparar(val_hecho, cond.operador, cond.valor):
                condiciones_ok = False
                break

        if condiciones_ok:
            puntaje_total += regla.peso
            reglas_activadas.append(
                {
                    "regla_id": regla.id,
                    "nombre": regla.nombre,
                    "diagnostico": regla.diagnostico.nombre,
                    "peso": regla.peso,
                }
            )
            diagnosticos_encontrados.append(regla.diagnostico)

    # Determinar riesgo por puntaje
    if puntaje_total >= 70:
        riesgo = "ALTO"
    elif puntaje_total >= 40:
        riesgo = "MEDIO"
    else:
        riesgo = "BAJO"

    # Recomendaciones -> unir las de todos los diagnósticos activados
    recomendaciones = []
    for dx in diagnosticos_encontrados:
        if dx.recomendaciones not in recomendaciones:
            recomendaciones.append(dx.recomendaciones)

    if not recomendaciones:
        recomendaciones.append(
            "Mantener controles actuales y revisar periódicamente la postura de seguridad."
        )

    detalle = {
        "reglas_activadas": reglas_activadas,
        "puntaje_total": puntaje_total,
    }

    return {
        "riesgo": riesgo,
        "puntaje": puntaje_total,
        "recomendaciones": recomendaciones,
        "detalle": detalle,
    }

def evaluar_respuestas(hechos: Dict[int, str]) -> Dict[str, Any]:
    """
    Motor de inferencia básico:
    - Recorre todas las reglas.
    - Verifica si todas las condiciones se cumplen.
    - Suma pesos de reglas activadas (para tener una idea de intensidad).
    - Determina el riesgo principalmente por el tipo de diagnóstico
      (ALTO / MEDIO), y usa el puntaje como apoyo.
    """
    reglas = Regla.objects.select_related("diagnostico").prefetch_related("condiciones")
    puntaje_total = 0
    reglas_activadas = []
    diagnosticos_encontrados = []

    for regla in reglas:
        condiciones_ok = True
        for cond in regla.condiciones.all():
            val_hecho = hechos.get(cond.pregunta_id)
            if not _comparar(val_hecho, cond.operador, cond.valor):
                condiciones_ok = False
                break

        if condiciones_ok:
            puntaje_total += regla.peso
            reglas_activadas.append(
                {
                    "regla_id": regla.id,
                    "nombre": regla.nombre,
                    "diagnostico": regla.diagnostico.nombre,
                    "peso": regla.peso,
                }
            )
            diagnosticos_encontrados.append(regla.diagnostico.nombre)

    # ---- Determinación del riesgo ----
    if "ALTO" in diagnosticos_encontrados:
        riesgo = "ALTO"
    elif "MEDIO" in diagnosticos_encontrados:
        riesgo = "MEDIO"
    else:
        # No se activó ninguna regla de ALTO ni de MEDIO
        riesgo = "BAJO"

    # Recomendaciones -> unir las de todos los diagnósticos activados
    recomendaciones = []
    for dx_nombre in set(diagnosticos_encontrados):
        # buscamos el objeto Diagnostico por nombre
        try:
            dx_obj = Diagnostico.objects.get(nombre=dx_nombre)
            if dx_obj.recomendaciones not in recomendaciones:
                recomendaciones.append(dx_obj.recomendaciones)
        except Diagnostico.DoesNotExist:
            continue

    if not recomendaciones:
        recomendaciones.append(
            "Mantener controles actuales y revisar periódicamente la postura de seguridad."
        )

    detalle = {
        "reglas_activadas": reglas_activadas,
        "puntaje_total": puntaje_total,
    }

    return {
        "riesgo": riesgo,
        "puntaje": puntaje_total,
        "recomendaciones": recomendaciones,
        "detalle": detalle,
    }

def guardar_evaluacion(resultado: Dict[str, Any], hechos: Dict[int, str]) -> int:
    """
    Persiste la evaluación y las respuestas en la base de datos.
    Retorna el ID de la evaluación creada.
    """
    eval_obj = Evaluacion.objects.create(
        riesgo_final=resultado["riesgo"],
        puntaje_total=resultado["puntaje"],
        detalle=str(resultado.get("detalle", "")),
    )

    respuestas = [
        Respuesta(
            evaluacion=eval_obj,
            pregunta_id=p_id,
            valor=valor,
        )
        for p_id, valor in hechos.items()
    ]
    Respuesta.objects.bulk_create(respuestas)
    return eval_obj.id
