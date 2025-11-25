from rest_framework import serializers
from .models import Usuario, Rol, Proyecto, Dashboard, UsuarioDashboard

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'nombre', 'correo', 'cargo', 'rol')


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = ['id', 'nombre_dashboard', 'workspace_id', 'report_id',  'tipo', 'estado']


class ProyectoConDashboardsSerializer(serializers.ModelSerializer):
    dashboards = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = ('id', 'nombre_proyecto', 'descripcion', 'dashboards')

    def get_dashboards(self, obj):
        qs = Dashboard.objects.filter(proyecto=obj, estado=True)
        return DashboardSerializer(qs, many=True).data

class UsuarioDashboardSerializer(serializers.ModelSerializer):
    dashboard = DashboardSerializer()

    class Meta:
        model = UsuarioDashboard
        fields = ['id', 'usuario', 'proyecto', 'dashboard', 'fecha_asignacion']