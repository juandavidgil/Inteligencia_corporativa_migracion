import reflex as rx
import json


class DashboardState(rx.State):
    dashboards: list = []
    loading: bool = True
    proyecto_id: int = None

    def on_load(self):
        """Carga inicial: obtiene proyecto_id desde la URL y busca dashboards."""
        params = rx.get_query_params()
        self.proyecto_id = int(params.get("proyecto_id", [0])[0])

        if not self.proyecto_id:
            self.loading = False
            return

        cache_key = f"dashboards_{self.proyecto_id}"
        cache_data = rx.get_session_storage(cache_key)

        if cache_data:
            self.dashboards = json.loads(cache_data)
            self.loading = False
        else:
            self.fetch_dashboards()

    async def fetch_dashboards(self):
        """Consulta al backend Django para obtener dashboards con embed."""
        try:
            usuario = json.loads(rx.get_local_storage("usuario") or "{}")
            url = f"http://127.0.0.1:8000/api/dashboards_con_embed/{self.proyecto_id}/?usuario_id={usuario.get('id')}"

            response = await rx.get(url)

            if response.status_code == 200:
                data = response.json()
                self.dashboards = data.get("dashboards", [])
                rx.set_session_storage(f"dashboards_{self.proyecto_id}", json.dumps(self.dashboards))
        except Exception as e:
            print("Error de conexión:", e)
        self.loading = False

    def ir_tablero(self, dashboard):
        """Navega al tablero seleccionado pasando parámetros."""
        return rx.redirect(
            f"/tableros?proyectoId={self.proyecto_id}"
            f"&dashboardId={dashboard['id']}"
            f"&nombreDashboard={dashboard['nombre_dashboard']}"
        )


def obtener_icono(nombre_dashboard: str):
    """Mapea el nombre del dashboard a una imagen o icono."""
    nombre = nombre_dashboard.lower()
    imagenes = {
        "financiero": "../assets/financiero.png",
        "indicadores": "../assets/indicadores.png",
        "operativo": "../assets/operativo.png",
        "agenda": "../assets/agenda.png",
        "aranda": "../assets/aranda.png",
    }
    for key, img in imagenes.items():
        if key in nombre:
            return rx.image(src=img, width="70px", height="70px")

    return rx.icon("bar_chart", size="60px")  

def tarjeta_dashboard(dashboard):
    """Tarjeta individual de dashboard."""
    return rx.button(
        rx.vstack(
            obtener_icono(dashboard["nombre_dashboard"]),
            rx.text(dashboard["nombre_dashboard"], color="white", font_size="18px", text_align="center"),
            align="center",
        ),
        on_click=lambda: DashboardState.ir_tablero(dashboard),
        padding="20px",
        background_color="#1e293b",
        border_radius="12px",
        box_shadow="0 4px 10px rgba(0,0,0,0.3)",
        cursor="pointer",
        _hover={"transform": "scale(1.05)", "transition": "0.3s"},
        width="220px",
        height="200px",
    )


def dashboard_page():
    """Estructura visual de la página."""
    return rx.box(
        rx.cond(
            DashboardState.loading,
            rx.center(rx.text("Cargando dashboards...", font_size="24px", color="white")),
            rx.box(
                rx.heading("Dashboards del Módulo", color="white", font_size="32px"),
                rx.text("Selecciona un dashboard para visualizarlo.",
                        font_size="18px", color="white", margin_bottom="20px"),
                rx.flex(
                    rx.foreach(DashboardState.dashboards, tarjeta_dashboard),
                    wrap="wrap",
                    gap="25px",
                    justify="center",
                    margin_top="20px",
                ),
                padding="40px",
                text_align="center",
            ),
        ),
        background_color="#0f172a",
        min_height="100vh",
        on_mount=DashboardState.on_load,
    )



app = rx.App()
app.add_page(dashboard_page, route="/dashboard")
