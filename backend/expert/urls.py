from django.urls import path
from . import views

urlpatterns = [
    path("ping/", views.ping, name="ping"),
    path("preguntas/", views.listar_preguntas, name="listar_preguntas"),
    path("evaluar/", views.evaluar, name="evaluar"),
    path("ruta-mejora/", views.ruta_mejora, name="ruta_mejora"),
]