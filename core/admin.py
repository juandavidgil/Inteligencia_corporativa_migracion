from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Rol, Usuario, Proyecto, UsuarioProyecto, Dashboard, UsuarioDashboard

class UsuarioAdmin(BaseUserAdmin):
    ordering = ('correo',)
    list_display = ('correo', 'nombre', 'rol', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Información personal', {'fields': ('nombre', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'nombre', 'password1', 'password2', 'rol', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('correo', 'nombre')

admin.site.register(Rol)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Proyecto)
admin.site.register(UsuarioProyecto)
admin.site.register(Dashboard)
admin.site.register(UsuarioDashboard)