from kivymd.uix.label import MDLabel

try:
    from kivy.uix.boxlayout import BoxLayout
    from kivymd.app import MDApp

except Exception as ex:
    error = f"{ex.__class__.__name__}: {ex}"
else:
    error = ''


class MainApp(MDApp):
    def build(self):
        main_layout = BoxLayout(orientation="vertical")
        # self.theme_cls.theme_style = "Dark"
        # self.theme_cls.primary_palette = "Green"

        global error

        if not error:
            try:
                error = 'Success'
            except Exception as ex:
                error = f"{ex.__class__.__name__}: {ex}"

        main_layout.add_widget(MDLabel(text=error))

        return main_layout


if __name__ == "__main__":
    app = MainApp()
    app.run()
    # app.main_widget.db.close()
