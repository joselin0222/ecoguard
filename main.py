from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.webview import WebView  # Si no existe, puedes usar Android WebView directamente

KV = '''
BoxLayout:
    orientation: 'vertical'
    WebView:
        url: 'http://192.168.100.12'  # ← Reemplaza con la IP de tu computadora
'''

class EcoGuardApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

EcoGuardApp().run()