import reflex as rx

config = rx.Config(
    app_name="Inteligencia_Corporativa",
    api_url="http://127.0.0.1:5555",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)