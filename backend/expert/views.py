from .serializers import (
    PreguntaSerializer,
    EvaluarRequestSerializer,
    EvaluarResponseSerializer,
    RutaMejoraRequestSerializer,
    RutaMejoraResponseSerializer,
)
from .services_ai import generar_ruta_mejora_con_ia

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def ping(request):
    """
    Endpoint de prueba para verificar que la API está funcionando.
    """
    data = {
        "message": "API del Sistema Experto de Riesgos TI funcionando",
        "status": "ok",
    }
    return Response(data)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Pregunta
from .serializers import (
    PreguntaSerializer,
    EvaluarRequestSerializer,
    EvaluarResponseSerializer,
)
from .services import evaluar_respuestas, guardar_evaluacion


@api_view(["GET"])
def ping(request):
    data = {
        "message": "API del Sistema Experto de Riesgos TI funcionando",
        "status": "ok",
    }
    return Response(data)


@api_view(["GET"])
def listar_preguntas(request):
    """
    Devuelve todas las preguntas activas, con sus opciones.
    """
    preguntas = Pregunta.objects.filter(activo=True).order_by("id")
    serializer = PreguntaSerializer(preguntas, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def evaluar(request):
    """
    Recibe un JSON con respuestas y devuelve
    el riesgo calculado y recomendaciones.
    """
    req_serializer = EvaluarRequestSerializer(data=request.data)
    if not req_serializer.is_valid():
        return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    respuestas = req_serializer.validated_data["respuestas"]

    # Convertimos la lista [{preguntaId, valor}, ...] a dict {id: valor}
    hechos = {item["preguntaId"]: item["valor"] for item in respuestas}

    resultado = evaluar_respuestas(hechos)
    evaluacion_id = guardar_evaluacion(resultado, hechos)

    resp_data = {
        "riesgo": resultado["riesgo"],
        "puntaje": resultado["puntaje"],
        "recomendaciones": resultado["recomendaciones"],
        "explicabilidad": resultado["detalle"],
        "evaluacion_id": evaluacion_id,
    }

    resp_serializer = EvaluarResponseSerializer(resp_data)
    return Response(resp_serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
def ruta_mejora(request):
    """
    Toma el resultado del sistema experto (riesgo, recomendaciones, reglas activadas)
    y llama a una IA externa para generar una ruta de implementación de mejoras.
    """
    req_serializer = RutaMejoraRequestSerializer(data=request.data)
    if not req_serializer.is_valid():
        return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    datos = req_serializer.validated_data
    riesgo = datos["riesgo"]
    recomendaciones = datos["recomendaciones"]
    reglas_activadas = datos["reglas_activadas"]

    texto_ruta = generar_ruta_mejora_con_ia(
        riesgo=riesgo,
        recomendaciones=recomendaciones,
        reglas_activadas=reglas_activadas,
    )

    resp_serializer = RutaMejoraResponseSerializer({"ruta_mejora": texto_ruta})
    return Response(resp_serializer.data, status=status.HTTP_200_OK)
