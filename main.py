import asyncio

try:
    from kivy.uix.boxlayout import BoxLayout
    from kivymd.app import MDApp
    import kivy
    from kivymd.uix.label import MDLabel

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
        self.title = config.APP_NAME

        global error

        if not error:
            try:
                self.main_widget = ChatPanel(self)
            except Exception as ex:
                error = f"{ex.__class__.__name__}: {ex}"

        if error:
            main_layout.add_widget(MDLabel(text=error + f"\n\nKivy version: {kivy._version.__version__}"))
        else:
            main_layout.add_widget(self.main_widget)

        return main_layout


def update_viewport(self=Window):
    from kivy.graphics.opengl import glViewport
    from kivy.graphics.transformation import Matrix
    from math import radians

    w, h = self.system_size
    if self._density != 1:
        w, h = self.size

    smode = self.softinput_mode
    target = self._system_keyboard.target
    targettop = max(0, target.to_window(0, target.y)[1]) if target else 0
    kheight = self.keyboard_height

    w2, h2 = w / 2., h / 2.
    r = radians(self.rotation)

    x, y = 0, 0
    _h = h
    if smode == 'pan':
        y = kheight
    elif smode == 'below_target':
        y = 0 if kheight < targettop else (kheight - targettop)
    if smode == 'scale':
        _h -= kheight
    if smode == 'resize':
        y += kheight
    # prepare the viewport
    glViewport(x, y, w, _h)

    # do projection matrix
    projection_mat = Matrix()
    projection_mat.view_clip(0.0, w, 0.0, h, -1.0, 1.0, 0)
    self.render_context['projection_mat'] = projection_mat

    # do modelview matrix
    modelview_mat = Matrix().translate(w2, h2, 0)
    modelview_mat = modelview_mat.multiply(Matrix().rotate(r, 0, 0, 1))

    w, h = self.size
    w2, h2 = w / 2., h / 2.
    modelview_mat = modelview_mat.multiply(Matrix().translate(-w2, -h2, 0))
    self.render_context['modelview_mat'] = modelview_mat
    frag_modelview_mat = Matrix()
    frag_modelview_mat.set(flat=modelview_mat.get())
    self.render_context['frag_modelview_mat'] = frag_modelview_mat

    # redraw canvas
    self.canvas.ask_update()

    # and update childs
    self.update_childsize()


async def main():
    app = MainApp()
    Window.update_viewport = update_viewport
    await app.async_run(async_lib='asyncio')
    app.main_widget.db.close()


if __name__ == "__main__":
    asyncio.run(main())
