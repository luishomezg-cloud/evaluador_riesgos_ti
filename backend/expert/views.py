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