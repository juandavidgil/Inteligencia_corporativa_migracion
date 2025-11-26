import reflex as rx
import requests


class Dashboard(rx.Base):
    id: int
    nombre_dashboard: str
    embed_url: str
    embed_token: str | None = None


class TablerosState(rx.State):
    proyecto_id: int = None
    dashboard_id: int = None
    usuario_id: int = None

    loading: bool = True
    error: str = ""
    current_dashboard: Dashboard | None = None

    async def cargar_dashboard(self):
        """Mantiene la misma lógica de React."""
        self.loading = True
        self.error = ""

        try:
            response = requests.get(
                f"http://127.0.0.1:8000/api/dashboards_con_embed/{self.proyecto_id}/",
                params={"usuario_id": self.usuario_id}
            )
            data = response.json()

            if response.status_code == 200 and "dashboards" in data:
                # Buscar el dashboard con el ID exacto (MATCH)
                dashboard_data = next(
                    (d for d in data["dashboards"] if d["id"] == self.dashboard_id),
                    None
                )
                if dashboard_data:
                    self.current_dashboard = Dashboard(**dashboard_data)
                else:
                    self.error = "No se encontró el dashboard solicitado."
            else:
                self.error = data.get("error", "No se encontraron dashboards activos.")

        except Exception as e:
            self.error = f"Error al cargar dashboard: {str(e)}"
        finally:
            self.loading = False


def tableros_page():
    """Equivalente a tu componente React."""
    return rx.container(
        rx.vstack(
           
            rx.heading(
                lambda: TablerosState.current_dashboard.nombre_dashboard
                if TablerosState.current_dashboard
                else "Dashboard",
                size="lg"
            ),

            rx.cond(
                TablerosState.loading,
                rx.text("Cargando dashboard...", color="white", font_size="20px"),
            ),

            rx.cond(
                TablerosState.error != "",
                rx.text(lambda: TablerosState.error, color="red"),
            ),

        
rx.cond(
    TablerosState.current_dashboard is not None,
    rx.box(
        rx.html(
            lambda: f"""
            <iframe
                width="100%"
                height="700px"
                src="{TablerosState.current_dashboard.iframe_url}"
                frameborder="0"
                allowFullScreen="true"
                style="border:1px solid #ccc; border-radius:10px; background-color:white;"
            ></iframe>
            """
        ),
        width="100%",
        overflow="hidden",
    ),
),
            spacing="4",
            width="100%",
        ),
        padding="20px",
    )
