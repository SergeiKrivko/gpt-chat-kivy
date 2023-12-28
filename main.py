from kivymd.uix.label import MDLabel

try:
    from kivy.uix.boxlayout import BoxLayout
    from kivymd.app import MDApp
    from kivy.core.window import Window
    Window.fullscreen = False
    Window.softinput_mode = 'resize'

    from src import config
    from src.chat import ChatPanel
except Exception as ex:
    error = f"{ex.__class__.__name__}: {ex}"
else:
    error = ''


class MainApp(MDApp):
    def build(self):
        main_layout = BoxLayout(orientation="vertical")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"

        self.title = config.APP_NAME

        global error

        if not error:
            try:
                self.main_widget = ChatPanel(self)
            except Exception as ex:
                error = f"{ex.__class__.__name__}: {ex}"

        if error:
            main_layout.add_widget(MDLabel(text=error))
        else:
            main_layout.add_widget(self.main_widget)

        return main_layout


if __name__ == "__main__":
    app = MainApp()
    app.run()
    app.main_widget.db.close()
