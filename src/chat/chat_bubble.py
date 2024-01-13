from typing import Union

from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.behaviors import StencilBehavior, TouchBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu

from src.gpt.message import GPTMessage


class ChatBubble(MDBoxLayout, StencilBehavior, TouchBehavior):
    def __init__(self, app: MDApp, temp_dir, message: GPTMessage):
        super(MDBoxLayout, self).__init__(orientation='vertical')
        super(StencilBehavior, self).__init__()
        super(TouchBehavior, self).__init__()
        self.message = message
        self.app = app
        self.side = 'right' if message.role == 'user' else 'left'
        self._lines = message.content.split('\n')
        self._current_line = -1
        self.adaptive_height = True
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_x = 0.8
        if self.side == 'right':
            self.md_bg_color = self.app.theme_cls.primary_dark if self.app.theme_cls.theme_style == 'Dark' else \
                self.app.theme_cls.primary_light
        else:
            self.md_bg_color = self.app.theme_cls.bg_light if self.app.theme_cls.theme_style == 'Dark' else \
                self.app.theme_cls.bg_darkest
        self.radius = (dp(10), dp(10), 0 if self.side == 'right' else dp(10), 0 if self.side == 'left' else dp(10))
        self.pos_hint = {'center_x': 0.4 if self.side == 'left' else 0.6}

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                'text': f"Item {i}",
                # 'icon': 'delete',
                'on_release': lambda x=f"Item {i}": print(x),
                # 'height': dp(42),
            } for i in range(5)
        ]
        self.menu = MDDropdownMenu(caller=self, width_mult=4, items=menu_items)

        self._last_items = dict()
        self._apply_text()

    def on_long_touch(self, *args):
        self.menu.open()

    def _next_line(self) -> Union[str, None]:
        self._current_line += 1
        if self._current_line >= len(self._lines):
            return None
        return self._lines[self._current_line]

    def _return_line(self):
        self._current_line -= 1

    def _have_lines(self):
        return self._current_line < len(self._lines) - 1

    def _apply_text(self):
        while (line := self._next_line()) is not None:
            # if self.parse_image(line):
            #     continue
            if self.parse_code(line):
                continue
            if self._parse_header(line):
                continue
            if self.parse_list(line):
                continue
            # if self.parse_formula(line):
            #     continue
            if self._parse_paragraph(line):
                continue

    def _parse_paragraph(self, line: str):
        if not line.strip():
            return False

        text = [line.strip()]

        while (line := self._next_line()) is not None and line.strip():
            if line.lstrip().startswith('- ') or line.lstrip(' 1234567890').startswith('.') or \
                    line.lstrip().startswith('#'):
                self._return_line()
                break
            text.append(line.strip())

        label = MDLabel(text=' '.join(text), markup=True, adaptive_height=True)
        self.add_widget(label)

        return True

    def _parse_header(self, line):
        if not line.startswith('#'):
            return False
        text, level = line.lstrip('#').strip(), _count_in_start(line, '#')

        label = MDLabel(text=f'[size=20sp]{text}[/size]', markup=True, adaptive_height=True)
        self.add_widget(label)

        return True

    def parse_list(self, line: str):
        if not line.strip().startswith('- ') and not line.strip().lstrip('1234567890').startswith('. ') or \
                line.strip().startswith('.'):
            return False

        new = line.strip().startswith('1.')
        text = [line.strip().lstrip('1234567890-.').lstrip()]
        num = not line.strip().startswith('- ')
        margin = _count_in_start(line, ' ') // 3

        while (line := self._next_line()) is not None and line.strip():
            if line.strip().startswith('- ') or line.strip().lstrip('1234567890').startswith('.') and \
                    not line.strip().startswith('.') or line.startswith('```'):
                self._add_list_item(' '.join(text), num, new, margin)

                text.clear()
                new = line.strip().startswith('1.')
                num = not line.strip().startswith('- ')
                margin = _count_in_start(line, ' ') // 3

                line = line.strip().lstrip('1234567890-.').lstrip()

            text.append(line.strip())

        self._add_list_item(' '.join(text), num, new, margin)

        self._return_line()
        return True

    def _add_list_item(self, text, num=False, new_list=False, level=0):
        if num:
            index = self._last_items.get(level, None)
            if new_list or index is None:
                index = 0
            index += 1
            mark = str(index) + '.'
            self._last_items[level] = index
        else:
            mark = '•'
            self._last_items[level] = None

        layout = MDBoxLayout(adaptive_height=True, padding=(dp(20) * level, 0, 0, 0))
        self.add_widget(layout)

        v_layout = MDBoxLayout(orientation='vertical', size_hint_x=None, width=dp(30))
        layout.add_widget(v_layout)

        mark_label = MDLabel(text=mark, size_hint_x=None, width=dp(30))
        mark_label.adaptive_height = True
        v_layout.add_widget(mark_label)

        v_layout.add_widget(Widget(size_hint_x=None, width=dp(30)))

        label = MDLabel(text=text, adaptive_height=True)
        layout.add_widget(label)

    def parse_formula(self, line):
        if line.startswith('[formula-start]: <>'):
            lines = []
            while (line := self._next_line()) is not None and not line.startswith('[formula-end]: <>'):
                lines.append(line)
            self.convert_formula('\n'.join(lines))
            return True
        return False

    def parse_simple_formula(self, line, paragraph=None):
        if line.startswith('[formula]: <> ('):
            self.convert_formula(line[len('[formula]: <> ('):-1], paragraph)
            return True
        return False

    # def parse_image(self, line):
    #     if not re.match(r"!\[[\w.=\\/:]*]\([\w.\\/:]+\)", line.strip()):
    #         return False
    #     default_text, image_path = line.strip()[2:line.index(')')].split('](')
    #     if image_path.endswith('.svg'):
    #         svg2png(url=image_path, write_to=(image_path := f"{self.bm.sm.temp_dir()}/image.png"))
    #     img = Image.open(image_path)
    #     height, width = img.height, img.width
    #     if default_text.startswith('height='):
    #         h = int(default_text.lstrip('height='))
    #         width = width * h // height
    #         height = h
    #     elif default_text.startswith('width='):
    #         w = int(default_text.lstrip('width='))
    #         height = height * w // width
    #         width = w
    #     elif width > 170:
    #         height = height * 170 // width
    #         width = 170
    #     img.close()
    #     try:
    #         self.document.add_picture(image_path, width=Mm(width), height=Mm(height))
    #     except Exception:
    #         self.document.add_paragraph(default_text)
    #     return True

    def parse_code(self, line):
        if not line.startswith('```'):
            return False
        lexer = line.lstrip('```').strip()
        code_lines = []
        while (line := self._next_line()) is not None and not line.endswith('```'):
            code_lines.append(line)

        label = _CodeBox(self.app, self.side, '\n'.join(code_lines))
        self.add_widget(label)

        return True


def _count_in_start(line, symbol):
    return len(line) - len(line.lstrip(symbol))


class _CodeBox(MDLabel, StencilBehavior):
    def __init__(self, app: MDApp, side, code: str):
        super().__init__()
        self.code = code

        self.text = code
        self.padding = dp(8)
        self.adaptive_height = True
        self.font_name = 'C:\\Windows\\Fonts\\consola.ttf'
        self.radius = dp(10)
        self.line_color = app.theme_cls.primary_color
        self.line_width = 1
        self.line_height = 1
