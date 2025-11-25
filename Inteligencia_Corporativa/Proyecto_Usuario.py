import reflex as rx
import json
import os



class ProyectosState(rx.State):
    proyectos: list = []
    loading: bool = True
    usuario: dict = {}
    imagenes_proyectos: dict = {}

    def on_load(self):
        """Carga inicial: usuario, proyectos y cache."""
        try:
        
            self.usuario = json.loads(rx.get_local_storage("usuario") or "{}")

            if not self.usuario:
                self.loading = False
                return

            cache = rx.get_session_storage("proyectos_usuario")
            if cache:
                self.proyectos = json.loads(cache)
                self.loading = False
                return

         
            self.fetch_proyectos()
        except Exception:
            self.loading = False

    async def fetch_proyectos(self):
        url = f"http://127.0.0.1:8000/api/proyectos_usuario/{self.usuario.get('id')}/"
        try:
            response = await rx.get(url)
            if response.status_code == 200:
                self.proyectos = response.json()
                rx.set_session_storage("proyectos_usuario", json.dumps(self.proyectos))
        except Exception as e:
            print("Error de conexión:", e)
        self.loading = False

    def cerrar_sesion(self):
        rx.clear_local_storage()
        rx.clear_session_storage()
        return rx.redirect("/")

    def ir_dashboard(self, proyecto_id: int):
        return rx.redirect(f"/dashboard?proyecto_id={proyecto_id}")



def obtener_imagen(nombre):
    ruta = f"/assets/{nombre.lower().replace(' ', '_')}.png"
    return ruta if os.path.exists(f"frontend/{ruta}") else "/assets/data.png"



def tarjeta_proyecto(proyecto):
    imagen = obtener_imagen(proyecto["nombre_proyecto"])
    return rx.box(
        rx.image(src=imagen, width="200px", height="150px", border_radius="10px"),
        rx.text(proyecto["nombre_proyecto"], color="white", font_size="18px"),
        on_click=lambda: ProyectosState.ir_dashboard(proyecto["id"]),
        cursor="pointer",
        padding="10px",
        background_color="#1e293b",
        border_radius="12px",
        box_shadow="0 4px 10px rgba(0,0,0,0.3)",
        _hover={"transform": "scale(1.05)", "transition": "0.3s"},
    )



def proyectos_usuario_page():
    return rx.box(
        rx.cond(
            ProyectosState.loading,
            rx.center(rx.text("Cargando tus módulos...", font_size="24px", color="white")),
            rx.box(
                rx.heading("MÓDULOS", color="white", font_size="32px"),
                rx.text("Aquí puedes ver los módulos en los que estás participando.",
                        font_size="18px", color="white"),
                rx.flex(
                    rx.foreach(ProyectosState.proyectos, tarjeta_proyecto),
                    wrap="wrap",
                    gap="20px",
                    justify="center",
                    margin_top="20px",
                ),
                rx.button(
                    "Cerrar Sesión",
                    on_click=ProyectosState.cerrar_sesion,
                    background_color="#ef4444",
                    color="white",
                    margin_top="30px",
                    padding="12px 20px",
                    border_radius="8px",
                ),
                padding="30px",
                text_align="center",
            ),
        ),
        background_color="#0f172a",
        min_height="100vh",
        padding="50px",
        on_mount=ProyectosState.on_load,
    )




app.add_page(proyectos_usuario_page, route="/Proyecto_Usuario")
