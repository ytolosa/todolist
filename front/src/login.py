import flet as ft
import httpx
from flet_core import ControlEvent

from conf import BACK_URL


class Register(ft.UserControl):
    def build(self):
        self.username_input = ft.TextField(
            label="Nombre de usuario",
            prefix_icon=ft.icons.PERSON_OUTLINE,
            border=ft.InputBorder.UNDERLINE,
        )

        self.password_input = ft.TextField(
            password=True,
            label="Contraseña",
            prefix_icon=ft.icons.LOCK_OUTLINE,
            on_submit=lambda x: self.page.go("/register"),
            border=ft.InputBorder.UNDERLINE,
            can_reveal_password=True,
        )

        return ft.Container(
            width=400,
            bgcolor=ft.colors.PRIMARY_CONTAINER,
            padding=30,
            border_radius=10,
            content=ft.Column(
                [
                    ft.Text("Crear nuevo usuario:"),
                    self.username_input,
                    self.password_input,
                    ft.Row(
                        [
                            ft.ElevatedButton("Registrarse", on_click=self.register),
                            ft.FilledButton(
                                icon=ft.icons.ARROW_LEFT,
                                text="Volver",
                                on_click=lambda x: self.page.go("/login"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ]
            ),
        )

    def reset_color(self, event: ControlEvent):
        if event.control.error_text:
            event.control.error_text = None
            self.update()

    def register(self, e):
        ok = True
        self.username_input.error_text = ""
        self.password_input.error_text = ""
        if len(self.username_input.value) < 5:
            self.username_input.error_text = (
                "Ingrese un nombre de usuario de al menos 5 caracteres"
            )
            ok = False
        if len(self.password_input.value) < 5:
            self.password_input.error_text = (
                "Ingrese una contraseña de al menos 5 caracteres"
            )
            ok = False

        if not ok:
            self.update()
            return

        response = httpx.post(
            BACK_URL + "/usuarios",
            json={
                "username": self.username_input.value,
                "password": self.password_input.value,
            },
        )
        if response.status_code == 200:
            self.page.go("/login")
        else:
            self.username_input.error_text = response.text
            self.username_input.update()


class Login(ft.UserControl):
    def __init__(self, on_login):
        super().__init__()
        self.on_login = on_login

    def build(self):
        self.username_input = ft.TextField(
            label="Nombre de usuario",
            prefix_icon=ft.icons.PERSON_OUTLINE,
            border=ft.InputBorder.UNDERLINE,
        )
        self.password_input = ft.TextField(
            password=True,
            label="Contraseña",
            prefix_icon=ft.icons.LOCK_OUTLINE,
            on_submit=self.login,
            border=ft.InputBorder.UNDERLINE,
            can_reveal_password=True,
        )

        return ft.Container(
            width=400,
            bgcolor=ft.colors.PRIMARY_CONTAINER,
            padding=30,
            border_radius=10,
            content=ft.Column(
                spacing=25,
                controls=[
                    self.username_input,
                    self.password_input,
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                text="Entrar",
                                on_click=self.login,
                            ),
                            ft.TextButton(
                                text="Registrarse",
                                on_click=lambda x: self.page.go("/register"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
            ),
        )

    def login(self, e):
        response = httpx.post(
            BACK_URL + "/usuarios/iniciar-sesion",
            data={
                "username": self.username_input.value,
                "password": self.password_input.value,
            },
        )
        if response.status_code != 200:
            self.username_input.error_text = ""
            self.password_input.error_text = (
                "Nombre de usuario o contraseña incorrectos"
            )
            self.update()
        else:
            self.page.client_storage.set("token", response.json())
            self.page.client_storage.set("user", self.username_input.value)
            self.update()
            self.on_login()
