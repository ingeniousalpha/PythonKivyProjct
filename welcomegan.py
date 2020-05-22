from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooser
from kivymd.theming import ThemeManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from  kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.listview import ListItemButton, ListView
from kivy.adapters.listadapter import ListAdapter
from kivymd.grid import SmartTile
from kivy.uix.image import Image, AsyncImage
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior, TouchRippleBehavior
from kivymd.snackbar import Snackbar
from kivymd.button import MDFlatButton, MDRaisedButton
from kivymd.progressbar import MDProgressBar
import requests
import socket
import time
import threading
import os

Window.size = (400, 711)

# _url = 'https://art-styler-server.herokuapp.com:35470/'
_url = 'https://art-styler-server.herokuapp.com/'
# _url = 'http://127.0.0.1:5000/'

# art_styler_dir = '\\storage\\emulated\\0\\art-styler\\'
art_styler_dir = 'C:\\users\\User\\desktop\\art-styler\\'


# -------------------- Functions --------------------

# def show_selected_image():
#     InputScreen.top_section.remove_widget(InputScreen.top_section.children[0])
#     print(InputScreen.input_image_path)
#     img = Image(size_hint=(1, 1), mipmap=True, source=InputScreen.input_image_path)
#     InputScreen.top_section.add_widget(img)


# -------------------- Classes --------------------

class DownloadThread(threading.Thread):

    def run(self):
        resp = requests.get(_url+"/get_image")

        flow = open(art_styler_dir+'/respond_image.jpg', 'wb')
        flow.write(resp.content)
        flow.close()

        MySnack(text="Image is downloaded!").show()


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
            # super(TouchRippleEffect, self).on_touch_up(touch)
            return True
        return False


class FileMan(FileChooserListView):

    def image_selected(self): # HERE TO CHECK FOR FORMATS(PNG, JPG, etc)
        for w in self.walk_reverse():
            if isinstance(w, InputScreen):
                w.input_image_path = self.selection[0]
                w.show_selected_image()
        MySnack(text="Image is selected!").show()


class DownloadableAsyncImage(TouchRippleEffect, ButtonBehavior, AsyncImage):
    image_size = []
    anchor_size = []

    def on_load(self, *args):
        self.set_norm_size()

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()
            print("I want to download this image: ", self.norm_image_size)

            # if self.source != 'http://asjdfjl':
            #     download = DownloadThread(name='Downloading')
            #     download.start()

            return True
        return False

    def set_norm_size(self):
        self.anchor_size = self.parent.parent.size
        self.image_size = self.norm_image_size
        print("anchor size: ", self.anchor_size)
        print("image size: ", self.image_size)

        self.parent.size_hint = [None, None]
        self.parent.size = self.image_size


class ClickableAsyncImage(TouchRippleEffect, ButtonBehavior, AsyncImage):
    image_size = []
    anchor_size = []

    def on_load(self, *args):
        self.set_norm_size()

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()
            print("I want to download this image: ", self.norm_image_size)
            return True
        return False

    def set_norm_size(self):
        self.anchor_size = self.parent.parent.size
        self.image_size = self.norm_image_size
        print("anchor size: ", self.anchor_size)
        print("image size: ", self.image_size)

        if self.image_size[0] > self.image_size[1]:
            ratio = self.image_size[0] / self.anchor_size[0]
        else:
            ratio = self.image_size[1] / self.anchor_size[1]

        width = self.image_size[0] / ratio
        height = self.image_size[1] / ratio
        self.parent.size_hint = [None, None]
        self.parent.size = [width, height]


