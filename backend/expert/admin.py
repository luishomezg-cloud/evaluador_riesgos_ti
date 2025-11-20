from django.contrib import admin
from .models import (
    Pregunta,
    OpcionRespuesta,
    Diagnostico,
    Regla,
    ReglaCondicion,
    Evaluacion,
    Respuesta,
)


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("id", "texto", "tipo", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("texto",)


@admin.register(OpcionRespuesta)
class OpcionRespuestaAdmin(admin.ModelAdmin):
    list_display = ("id", "pregunta", "etiqueta", "valor")
    list_filter = ("pregunta",)
    search_fields = ("etiqueta", "valor")


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


class ReglaCondicionInline(admin.TabularInline):
    model = ReglaCondicion
    extra = 1


@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "peso", "diagnostico")
    list_filter = ("diagnostico",)
    search_fields = ("nombre", "descripcion")
    inlines = [ReglaCondicionInline]


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "riesgo_final", "puntaje_total")
    list_filter = ("riesgo_final", "fecha")


@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ("id", "evaluacion", "pregunta", "valor")
    list_filter = ("evaluacion", "pregunta")
