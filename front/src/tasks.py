from datetime import date, datetime

import flet as ft
import httpx

from components import DataPicker
from conf import BACK_URL
from models import TaskModel, CategoryModel
from categories import get_categories

STATUS = {"Sin iniciar": 1, "Iniciada": 2, "Finalizada": 3}


class Task(ft.UserControl):
    categories: list[CategoryModel] = []

    def __init__(self, task: TaskModel, on_remove=None):
        super().__init__()
        self.on_remove = on_remove
        self.task = task

    def on_change(self, event: ft.ControlEvent):
        setattr(self.task, event.control.data, event.control.value)
        token = self.page.client_storage.get("token")["access_token"]

        if type(event.control.value) is datetime:
            value = event.control.value.date().isoformat()
        else:
            value = event.control.value
        r = httpx.put(
            f"{BACK_URL}/tareas/{self.task.id}",
            json={event.control.data: value},
            headers={"Authorization": "Bearer " + token},
        )

        if r.status_code == 401:
            self.page.go("/login")

        if event.control.data == "state":
            self.change_status()

    def change_status(self):
        match int(self.task.state):
            case 1:
                self.icon.icon_color = ft.colors.GREY
                self.icon.icon = ft.icons.BEDTIME_OUTLINED
            case 2:
                self.icon.icon_color = ft.colors.ORANGE
                self.icon.icon = ft.icons.RUN_CIRCLE_OUTLINED
            case 3:
                self.icon.icon_color = ft.colors.GREEN
                self.icon.icon = ft.icons.CHECK
        self.state.value = int(self.task.state)
        if self.page is not None:
            self.icon.update()
            self.state.update()

    def rotate_status(self, event=None):
        state = int(self.task.state) + 1
        if state > 3:
            state = 1
        self.task.state = state
        self.change_status()

    def delete(self, event: ft.ControlEvent):
        token = self.page.client_storage.get("token")["access_token"]
        r = httpx.delete(
            f"{BACK_URL}/tareas/{self.task.id}",
            headers={"Authorization": "Bearer " + token},
        )

        if r.status_code == 401:
            self.page.go("/login")

        if r.status_code != 200:
            raise RuntimeError()
        if self.on_remove:
            self.on_remove(self)

    def build(self):
        result = ft.Column()
        self.text = ft.TextField(
            data="text",
            value=self.task.text,
            on_change=self.on_change,
            border=ft.InputBorder.NONE,
            dense=True,
            content_padding=5,
            capitalization=ft.TextCapitalization.SENTENCES,
            expand=True,
        )

        self.category = ft.Dropdown(
            data="category_id",
            options=[
                ft.dropdown.Option(category.id, category.name)
                for category in self.categories
            ],
            on_change=self.on_change,
            expand=1,
            content_padding=5,
            dense=True,
            border=ft.InputBorder.NONE,
            text_size=13,
            color=ft.colors.SECONDARY,
        )

        self.category.value = self.task.category_id
        self.state = ft.Dropdown(
            data="state",
            # label="Estado",
            options=[ft.dropdown.Option(key=v, text=k) for k, v in STATUS.items()],
            on_change=self.on_change,
            expand=1,
            content_padding=5,
            dense=True,
            border=ft.InputBorder.NONE,
            text_size=13,
            color=ft.colors.SECONDARY,
        )

        self.state.value = self.task.state

        self.end_date = DataPicker(
            data="end_planned_date",
            value=self.task.end_planned_date,
            on_change=self.on_change,
            expand=1,
            text_kwargs=dict(size=13, color=ft.colors.SECONDARY),
        )

        self.icon = ft.IconButton(on_click=self.rotate_status)
        self.change_status()

        result.controls = [
            ft.Container(
                ft.Column(
                    [
                        ft.Row([self.text, self.icon]),
                        ft.Row(
                            [
                                self.state,
                                self.category,
                                self.end_date,
                                ft.IconButton(ft.icons.DELETE, on_click=self.delete),
                            ]
                        ),
                    ],
                    spacing=0
                ),
                bgcolor=ft.colors.PRIMARY_CONTAINER,
                border_radius=5,
                margin=3,
                padding=10,
            ),
        ]

        return result


