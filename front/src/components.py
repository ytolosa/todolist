from datetime import date

import flet as ft


class DataPicker(ft.UserControl):
    def __init__(
        self, value=None, on_change=None, data=None, text_kwargs=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.text_kwargs = text_kwargs or {}
        self.data = data
        self.on_select = on_change
        self.value = value

    def build(self):
        def on_change(event):
            button.content.value = dp.value.date()
            self.value = dp.value.date()
            button.update()
            if self.on_select:
                self.on_select(event)

        if self.value is None:
            self.value = date.today()

        dp = ft.DatePicker(on_change=on_change, data=self.data)
        dp.value = self.value

        button = ft.TextButton(
            content=ft.Text(self.value.strftime("%Y-%m-%d"), **self.text_kwargs),
            on_click=lambda _: dp.pick_date(),
        )
        return ft.Row([button, dp])
