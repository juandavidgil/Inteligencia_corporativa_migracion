import reflex as rx
from Inteligencia_Corporativa.login_page import login_page
from Inteligencia_Corporativa.proyecto_usuario_page import proyecto_usuario_page

app = rx.App()
app.add_page(login_page, route="/")
app.add_page(proyecto_usuario_page, route="/proyecto_usuario")