class TaskCreator(ft.UserControl):
    def __init__(self, on_create=None):
        super().__init__()
        self.on_create = on_create
        self.categories = {}

    def open(self, event=None):
        self.dialog.open = True
        self.dialog.update()

    def close(self, event=None):
        self.dialog.open = False
        self.dialog.update()

    def on_dismiss(self, event=None):
        self.name.value = ""
        self.end_date.value = date.today()
        self.category.value = self.category.options[0].key
        self.status.value = 1

    def create_task(self, event=None):
        if not self.name.value:
            self.name.error_text = "Debe incluir un nombre"
            self.update()
            return

        data = {
            "text": self.name.value,
            "end_planned_date": str(self.end_date.value),
            "state": int(self.status.value),
            "category_id": self.categories[self.category.value],
        }

        r = httpx.post(
            BACK_URL + "/tareas",
            json=data,
            headers={
                "Authorization": "Bearer "
                + self.page.client_storage.get("token")["access_token"]
            },
        )
        if r.status_code == 401:
            self.page.go("/login")

        if r.status_code != 200:
            raise RuntimeError("Error")

        self.dialog.open = False
        self.on_dismiss()
        self.dialog.update()
        self.on_create(TaskModel.parse_obj(r.json()))

    def build(self):
        self.name = ft.TextField(label="Tarea", on_submit=self.create_task)
        self.end_date = DataPicker()
        self.category = ft.Dropdown(label="Categoría")
        self.status = ft.Dropdown(
            label="Estado",
            options=[ft.dropdown.Option(key=v, text=k) for k, v in STATUS.items()],
        )
        self.status.value = 1
        self.create = ft.ElevatedButton("Crear Tarea", on_click=self.create_task)
        self.cancel = ft.ElevatedButton("Cancelar", color="red", on_click=self.close)

        self.dialog = ft.AlertDialog(
            content=ft.Container(
                ft.Column(
                    [
                        self.name,
                        self.category,
                        self.status,
                        ft.Row([ft.Text("Fecha de finalización: "), self.end_date]),
                    ],
                    spacing=25,
                ),
                height=300,
            ),
            modal=True,
            on_dismiss=self.on_dismiss,
            title=ft.Text("Nueva tarea"),
            actions=[self.create, self.cancel],
        )
        return self.dialog

    def did_mount(self):
        token = self.page.client_storage.get("token")["access_token"]
        self.categories = {
            category.name: category.id for category in get_categories(token)
        }

        self.category.options = [
            ft.dropdown.Option(category) for category in self.categories
        ]

        self.category.value = self.category.options[0].key
        self.update()


class TaskList(ft.UserControl):
    def add_task(self, task: TaskModel):
        self.task_list.controls.append(Task(task, on_remove=self.remove_task))
        self.task_list.update()

    def remove_task(self, control):
        self.task_list.controls.remove(control)
        self.task_list.update()

    def build(self):
        self.result = ft.Column()
        self.task_list = ft.ListView()

        self.task_creator = TaskCreator(on_create=self.add_task)
        self.result.controls.append(self.task_creator)
        self.result.controls.append(
            ft.ElevatedButton("Agregar", on_click=self.task_creator.open)
        )
        self.result.controls.append(self.task_list)
        return ft.Container(
            self.result,
            padding=10,
            margin=50,
            blur=10,
        )

    def did_mount(self):
        token = self.page.client_storage.get("token")["access_token"]
        r = httpx.get(
            f"{BACK_URL}/tareas",
            headers={"Authorization": "Bearer " + token},
        )

        if r.status_code == 401:
            self.page.go("/login")

        tasks = r.json()

        Task.categories = get_categories(token)
        for task in tasks:
            task = TaskModel.parse_obj(task)
            self.task_list.controls.append(Task(task, on_remove=self.remove_task))

        self.task_list.update()
