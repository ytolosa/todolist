import flet as ft
from flet_core.types import AppView

from categories import CategoryList
from login import Login, Register
from tasks import TaskList


def main(page: ft.Page):
    def route_change(route):
        if page.route == "/register":
            page.views.append(
                ft.View(
                    "/register",
                    [Register()],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
            return

        if (
            not page.client_storage.contains_key("token")
            or page.route == "/login"
            or page.route == "/logout"
        ):
            page.views.clear()
            page.route = "/login"
            page.client_storage.clear()
            page.views.append(
                ft.View(
                    "/login",
                    [Login(on_login=lambda: page.go("/tasks"))],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
            return

        if page.route == "/categories":
            page.views.clear()
            page.views.append(
                ft.View(
                    "/store",
                    [
                        ft.AppBar(
                            title=ft.Row(
                                [
                                    ft.IconButton(
                                        ft.icons.ARROW_LEFT,
                                        on_click=lambda _: page.go("/tasks"),
                                    ),
                                    ft.Text("Usuario: "),
                                    ft.Text(
                                        page.client_storage.get("user"), expand=True
                                    ),
                                    ft.FilledButton(
                                        "Cerrar sesión",
                                        on_click=lambda _: page.go("/login"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            )
                        ),
                        CategoryList(),
                    ],
                )
            )
        if page.route == "/tasks":
            page.views.clear()
            page.views.append(
                ft.View(
                    "/store",
                    [
                        ft.AppBar(
                            title=ft.Row(
                                [
                                    ft.Text("Usuario: "),
                                    ft.Text(
                                        page.client_storage.get("user"), expand=True
                                    ),
                                    ft.TextButton(
                                        "Administrar categorías",
                                        on_click=lambda _: page.go("/categories"),
                                    ),
                                    ft.FilledButton(
                                        "Cerrar sesión",
                                        on_click=lambda _: page.go("/login"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            )
                        ),
                        TaskList(),
                    ],
                )
            )
        page.update()

    def view_pop(*args, **kwargs):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.title = "Lista de tareas"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.update()
    if page.client_storage.contains_key("user"):
        page.go("/tasks")
    else:
        page.go("/login")


if __name__ == "__main__":
    ft.app(target=main, view=AppView.WEB_BROWSER)
