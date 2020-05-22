from kivy.app import App
from kivy.lang import Builder
from kivymd.theming import ThemeManager

Activity = ''' 
#: import MDFlatButton kivymd.button.MDFlatButton 

ScreenManager: 
    
    Screen: 
        name: 'Screen one'  # имя экрана
        
        AnchorLayout:
            BoxLayout:
                orientation: 'vertical'
                
                MDFlatButton: 
                    theme_text_color: 'Custom'
                    text_color: (0,0,1,1)
                    text: 'I`m Screen 1 with Button' 
                    size_hint: .5, .5 
                    on_release: 
                        root.transition.direction = "left"
                        root.current = 'Screen two'  # смена экрана

    Screen: 
        name: 'Screen two' 

        BoxLayout: 
            orientation: 'vertical' 

            Image: 
                source: 'data/logo/kivy-icon-128.png' 

            MDFlatButton: 
                text: 'I`m Screen 2 with Button' 
                size_hint: 1, 1 
                on_release: 
                    root.transition.direction = "right"
                    root.current = 'Screen one' 
'''

class Program(App):
    theme_cls = ThemeManager()
    theme_cls.theme_style = 'Dark'
    def build(self):
        return Builder.load_string(Activity)

if __name__ in ('__main__', '__android__'):
    Program().run()