class ClickableImage(TouchRippleEffect, ButtonBehavior, Image):
    image_size = []
    anchor_size = []

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.ripple_fade()

            for w in self.walk_reverse():
                if isinstance(w, InputScreen):
                    w.select_image(1)

            print("calculated image size: ", self.image_size)

            return True
        return False

    def set_norm_size(self):
        self.anchor_size = self.parent.parent.size
        self.image_size = self.norm_image_size
        print("anchor size: ", self.anchor_size)
        print("image size: ", self.image_size)

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
    input_image_path = 'some_picture'

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
        # self.top_section = self.ids.top_section
        # self.middle_section = self.ids.middle_section
        # self.bottom_section = self.ids.bottom_section

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
            if key == False:
                self.inner_top_section.add_widget(self.choose_img_btn)


    def select_style(self):
        if self.style_list.adapter.selection:
            self.chosen_style = self.style_list.adapter.selection[0].text
            style = self.chosen_style.replace(' ', '_').lower()
            self.manager.get_screen('output_screen').chosen_style = style
            print(self.chosen_style)

        try:
            # connect to the host -- tells us if the host is actually
            # reachable
            socket.create_connection(("www.google.com", 80))
            self.manager.get_screen('output_screen').input_image_path = self.input_image_path
            # self.manager.get_screen('output_screen').input_img.children[0].source = self.input_image_path
            # self.manager.get_screen('output_screen').styled_img.source = self.input_image_path
            self.manager.transition.direction = "left"
            self.manager.current = 'output_screen'
        except OSError:
            Snackbar(text="There is no internet connection!").show()

    # CREATING IMAGE
    def show_selected_image(self):
        self.top_section.remove_widget(self.top_section.children[0])#removing FileMan()
        print(self.input_image_path)
        img = ClickableImage(size_hint=(1, 1), keep_ratio= True, mipmap= True, source=self.input_image_path)
        # img = ClickableAsyncImage(size_hint=(1, 1), keep_ratio= True, mipmap= True,
        #                      source= "https://theblueprint.ru/upload/10580/c8a9d614c39b9d3b19a61ccea32207a7_small.jpg")
        al = AnchorLayout()
        al.add_widget(img)
        self.top_section.children[0].add_widget(al)
        img.set_norm_size()


class OutputScreen(Screen):
    input_image_path = ''
    styled_image_path = ''
    output_image_path = ''
    chosen_style = ''
    progressbar_size = ()

    input_img = ObjectProperty()
    styled_img = ObjectProperty()
    progressbar = ObjectProperty()
    nextgen_btn = ObjectProperty()

    def on_pre_enter(self, *args):
        self.input_img.children[0].source = self.input_image_path
        self.progressbar.value = 0

    def on_enter(self, *args):

        x = self.input_img.children[0].norm_image_size[0]/self.progressbar.parent.size[0]
        self.progressbar_size = (x, 1)

        imga = DownloadableAsyncImage(size_hint=(1, 1), keep_ratio=True, mipmap=True, source='http://asjdfjl')
        al = AnchorLayout()
        al.add_widget(imga)
        self.styled_img.add_widget(al)

        # self.send_request()
        self.show_progress()
        self.request()
        # t1 = threading.Thread(target=self.request)
        # t2 = threading.Thread(target=self.progress)
        # t1.start()
        # t2.start()
        # t1.join()
        # t1.join()
        # t = threading.Thread(target=self.request).start()
        print('enter output_screen')

    def request(self):

        options = {'style': self.chosen_style}
        with open(self.input_image_path, 'rb') as f:
            resp = requests.post(_url, files={'input_image': f}, data=options)
        print("API response: ", resp)

        if not os.path.exists(art_styler_dir):
            os.mkdir(art_styler_dir)

        print(self.input_image_path.split('\\')[-1])
        image_name = "styled-" + self.input_image_path.split('\\')[-1]
        print(image_name)
        styled_image_path = art_styler_dir + image_name

        flow = open(styled_image_path, 'wb')
        flow.write(resp.content)
        flow.close()


        self.styled_image_path = styled_image_path
        MySnack(text="Image is downloaded!").show()
        return

    # def send_request(self):
    #     threading.Thread(target=self.request).start()

    def on_leave(self, *args):
        self.styled_img.remove_widget(self.styled_img.children[0])
        self.styled_image_path = ''
        print("leave output_screen")

    def progress(self):
        self.progressbar.size_hint = self.progressbar_size

        while True:
            if self.progressbar.value < 90:
                self.progressbar.value += 2
            if self.styled_image_path:
                self.progressbar.value = 100
                self.styled_img.children[0].children[0].source = self.styled_image_path
                break
            time.sleep(.3)
        return

    def show_progress(self):
        threading.Thread(target=self.progress).start()
        # t1 = threading.Thread(target=self.request)
        # t2 = threading.Thread(target=self.progress)
        # t1.start()
        # t2.start()
        # t1.join()
        # t1.join()

class MyButton(ListItemButton):
    pass


class MySnack(Snackbar):
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
