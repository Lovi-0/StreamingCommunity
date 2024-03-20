import gi
import os
import signal

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2, Gdk

class WebBrowser(Gtk.Window):
    whitelist = ["streamingcommunity", "vixcloud", "thaculse"]

    def __init__(self):
        Gtk.Window.__init__(self, title="StreamingCommunity")
        self.set_default_size(800, 600)

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = "StreamingCommunity"

        self.set_titlebar(headerbar)

        # Creiamo un box per contenere il WebView
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        self.webview = WebKit2.WebView()
        self.webview.connect("load-changed", self.on_load_changed)
        self.box.pack_start(self.webview, True, True, 0)  # Aggiungiamo il WebView al box
        self.load_url("https://streamingcommunity.report")
        self.connect("key-press-event", self.on_key_press)
        self.cookie_manager = self.webview.get_context().get_cookie_manager()
        self.load_cookies()

        # Aggiungiamo il bottone alla barra delle impostazioni
        button = Gtk.Button.new_with_label("Stampa URL del video")
        button.connect("clicked", self.print_video_url)
        headerbar.pack_end(button)

    def load_url(self, url):
        self.webview.load_uri(url)

    def on_load_changed(self, webview, event):
        if event == WebKit2.LoadEvent.FINISHED:
            current_uri = webview.get_uri()
            if not self.is_whitelisted(current_uri):
                print("Blocked:", current_uri)
                webview.go_back()

    @classmethod
    def is_whitelisted(cls, uri):
        domain = cls.get_domain(uri)
        return any(domain.endswith(allowed_domain) for allowed_domain in cls.whitelist)

    @staticmethod
    def get_domain(uri):
        return uri.split("//www.")[-1].split(".")[0]

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Left and event.state & Gdk.ModifierType.MOD1_MASK:
            self.webview.go_back()
            return True  

    def save_cookies(self):
        self.cookie_manager.save_cookies(".cookies.txt", None, None)

    def load_cookies(self):
        self.cookie_manager.set_persistent_storage(".cookies.txt", WebKit2.CookiePersistentStorage.TEXT)
        self.cookie_manager.set_accept_policy(WebKit2.CookieAcceptPolicy.ALWAYS)

    def print_video_url(self, widget):
        current_uri = self.webview.get_uri()
        print("URL attuale:", current_uri)

if __name__ == "__main__":
    win = WebBrowser()
    win.connect("destroy", Gtk.main_quit)
    signal.signal(signal.SIGINT, lambda sig, frame: win.save_cookies())
    win.show_all()
    Gtk.main()
