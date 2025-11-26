from rest_framework import serializers
from .models import (
    Pregunta,
    OpcionRespuesta,
    Diagnostico,
    Regla,
    ReglaCondicion,
    Evaluacion,
    Respuesta,
)


class OpcionRespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionRespuesta
        fields = ["id", "etiqueta", "valor"]


class PreguntaSerializer(serializers.ModelSerializer):
    opciones = OpcionRespuestaSerializer(many=True, read_only=True)

    class Meta:
        model = Pregunta
        fields = ["id", "texto", "tipo", "opciones"]


class DiagnosticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnostico
        fields = ["id", "nombre", "recomendaciones"]


class EvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluacion
        fields = ["id", "fecha", "riesgo_final", "puntaje_total", "detalle"]


# ---- Serializers para entrada/salida del endpoint /evaluar ----

class RespuestaEntradaSerializer(serializers.Serializer):
    preguntaId = serializers.IntegerField()
    valor = serializers.CharField(max_length=100)


class EvaluarRequestSerializer(serializers.Serializer):
    respuestas = RespuestaEntradaSerializer(many=True)


class EvaluarResponseSerializer(serializers.Serializer):
    riesgo = serializers.CharField()
    puntaje = serializers.IntegerField()
    recomendaciones = serializers.ListField(
        child=serializers.CharField()
    )
    explicabilidad = serializers.DictField()
    evaluacion_id = serializers.IntegerField()

class RutaMejoraRequestSerializer(serializers.Serializer):
  riesgo = serializers.CharField()
  puntaje = serializers.IntegerField()
  recomendaciones = serializers.ListField(
      child=serializers.CharField()
  )
  reglas_activadas = serializers.ListField(
      child=serializers.DictField()
  )


class RutaMejoraResponseSerializer(serializers.Serializer):
  ruta_mejora = serializers.CharField()

