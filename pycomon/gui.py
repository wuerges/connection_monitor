import gi
from pycomon.tester import Test
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import threading
import time
import csv


class TestStore(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, str, int, bool)
        self.tests = []
  
    def append(self, v):
        t = Test(v[0])
        self.tests.append(t)
        return Gtk.ListStore.append(self, v)

    def modify(self, path, text):
        self[int(path)][0] = text
        self.tests[int(path)].url = text

    def reset(self):
        self.tests = []
        self.clear()
        for i in range(10):
            #self.liststore.append(["http://mirror.internode.on.net/pub/test/1meg.test", 0.0, False])
            self.append(["                                                                          ", 0.0, False])

    def save_state(self, fn):
        with open(fn, 'wb') as f:
            pickle.dump((self.tests, list(self)), f)

    def load_state(self, fn):
        with open(fn, 'rb') as f:
            (self.tests, lself) = pickle.load(self.tests)
            self.clear()
            for r in lself:
                Gtk.ListStore.append(self, r)

class StatusIconManager:
    def __init__(self, win):
        self.win = win
        self.active = True

        self.icon = Gtk.StatusIcon()

        import os.path
        icon_location = os.path.join(os.path.dirname(__file__), '..', 'imgs', 'icon.png')

        self.icon.set_from_file(icon_location)

        self.icon.set_title("Connection Monitor")
        self.icon.set_title("connectionmonitor")
        self.icon.set_tooltip_text("pycomon")
        self.icon.set_has_tooltip(True)
        self.icon.set_visible(True)
        self.icon.connect("activate", self.status_icon_activate )

    def status_icon_activate(self, icon):
        if self.active:
            self.win.hide()
        else:
            self.win.show()
        self.active = not self.active

class CellRendererProgressWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Connection Monitor")
        self.set_default_size(400, 300)

        self.liststore = TestStore()
        self.liststore.reset()

        treeview = Gtk.TreeView(model=self.liststore)

        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("editable", True)
        renderer_text.connect("edited", self.text_edited)

        column_text = Gtk.TreeViewColumn("URL", renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_progress = Gtk.CellRendererProgress()
        column_progress = Gtk.TreeViewColumn("Progress", renderer_progress,
            value=1)
        treeview.append_column(column_progress)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_inverted_toggled)
        column_toggle = Gtk.TreeViewColumn("Enabled", renderer_toggle,
            active=2)
        treeview.append_column(column_toggle)

        box  = Gtk.Box(orientation=1, spacing=6)
        hbox = Gtk.Box(orientation=0, spacing=6)

        self.testB  = Gtk.Button.new_with_label("Test Now!")
        self.testB.connect("clicked", self.test_now)

        resetB = Gtk.Button.new_with_label("Reset")
        resetB.connect("clicked", self.reset_now)
        
        resultB = Gtk.Button.new_with_label("Save Results")
        resultB.connect("clicked", self.show_results_now)

        box.add(treeview)
        box.add(hbox)
        hbox.add(self.testB)
        hbox.add(resetB)
        hbox.add(resultB)
        self.add(box)

        self.lock = threading.Lock()
        self.test_thread = None 
        
        GObject.timeout_add(3600 * 1000, self.hourly_timeout, None)

    def show_results_now(self, button):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name("Untitled.csv")
        
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self.write_csv(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def reset_now(self, button):
        self.liststore.reset()
        if self.test_thread:
          self.test_thread.join(0.0)
        self.update_progress_bars()

    def text_edited(self, widget, path, text):
        self.liststore.modify(path, text)

    def on_inverted_toggled(self, button, path):
        self.liststore[path][2] = not self.liststore[path][2]

    def start_new_test_thread(self):
        """
        performs the tests
        and setups the update bars timeout
        """
        GObject.timeout_add(100, self.on_timeout, None)
        def run_tests():
            with self.lock:
                for l, t in zip(self.liststore, self.liststore.tests):
                    if l[2]:
                        t.test()
                for l, t in zip(self.liststore, self.liststore.tests):
                    if l[2]:
                        print(t.results)
               
        if not self.test_thread:
            self.test_thread = threading.Thread(target=run_tests)
            self.test_thread.start()

    def test_now(self, button):
        self.testB.set_sensitive(False)
        self.start_new_test_thread()
        return True

    def update_progress_bars(self):
        for l, t in zip(self.liststore, self.liststore.tests):
            l[1] = t.progress

    def hourly_timeout(self, user_data):
        self.start_new_test_thread()

    def write_csv(self, filename):
        with open(filename, 'w') as f:
            w = csv.writer(f)
            for t in self.liststore.tests:
                w.writerows(t.result_lines())

    def save_state(self, filename):
        self.liststore.save_state(filename)

    def load_state(self, filename):
        self.liststore.load_state(filename)

    def on_timeout(self, user_data):
        """ 
        Updates progress bars and makes the button
        sensitive once there is not a thread running anymore
        """
        self.update_progress_bars()
       
        if self.test_thread: 
            if self.test_thread.is_alive():
                self.testB.set_sensitive(False)
            else:
                self.test_thread.join()
                self.test_thread = None
                self.testB.set_sensitive(True)
                return False
        else:
            self.testB.set_sensitive(True)
            return False
       
        return True

def main():
    GObject.threads_init()
    win = CellRendererProgressWindow()
    icon = StatusIconManager(win)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    if win.test_thread:
        win.test_thread.join(0.0)

