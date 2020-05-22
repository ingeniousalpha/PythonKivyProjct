from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.listview import ListItemButton
from kivy.uix.image import Image, AsyncImage
from kivy.uix.behaviors import ButtonBehavior, TouchRippleBehavior
from kivy.core.window import Window

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar

import requests
import socket
import time
import threading
import os

Window.size = (400, 711)

# -------------------- Global Variables --------------------

_url = 'https://art-styler-server.herokuapp.com/'
# _url = 'http://127.0.0.1:5000/'

# art_styler_dir = '\\storage\\emulated\\0\\art-styler\\'
art_styler_dir = 'C:\\users\\User\\desktop\\art-styler\\'


# -------------------- Classes --------------------

class TouchRippleEffect(TouchRippleBehavior):
    def __init__(self, **kwargs):
        super(TouchRippleEffect, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        collide_point = self.collide_point(touch.x, touch.y)
        if collide_point:
            touch.grab(self)
            self.ripple_show(touch)
            return True
        return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()
            return True
        return False


class FileMan(FileChooserListView):

    def image_selected(self): # HERE TO CHECK FOR FORMATS(PNG, JPG, etc)
        for w in self.walk_reverse():
            if isinstance(w, InputScreen):
                w.input_image_path = self.selection[0]
                w.show_selected_image()
        Snackbar(text="Image is selected!").show()


class DownloadableAsyncImage(TouchRippleEffect, ButtonBehavior, AsyncImage):
    image_size = []
    anchor_size = []

    def on_load(self, *args):
        self.set_norm_size()

    def set_norm_size(self):
        self.anchor_size = self.parent.parent.size
        self.image_size = self.norm_image_size

        self.parent.size_hint = [None, None]
        self.parent.size = self.image_size


class ClickableImage(TouchRippleEffect, ButtonBehavior, Image):
    image_size = []
    anchor_size = []

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()

            for w in self.walk_reverse():
                if isinstance(w, InputScreen):
                    w.input_image_path = ''
                    w.select_image(1)

            return True
        return False

    def set_norm_size(self):
        self.anchor_size = self.parent.parent.size
        self.image_size = self.norm_image_size

        if self.image_size[0] > self.image_size[1]:
            ratio = self.image_size[0] / self.anchor_size[0]
        else:
            ratio = self.image_size[1] / self.anchor_size[1]

        width = self.image_size[0] / ratio
        height = self.image_size[1] / ratio
        self.parent.size_hint = [None, None]
        self.parent.size = [width, height]


class InputScreen(Screen):
    chosen_style = ''
    input_image_path = ''

    top_section = ObjectProperty()
    inner_top_section = ObjectProperty()
    middle_section = ObjectProperty()
    bottom_section = ObjectProperty()

    style_list = ObjectProperty()
    file_manager = ObjectProperty()
    choose_img_btn = ObjectProperty()
    generate_btn = ObjectProperty()

    def select_image(self, snum):
        key = False

        # ANCHOR FOR CHOOSE BUTTON
        self.top_section.children[0].size_hint = (1, 1)
        self.inner_top_section.remove_widget(self.choose_img_btn)

        for obj in self.top_section.children:
            if obj.children:
                if isinstance(obj.children[0], ClickableImage) or isinstance(obj.children[0], AnchorLayout):
                    obj.remove_widget(obj.children[0])
            elif isinstance(obj, FileMan):
                key = True

        if snum == 1:
            if not key:
                self.top_section.add_widget(FileMan())
        elif snum == 2:
            if not key:
                self.inner_top_section.add_widget(self.choose_img_btn)

    def select_style(self):
        if self.style_list.adapter.selection:
            self.chosen_style = self.style_list.adapter.selection[0].text
            style = self.chosen_style.replace(' ', '_').lower()
            self.manager.get_screen('output_screen').chosen_style = style

        try:
            # checking for internet connection
            socket.create_connection(("www.google.com", 80))

            if self.input_image_path != '' and self.chosen_style != '':
                self.manager.get_screen('output_screen').input_image_path = self.input_image_path
                self.manager.get_screen('output_screen').input_img.children[0].source = self.input_image_path
                self.manager.transition.direction = "left"
                self.manager.current = 'output_screen'
                self.input_image_path = ''
                self.chosen_style = ''
            else:
                Snackbar(text='Select a picture and style').show()

        except OSError:
            Snackbar(text="There is no internet connection!").show()

    # CREATING IMAGE
    def show_selected_image(self):
        self.top_section.remove_widget(self.top_section.children[0])#removing FileMan()
        img = ClickableImage(size_hint=(1, 1), keep_ratio= True, mipmap= True, source=self.input_image_path)
        al = AnchorLayout()
        al.add_widget(img)
        self.top_section.children[0].add_widget(al)
        img.set_norm_size()


class OutputScreen(Screen):
    input_image_path = ''
    styled_image_path = ''
    output_image_path = ''
    chosen_style = ''
    ready = False

    input_img = ObjectProperty()
    styled_img = ObjectProperty()
    progressbar = ObjectProperty()
    nextgen_btn = ObjectProperty()

    def on_enter(self, *args):
        self.input_img.children[0].source = self.input_image_path
        x = self.input_img.children[0].norm_image_size[0]/self.progressbar.parent.size[0]
        self.progressbar.size_hint = x, 1
        self.progressbar.value = 0
        self.show_progress()
        self.send_request()

    def request(self):
        options = {'style': self.chosen_style}
        with open(self.input_image_path, 'rb') as f:
            resp = requests.post(_url, files={'input_image': f}, data=options)

        if not os.path.exists(art_styler_dir):
            os.mkdir(art_styler_dir)

        image_name = "styled-" + self.input_image_path.split('\\')[-1]
        styled_image_path = art_styler_dir + image_name

        flow = open(styled_image_path, 'wb')
        flow.write(resp.content)
        flow.close()

        self.styled_image_path = styled_image_path
        self.ready = True

    def send_request(self):
        threading.Thread(target=self.request).start()

        al = AnchorLayout()
        imga = DownloadableAsyncImage(keep_ratio=True, mipmap=True, source='http://asjdfjl')
        al.add_widget(imga)
        self.styled_img.add_widget(al)

    def on_leave(self, *args):
        self.styled_img.remove_widget(self.styled_img.children[0])
        self.ready = False

    def progress(self):
        step = 1
        while self.progressbar.value < 100:
            self.progressbar.value += step
            time.sleep(.2)
            if self.ready:
                step += 2

        self.styled_img.children[0].children[0].source = self.styled_image_path
        Snackbar(text="Image is downloaded!").show()

    def show_progress(self):
        threading.Thread(target=self.progress).start()


class MyButton(ListItemButton):
    pass


class WelcomeApp(App):
    theme_cls = ThemeManager()

    def build(self):
        self.theme_cls.theme_style = 'Dark'

        self.theme_cls.primary_palette = 'Blue'
        # 'Pink', 'Blue', 'Indigo', 'BlueGrey',
        # 'Brown', 'LightBlue', 'Purple', 'Grey',
        # 'Yellow', 'LightGreen', 'DeepOrange',
        # 'Green', 'Red', 'Teal', 'Orange', 'Cyan',
        # 'Amber', 'DeepPurple','Lime'

        self.theme_cls.accent_palette = 'Orange'
        # 'Pink', 'Blue', 'Indigo', 'LightBlue',
        # 'Purple', 'Yellow', 'LightGreen', 'Red',
        # 'DeepOrange', 'Green', 'Teal', 'Amber',
        # 'Orange', 'Cyan', 'DeepPurple','Lime'

        screen_manager = ScreenManager()
        screen_manager.add_widget(InputScreen(name='input_screen'))
        screen_manager.add_widget(OutputScreen(name='output_screen'))

        return screen_manager


# -------------------- Main --------------------

if __name__ in ('__main__', '__android__'):
    WelcomeApp().run()
