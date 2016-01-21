import gi
import tester
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import threading
import time


class TestStore(Gtk.ListStore):
  def __init__(self):
    Gtk.ListStore.__init__(self, str, int, bool)
    self.tests = []
  def append(self, v):
    self.tests.append(tester.Test(v[0]))
    return Gtk.ListStore.append(self, v)

  def save_state(self, fn):
    with open(fn, 'wb') as f:
      pickle.dump((self.tests, list(self)), f)

  def load_state(self, fn):
    with open(fn, 'rb') as f:
      (self.tests, lself) = pickle.load(self.tests)
      self.clear()
      for r in lself:
        Gtk.ListStore.append(self, r)




class CellRendererProgressWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="CellRendererProgress Example")
        self.set_default_size(400, 300)

        self.liststore = TestStore()
        for i in range(10):
          self.liststore.append(["http://mirror.internode.on.net/pub/test/1meg.test", 0.0, False])
          #self.liststore.append(["", 0.0, False])

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
        box.add(treeview)
        box.add(hbox)
        hbox.add(self.testB)
        hbox.add(resetB)
        self.add(box)

        self.timeout_id = GObject.timeout_add(100, self.on_timeout, None)

        self.lock = threading.Lock()
        self.test_thread = None 
        self.count = 0

    def text_edited(self, widget, path, text):
      print("TEXT", text)
      self.liststore[path][0] = text
      self.tests[path].url = text


    def on_inverted_toggled(self, button, path):
      self.liststore[path][2] = not self.liststore[path][2]

    def start_new_test_thread(self):
      def run_tests():
        with self.lock:
          for l, t in zip(self.liststore, self.liststore.tests):
            if l[2]:
              t.test()

      if not self.test_thread:
        self.testB.set_sensitive(False)
        self.test_thread = threading.Thread(target=run_tests)
        self.test_thread.start()

    def test_now(self, button):
      self.start_new_test_thread()

      return True

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
      self.count += 1
      if self.count > (3600 * 10):
        self.start_new_test_thread()
        self.count = 0

      if self.test_thread: 
        if not self.test_thread.is_alive():
          self.test_thread.join()
          self.test_thread = None
          self.testB.set_sensitive(True)
      else:
        self.testB.set_sensitive(True)

      for l, t in zip(self.liststore, self.liststore.tests):
        l[1] = t.progress
      return True

GObject.threads_init()
win = CellRendererProgressWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
if win.test_thread:
  win.test_thread.join(1.0)
