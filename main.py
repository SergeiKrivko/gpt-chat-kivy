from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp

from src import config
from src.chat import ChatPanel


class MainApp(MDApp):
    def build(self):
        main_layout = BoxLayout(orientation="vertical")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"

        self.title = config.APP_NAME

        self.main_widget = ChatPanel(self)
        main_layout.add_widget(self.main_widget)

        return main_layout


if __name__ == "__main__":
    app = MainApp()
    app.run()
    app.main_widget.db.close()
