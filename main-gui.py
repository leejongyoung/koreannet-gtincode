import tkinter as tk
import pyperclip
from koreannet.gtin import Search

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="Please enter the GTIN (Product Barcode) number)", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._set_placeholder)
        self._set_placeholder()

    def _clear_placeholder(self, event):
        if self["fg"] == self.placeholder_color:
            self.delete(0, tk.END)
            self["fg"] = self.default_fg_color

    def _set_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self["fg"] = self.placeholder_color


class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("GTIN Code Search")
        self.window.geometry("400x200")

        self.gtin_label = tk.Label(self.window, text="Please enter the GTIN (Product Barcode) number")
        self.gtin_label.pack(pady=10)

        self.gtin_entry = EntryWithPlaceholder(self.window, width=30, placeholder="8801043056489")
        self.gtin_entry.pack(pady=10)

        self.buttons_frame = tk.Frame(self.window)
        self.buttons_frame.pack()

        self.paste_button = tk.Button(self.buttons_frame, text="Paste from clipboard", command=self.paste)
        self.paste_button.pack(side=tk.LEFT, padx=10)

        self.search_button = tk.Button(self.buttons_frame, text="Search", command=self.search)
        self.search_button.pack(side=tk.LEFT, padx=10)

        self.result_label = tk.Label(self.window, text="")
        self.result_label.pack(pady=10)

    def search(self):
        gtin_num = self.gtin_entry.get()
        koreannet = Search(gtin_num)
        result = koreannet.search_gtin()

        if result["product_name"]:
            self.result_label.configure(text="GTIN code: " + result["gtin_code"] + "\nProduct name: " + result["product_name"])
        else:
            self.result_label.configure(text=result["message"])

    def paste(self):
        clipboard_text = pyperclip.paste()
        self.gtin_entry.delete(0, tk.END)
        self.gtin_entry.insert(0, clipboard_text)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = GUI()
    gui.run()
