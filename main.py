from kivymd.uix.label import MDLabel

from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp


class MainApp(MDApp):
    def build(self):
        main_layout = BoxLayout(orientation="vertical")
        # self.theme_cls.theme_style = "Dark"
        # self.theme_cls.primary_palette = "Green"

        main_layout.add_widget(MDLabel(text='Hello World'))

        return main_layout


if __name__ == "__main__":
    app = MainApp()
    app.run()
    # app.main_widget.db.close()
