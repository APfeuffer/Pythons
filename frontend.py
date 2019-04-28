import kivy
kivy.require("1.9.0")

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
files = ["gui.kv", "host.kv", "join.kv"]
Builder.load_string("\n".join([open(f,"r").read() for f in files]))

class ScreenGui(Screen):
    pass
class ScreenHost(Screen):
    pass
class ScreenJoin(Screen):
    pass

screen_manager = ScreenManager()
screen_manager.add_widget(ScreenGui(name="screen_gui"))
screen_manager.add_widget(ScreenHost(name="screen_host"))
screen_manager.add_widget(ScreenJoin(name="screen_join"))


"""
class GuiLayout(GridLayout):
    checkbox = ObjectProperty()
    name = ObjectProperty()
    ip = ObjectProperty()
    test = ObjectProperty()

    def jump(self):
        print(self.test.text)
    
"""            
class GuiApp(App):
    def build(self):
        return screen_manager


gui = GuiApp()
#print(gui.__dict__)
gui.run()
