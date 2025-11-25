import reflex as rx
import httpx
import json

BACKEND_URL = "http://127.0.0.1:8000/api"  

class UsuarioState(rx.State):
    correo: str = ""
    password: str = ""
    mensaje: str = ""
    cargando: bool = False

    # Estado solo en memoria
    usuario: dict = {}
    powerbi_token: str = ""
    proyectos_usuario: list = []
    dashboards: dict = {}

    async def ingresar(self, **kwargs):
        self.cargando = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/login/",
                    json={"correo": self.correo, "password": self.password},
                    timeout=10.0
                )

            data = response.json()

            if response.status_code == 200:
       
                self.usuario = data["usuario"]
                self.powerbi_token = data["powerbi_token"]

                await self.precargar_datos(data["usuario"]["id"])

                self.mensaje = f"Bienvenido {data['usuario']['nombre']}"
                return rx.redirect("/Proyecto_Usuario")
            else:
                self.mensaje = data.get("error", "Credenciales incorrectas")
        except Exception as e:
            self.mensaje = f"Error al conectar con el servidor: {str(e)}"
        finally:
            self.cargando = False

    async def precargar_datos(self, usuario_id: int):
        try:
            async with httpx.AsyncClient() as client:
               
                proyectos_res = await client.get(f"{BACKEND_URL}/proyectos_usuario/{usuario_id}/")
                if proyectos_res.status_code != 200:
                    return
                proyectos = proyectos_res.json()
                self.proyectos_usuario = proyectos

                dashboards_dict = {}
                for proyecto in proyectos:
                    dashboards_res = await client.get(
                        f"{BACKEND_URL}/dashboards_con_embed/{proyecto['id']}/?usuario_id={usuario_id}"
                    )
                    if dashboards_res.status_code == 200:
                        dashboards_data = dashboards_res.json()
                        dashboards_dict[str(proyecto['id'])] = dashboards_data.get("dashboards", [])

                self.dashboards = dashboards_dict
        except Exception:
            pass

    def Administrar(self, **kwargs):
        return rx.redirect("http://127.0.0.1:8000/admin/")

    def cerrar_sesion(self, **kwargs):
        self.correo = ""
        self.password = ""
        self.mensaje = ""
        self.cargando = False
        self.usuario = {}
        self.powerbi_token = ""
        self.proyectos_usuario = []
        self.dashboards = {}
        return rx.redirect("/login")


def login_page() -> rx.Component:
    return rx.center(
        rx.box(
            rx.form(
                rx.vstack(
                    rx.heading("Inteligencia Corporativa", size="5"),
                    rx.text("Correo electrónico"),
                    rx.input(
                        placeholder="Ingrese su correo electrónico",
                        value=UsuarioState.correo,
                        on_change=UsuarioState.set_correo,
                        type_="email",
                        required=True,
                        width="100%",
                    ),
                    rx.text("Contraseña"),
                    rx.input(
                        placeholder="Ingrese su contraseña",
                        value=UsuarioState.password,
                        on_change=UsuarioState.set_password,
                        type_="password",
                        required=True,
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Ingresar",
                            on_click=UsuarioState.ingresar,
                            loading=UsuarioState.cargando,
                            width="100%",
                        ),
                        rx.button(
                            "Administrar",
                            on_click=UsuarioState.Administrar,
                            width="100%",
                            variant="outline",
                        ),
                        width="100%",
                    ),
                    rx.text(UsuarioState.mensaje, color="red"),
                    rx.text('"Producto No Para"', font_style="italic"),
                    spacing="4",
                ),
                on_submit=UsuarioState.ingresar,
            ),
            width="400px",
            padding="2em",
            border="1px solid #ddd",
            border_radius="10px",
            box_shadow="lg",
        ),
        height="100vh",
    )


app = rx.App()
app.add_page(login_page, route="/")
