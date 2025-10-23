import pathlib
import tkinter as tk
from tkinter import ttk

def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
    except ValueError:
        pass

icon_filepath = pathlib.Path(__file__).parent.resolve() / "icon.ico"

root = tk.Tk()
root.title("Feet to Meetor")
root.iconbitmap(icon_filepath)

mainframe = ttk.Frame(root, padding="6 6 12 12")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

feet = tk.StringVar()
feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(tk.W, tk.E))

meters = tk.StringVar()
ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(tk.W, tk.E))

ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=tk.W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=tk.W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=tk.E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=tk.W)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

feet_entry.focus()
root.bind("<Return>", calculate)

root.mainloop()