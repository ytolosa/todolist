import flet as ft
import httpx

from conf import BACK_URL
from models import CategoryModel


def get_categories(token) -> list[CategoryModel]:
    r = httpx.get(
        BACK_URL + "/categorias",
        headers={"Authorization": "Bearer " + token},
    )
    return [CategoryModel.parse_obj(c) for c in r.json()]


class Category(ft.UserControl):
    def __init__(self, category: CategoryModel, on_remove):
        super().__init__()
        self.on_remove = on_remove

        self.category = category

    def remove(self, event):
        token = self.page.client_storage.get("token")["access_token"]
        r = httpx.delete(
            f"{BACK_URL}/categorias/{self.category.id}",
            headers={"Authorization": "Bearer " + token},
        )

        if r.status_code == 401:
            self.page.go("/login")

        if self.on_remove:
            self.on_remove(self, error=r.status_code != 200)

    def build(self):
        self.name = ft.TextField(
            label="Nombre",
            value=self.category.name,
            border=ft.InputBorder.NONE,
        )

        self.description = ft.TextField(
            label="Descripción",
            value=self.category.description,
            expand=True,
            border=ft.InputBorder.NONE,
        )

        return ft.Container(
            ft.Row(
                [
                    self.name,
                    self.description,
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color=ft.colors.RED,
                        on_click=self.remove,
                    ),
                ]
            ),
            bgcolor=ft.colors.PRIMARY_CONTAINER,
            border_radius=5,
            margin=3,
            padding=10,
        )


class CategoryList(ft.UserControl):
    def add_category(self, event=None):
        token = self.page.client_storage.get("token")["access_token"]
        r = httpx.post(
            f"{BACK_URL}/categorias",
            json={
                "name": self.name.value,
                "description": self.description.value,
            },
            headers={"Authorization": "Bearer " + token},
        )

        if r.status_code == 401:
            self.page.go("/login")
        if r.status_code != 200:
            raise RuntimeError()

        category = CategoryModel.parse_obj(r.json())
        self.list.controls.append(Category(category, on_remove=self.remove_category))
        self.list.update()

    def close_banner(self, event):
        self.banner.open = False
        self.banner.update()

    def remove_category(self, control, error=False):
        if error:

            self.banner = ft.Banner(
                bgcolor=ft.colors.AMBER_100,
                leading=ft.Icon(
                    ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40
                ),
                content=ft.Text(
                    "No se puede eliminar una categoría que está siendo utilizada por una tarea",
                    color=ft.colors.BLACK,
                ),
                actions=[
                    ft.TextButton("Ok", on_click=self.close_banner),
                ],
                open=True,
            )

            self.result.controls.append(self.banner)
            self.result.update()
        else:
            self.list.controls.remove(control)
            self.list.update()

    def build(self):
        self.result = ft.Column()
        self.list = ft.ListView(padding=0)
        self.name = ft.TextField(
            label="Nombre",
            border=ft.InputBorder.NONE,
        )

        self.description = ft.TextField(
            label="Descripción",
            expand=True,
            border=ft.InputBorder.NONE,
        )

        self.result.controls.append(self.list)
        self.result.controls.append(
            ft.Container(
                ft.Row(
                    [
                        self.name,
                        self.description,
                        ft.IconButton(
                            icon=ft.icons.ADD,
                            icon_color=ft.colors.GREEN,
                            on_click=self.add_category,
                        ),
                    ]
                ),
                bgcolor=ft.colors.SECONDARY_CONTAINER,
                border_radius=5,
                margin=3,
                padding=10,
            )
        )
        return ft.Container(
            self.result,
            padding=10,
            margin=50,
            blur=10,
        )

    def did_mount(self):
        token = self.page.client_storage.get("token")["access_token"]
        for category in get_categories(token):
            self.list.controls.append(
                Category(category, on_remove=self.remove_category)
            )

        self.list.update()
