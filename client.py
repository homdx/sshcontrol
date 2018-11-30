import subprocess
import paramiko
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', 400)
Config.set('graphics', 'height', 500)


class PiControlApp(App):
    def build(self):

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = ""
        self.user = ""
        self.password  = ""
        self.history = ""
        self.output = ""

        btn_properties = [[0, 0, 1, 1], 30] #0-background 1-font size 

        top_grid = GridLayout ( cols = 2, spacing = 4, size_hint = [1, .06])
        pw_grid = GridLayout ( cols = 2, spacing = 4, size_hint = [1, .06])
        gl = GridLayout( cols = 2, spacing = 3, size_hint = [1, .76] )
        bl = BoxLayout( orientation = "vertical", padding = [10], spacing = 5 )

        #connection field
        self.lbl = Label(text = "You need to connect", size_hint = [.7, 1], text_size = (400 * .7 - 20, 500 * .07 - 20), halign = "left")
        top_grid.add_widget( self.lbl )

        self.conn_btn = Button(text = "connect", background_color = [1, 0, 0, 1], size_hint = [.3, 1], font_size = 20, on_press = self.connection_popup)
        top_grid.add_widget ( self.conn_btn )

        bl.add_widget( top_grid )

        #command field
        self.txt = TextInput( multiline = False, size_hint = [1, .06] )
        bl.add_widget( self.txt )

        #path field
        self.path_lbl = Label(text = "Path: ", size_hint = [1, .06], text_size = (400 - 20, 500 * .07 - 20), halign = "left")
        bl.add_widget(self.path_lbl)
        
        gl.add_widget( Button(text = "run"     , background_color = btn_properties[0], font_size = btn_properties[1], on_press = self.command_call) )
        gl.add_widget( Button(text = "output"  , background_color = btn_properties[0], font_size = btn_properties[1], on_press = self.show_output) )
        gl.add_widget( Button(text = "ls"      , background_color = btn_properties[0], font_size = btn_properties[1], on_press = self.run_ls) )
        gl.add_widget( Button(text = "pwd"     , background_color = btn_properties[0], font_size = btn_properties[1], on_press = self.get_path) )
        gl.add_widget( Button(text = ""        , background_color = btn_properties[0], font_size = btn_properties[1]) )
        gl.add_widget( Button(text = "hisory"  , background_color = btn_properties[0], font_size = btn_properties[1], on_press = self.show_history) )
        gl.add_widget( Button(text = "reboot"  , background_color = btn_properties[0], font_size = btn_properties[1], on_press = self.command_reboot) )
        gl.add_widget( Button(text = "shutdown", background_color = btn_properties[0], font_size = btn_properties[1], on_press = self.command_shutdown) )

        bl.add_widget( gl )

        return bl

    def command_call(self, instance):
        command = self.txt.text

        if ( len(command) == 0 ):
            self.lbl.text = "Command is wrong!"

        else:
            try:
                stdin, stdout, stderr = self.client.exec_command(command)
                self.output = stdout.read() + stderr.read()
                self.history += command + "\n"
            except:
                self.lbl.text = "Error"


            self.lbl.text = "Command completed!"
            self.txt.text = ''

    def connection_popup(self, instance):
        content = BoxLayout(orientation = "vertical", spacing = 5, size_hint = (.9, .9))

        self.adr_lbl = Label(text = "Enter adress", size_hint = [1, .1])
        content.add_widget( self.adr_lbl )

        self.adr_input = TextInput(multiline = False, size_hint = [1, .1])
        content.add_widget( self.adr_input )

        self.login_lbl = Label(text = "Enter login", size_hint = [1, .1])
        content.add_widget( self.login_lbl )

        self.login_input = TextInput(password = True, multiline = False, size_hint = [1, .1])
        content.add_widget( self.login_input) 

        self.pw_lbl = Label(text = "Enter password", size_hint = [1, .1])
        content.add_widget( self.pw_lbl )

        self.pw_input = TextInput(password = True, multiline = False, size_hint = [1, .1])
        content.add_widget( self.pw_input )

        content.add_widget( Button(text="connect", size_hint = [1, .1], on_press = self.connection) )

        self.msg_lbl = Label(text = "", size_hint = [1, .3])
        content.add_widget( self.msg_lbl )

        popup = Popup( title = "CONNECTION", content = content, size_hint=(.9, .9) )
        popup.open()

    def connection(self, instance):
        if self.adr_input.text != "" and self.pw_input.text != "":
            try:
                self.msg_lbl.text = "connecting..."
                self.client.connect(hostname = self.adr_input.text, username = self.login_input.text, password = self.pw_input.text, port = 22)
                self.lbl.text = "connected"
                self.conn_btn.background_color = [0, 1, 0, 1]
                self.get_path()
                self.host = self.adr_input.text
                self.user = self.login_input.text
                self.password = self.pw_input.text
                self.msg_lbl.text = "successfully connected\n" + self.user + "@" + self.host
            except:
                self.msg_lbl.text = "connection refused"

        elif self.adr_input.text == "":
                self.adr_lbl.text = "Adress is wrong!"
        elif self.pw_input.text == "":
                self.pw_lbl.text = "Password is wrong!"

    def show_output(self, instance):
        content = BoxLayout( orientation = "vertical", padding = [10], spacing = 5 )
        content.add_widget( Label(text = self.output, font_size = 13, text_size = ((400 - 30) * .9, (500 - 20) * .8), halign = "left", valign = "top") )
        popup = Popup( title = "OUTPUT", content = content, size_hint=(.9, .9) )
        popup.open()

    def run_ls(self, instance):
        try:
            stdin, stdout, stderr = self.client.exec_command('ls -l')
            popup = Popup( title = "Ls -l", content = Label(text = stdout.read(), font_size = 13, text_size = ((400 - 30) * .9, (500 - 20) * .8), halign = "left", valign = "top"), size_hint=(.9, .9) )
            popup.open()
        except:
            self.lbl.text = "Error"

    def show_history(self, instance):
        content = BoxLayout( orientation = "vertical", padding = [10], spacing = 5 )
        content.add_widget( Label(text = self.history, font_size = 13, text_size = ((400 - 30) * .9, (500 - 20) * .8), halign = "left", valign = "top") )
        popup = Popup( title = "HISTORY", content = content, size_hint=(.9, .9) )
        popup.open()

    def command_reboot(self, instance):
        try:
            stdin, stdout, stderr = self.client.exec_command('sudo reboot')
            self.output = stdout.read() + stderr.read()
        except:
            self.lbl.text = "Error"

    def command_shutdown(self, instance):
        try:
            stdin, stdout, stderr = self.client.exec_command('sudo shutdown now')
            self.output = stdout.read() + stderr.read()
        except:
            self.lbl.text = "Error"

    def get_path(self, instance):
        try:
            stdin, stdout, stderr = self.client.exec_command('pwd')
            self.path_lbl.text = 'Path: ' + stdout.read()[:-1]
        except:
            self.lbl.text = "Error"

if __name__ == "__main__":
    PiControlApp().run()