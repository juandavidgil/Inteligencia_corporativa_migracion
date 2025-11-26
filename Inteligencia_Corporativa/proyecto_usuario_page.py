
import reflex as rx
import json
from pydantic import BaseModel

class Proyecto(BaseModel):
    id: int
    nombre_proyecto: str


class ProyectosState(rx.State):
    proyectos: list[Proyecto] = []
    loading: bool = True
    usuario: dict = {}
    imagenes_proyectos: dict = {
        "Guayaquil": "/assets/ATM.png",
        "VUS": "/assets/VUS.png",
        "MOVIDIC": "/assets/MOVIDIC.png",
        "Chía": "/assets/Chia.png",
        "Silvania": "/assets/Silvania.jpg",
        "Neiva": "/assets/Neiva.jpg",
        "Cartagena": "/assets/Cartagena.png",
        "Data": "/assets/dataTools.jpg",
    }

    async def on_load(self):
        try:
            self.usuario = json.loads(rx.get_local_storage("usuario") or "{}")
           

            if not self.usuario:
                self.loading = False
                return

            cache = rx.get_session_storage("proyectos_usuario")

            if cache:
                self.proyectos = [Proyecto(**p) for p in json.loads(cache)]
                self.loading = False
                return

            await self.fetch_proyectos()
        except Exception:
            self.loading = False

    async def fetch_proyectos(self):
        url = f"http://127.0.0.1:8000/api/proyectos_usuario/{self.usuario.get('id')}/"
        print(url)
        try:
            response = await rx.get(url)
            if response.status_code == 200:
                self.proyectos = [
                    Proyecto(id=p["id"], nombre_proyecto=p["nombre_proyecto"])
                    for p in response.json()
                ]
                rx.set_session_storage("proyectos_usuario", json.dumps([p.dict() for p in self.proyectos]))
        except Exception as e:
            print("Error de conexión:", e)
        self.loading = False

    def cerrar_sesion(self):
        rx.clear_local_storage()
        rx.clear_session_storage()
        return rx.redirect("/")

    def ir_dashboard(self, proyecto_id: int):
        return rx.redirect(f"/dashboard?proyecto_id={proyecto_id}")


def tarjeta_proyecto(proyecto):
    return rx.box(
        rx.image(
            src=("/assets/" + proyecto.nombre_proyecto.lower().replace(" ", "_") + ".png"),
            width="200px",
            height="150px",
            border_radius="10px",
        ),
        rx.text(proyecto.nombre_proyecto, color="white", font_size="18px"),
        on_click=lambda: ProyectosState.ir_dashboard(proyecto.id),
        cursor="pointer",
        padding="10px",
        background_color="#1e293b",
        border_radius="12px",
        box_shadow="0 4px 10px rgba(0,0,0,0.3)",
        _hover={"transform": "scale(1.05)", "transition": "0.3s"},
    )


def proyecto_usuario_page():
    return rx.box(
          
           rx.cond(
            ProyectosState.loading,
            rx.center(rx.text("Cargando tus módulos...", font_size="24px", color="white")),
            rx.box(
                rx.heading("MÓDULOS", color="white", font_size="32px"),
                rx.text("Aquí puedes ver los módulos en los que estás participando.", font_size="18px", color="white"),
                rx.cond(
                    ProyectosState.proyectos.length() > 0,  # ✅ CORREGIDO
                    rx.flex(
                        rx.foreach(ProyectosState.proyectos, tarjeta_proyecto),
                        wrap="wrap",
                        gap="20px",
                        justify="center",
                        margin_top="20px",
                    ),
                    rx.text("No tienes proyectos asignados actualmente.", font_size="20px", color="white", margin_top="30px"),
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
