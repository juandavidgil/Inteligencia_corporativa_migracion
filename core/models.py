from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre_rol


class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombre, password):
        user = self.create_user(correo, nombre, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    correo = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    powerbi_token = models.TextField(null=True, blank=True)

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    objects = UsuarioManager()

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    nombre_proyecto = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    ubicacion = models.CharField(max_length=100, null=True, blank=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_proyecto


class UsuarioProyecto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'proyecto')

    def __str__(self):
        return f"{self.usuario.nombre} - {self.proyecto.nombre_proyecto}"


# ✅ Modelo actualizado
class Dashboard(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    nombre_dashboard = models.CharField(max_length=100)
    workspace_id = models.CharField(max_length=200)
    report_id = models.CharField(max_length=200, null=True, blank=True)
    tipo = models.CharField(max_length=50, null=True, blank=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.proyecto.nombre_proyecto} - {self.nombre_dashboard} ({self.tipo})"

class UsuarioDashboard(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'proyecto', 'dashboard')

    def __str__(self):
        return f"{self.usuario.nombre} - {self.proyecto.nombre_proyecto} - {self.dashboard.nombre_dashboard}"
