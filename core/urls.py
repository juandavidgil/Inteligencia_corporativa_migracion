from django.urls import path

from . import views

urlpatterns = [
   path('login/', views.login_usuario, name='login_usuario'),
   path('logout/', views.logout_usuario, name='logout_usuario'),
   path('proyectos_usuario/<int:user_id>/', views.proyectos_por_usuario, name='proyectos_por_usuario'),
   path('dashboards_proyecto/<int:proyecto_id>/', views.dashboards_proyecto, name='dashboards_proyecto'),
   path('generar_token_powerbi/', views.generar_token_powerbi, name='generar_token_powerbi'),
   path('dashboards_con_embed/<int:proyecto_id>/', views.dashboards_con_embed, name='dashboards_con_embed'),
   ]

