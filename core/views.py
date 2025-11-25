from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UsuarioProyecto
from .models import Dashboard 
from .models import UsuarioDashboard

from .serializers import DashboardSerializer
import requests
from django.conf import settings


#LOGIN USUARIO
@api_view(['POST'])
def login_usuario(request):
    correo = request.data.get('correo')
    password = request.data.get('password')

    user = authenticate(username=correo, password=password)
    if not user:
        return Response({'error': 'Credenciales incorrectas'}, status=400)

    
    try:
        tenant_id = settings.POWER_BI_TENANT_ID
        client_id = settings.POWER_BI_CLIENT_ID
        client_secret = settings.POWER_BI_CLIENT_SECRET

        url_token = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        }

        token_response = requests.post(url_token, headers=headers, data=data)
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return Response({'error': 'No se pudo generar el token de Power BI'}, status=400)

        # Guardar el token en el usuario
        user.powerbi_token = access_token
        user.save()

    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({
    'usuario': {
        'id': user.id,
        'nombre': user.nombre,
        'correo': user.correo,
        'rol': user.rol.nombre_rol if user.rol else None,
    },
    'powerbi_token': user.powerbi_token
})

#log out
@api_view(['POST'])
def logout_usuario(request):
    user_id = request.data.get('user_id')
    try:
        usuario = Usuario.objects.get(id=user_id)
        usuario.powerbi_token = None 
        usuario.save()
        return Response({'message': 'Sesión cerrada y token eliminado correctamente'})
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)

#MOSTRAR PROYECTOS A LOS QUE PERTENECE EL USUARIO
def proyectos_por_usuario(request, user_id):
    try:
        proyectos = UsuarioProyecto.objects.filter(usuario_id=user_id).select_related('proyecto')

        data = [
            {
                'id': p.proyecto.id,
                'nombre_proyecto': p.proyecto.nombre_proyecto,
                'descripcion': p.proyecto.descripcion,
                'ubicacion': p.proyecto.ubicacion,
            }
            for p in proyectos
        ]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
#TABLEROS SEGUN PROYECTO
@api_view(['GET'])
def dashboards_proyecto(request, proyecto_id):
    """
    Retorna todos los dashboards asociados a un proyecto específico.
    """
    try:
        dashboards = Dashboard.objects.filter(proyecto_id=proyecto_id, estado=True)
        serializer = DashboardSerializer(dashboards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


#GENERAR TOKEN
@api_view(['GET']) 
def generar_token_powerbi(request):
    """
    Genera un nuevo embed token para Power BI.
    """
    try:
        tenant_id = settings.POWER_BI_TENANT_ID
        client_id = settings.POWER_BI_CLIENT_ID
        client_secret = settings.POWER_BI_CLIENT_SECRET
        workspace_id = settings.POWER_BI_WORKSPACE_ID

        # 1️⃣ Obtener access token desde Azure AD
        url_token = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        }

        token_response = requests.post(url_token, headers=headers, data=data)
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return Response({"error": "No se pudo obtener el token de acceso."}, status=400)

        # 2️⃣ Devolver token al frontend
        return Response({"token": access_token}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)    



#MOSTRAR  TABLERO DEL PROYECTO
@api_view(['GET'])
def dashboards_con_embed(request, proyecto_id):
    try:
        # 🟩 Nuevo: obtener el usuario desde query params
        usuario_id = request.query_params.get('usuario_id')
        if not usuario_id:
            return Response({"error": "Debe enviar usuario_id"}, status=400)

        # 🟩 Nuevo: filtrar dashboards asignados al usuario en ese proyecto
        dashboards_ids = UsuarioDashboard.objects.filter(
            usuario_id=usuario_id,
            proyecto_id=proyecto_id
        ).values_list('dashboard_id', flat=True)

        # 🟩 Filtrar solo dashboards activos y asignados
        dashboards = Dashboard.objects.filter(
            proyecto_id=proyecto_id,
            id__in=dashboards_ids,
            estado=True
        )

        if not dashboards.exists():
            return Response({"error": "No hay dashboards activos para este usuario en este proyecto."}, status=404)

        serializer = DashboardSerializer(dashboards, many=True)

        # 🔹 Configuración Power BI
        tenant_id = settings.POWER_BI_TENANT_ID
        client_id = settings.POWER_BI_CLIENT_ID
        client_secret = settings.POWER_BI_CLIENT_SECRET

        # 🔹 Obtener access token
        url_token = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        }

        token_response = requests.post(url_token, headers=headers, data=data)
        if token_response.status_code != 200:
            return Response(
                {"error": "Error al obtener access_token", "detalle": token_response.text},
                status=token_response.status_code
            )

        access_token = token_response.json().get("access_token")
        if not access_token:
            return Response({"error": "No se recibió access_token desde Azure AD."}, status=400)

        dashboards_embed = []

        # 🔹 Recorre cada dashboard (idéntico a tu versión)
        for dash in serializer.data:
            report_id = dash.get('report_id')
            workspace_id = dash.get('workspace_id')

            if not report_id:
                continue

            url_report_api = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}"
            headers_report = {"Authorization": f"Bearer {access_token}"}
            report_response = requests.get(url_report_api, headers=headers_report)

            if report_response.status_code != 200:
                dashboards_embed.append({
                    "nombre_dashboard": dash['nombre_dashboard'],
                    "error": f"No se pudo acceder al reporte {report_id}. "
                             f"Verifica permisos o IDs. ({report_response.status_code})"
                })
                continue

            report_data = report_response.json()
            embed_url = report_data.get("embedUrl")

            # Generar token de incrustación
            url_embed_api = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken"
            headers_embed = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            payload = {"accessLevel": "view"}
            embed_response = requests.post(url_embed_api, headers=headers_embed, json=payload)

            if embed_response.status_code != 200:
                dashboards_embed.append({
                    "nombre_dashboard": dash['nombre_dashboard'],
                    "error": f"No se pudo generar embed_token. "
                             f"Código: {embed_response.status_code}. "
                             f"Detalle: {embed_response.text}"
                })
                continue

            embed_token = embed_response.json().get("token")

            dashboards_embed.append({
                "id": dash['id'],
                "nombre_dashboard": dash['nombre_dashboard'],
                "report_id": report_id,
                "workspace_id": workspace_id,
                "embed_url": embed_url,
                "embed_token": embed_token
            })

        return Response({"dashboards": dashboards_embed}, status=200)

    except Exception as e:
        return Response({"error": f"Excepción en servidor: {str(e)}"}, status=500)


@api_view(['GET'])
def dashboards_por_usuario_y_proyecto(request, proyecto_id):
    usuario_id = request.query_params.get('usuario_id')

    if not usuario_id:
        return Response(
            {"error": "Debe enviar el usuario_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        dashboards_ids = UsuarioDashboard.objects.filter(
            usuario_id=usuario_id,
            proyecto_id=proyecto_id
        ).values_list('dashboard_id', flat=True)

        dashboards = Dashboard.objects.filter(id__in=dashboards_ids, estado=True)

        if not dashboards.exists():
            return Response(
                {"error": "No hay dashboards activos para este usuario en este proyecto."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DashboardSerializer(dashboards, many=True)
        return Response({"dashboards": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        print("Error en dashboards_por_usuario_y_proyecto:", e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 