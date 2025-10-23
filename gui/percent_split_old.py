from tkinter import *
from tkinter import ttk

class MainMenu:
    def __init__(self, root):
        root.title("NumUp - Main Menu")
        
        mainframe = ttk.Frame(root, padding="3 3 120 30")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        percent_split = ttk.Button(mainframe, text="Percent split", command=self.change_menu)
        percent_split.grid(column=0, row=0, sticky=(E, S))
        
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        percent_split.focus()
        
    def change_menu(self):
        PercentSplit(root)

class PercentSplit:
    def __init__(self, root):
        root.title("NumUp - Split by percent")

        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.num_to_split = StringVar()
        num_to_split_entry = ttk.Entry(self.mainframe, width=8, textvariable=self.num_to_split)
        num_to_split_entry.grid(column=1, row=0, sticky=(W, E))

        self.percent_split_by = StringVar()
        percent_split_by_entry = ttk.Entry(self.mainframe, width=8, textvariable=self.percent_split_by)
        percent_split_by_entry.grid(column=1, row=1, sticky=(W, E))

        ttk.Button(self.mainframe, text="Calculate", command=self.percent_calc).grid(column=2, row=2, sticky=E)

        self.num_split_output = StringVar()
        ttk.Label(self.mainframe, textvariable=self.num_split_output).grid(column=3, row=1, sticky=(W, E))

        ttk.Label(self.mainframe, text="Number to split:").grid(column=0, row=0, sticky=W)
        ttk.Label(self.mainframe, text="Percent to split by:").grid(column=0, row=1, sticky=W)
        ttk.Label(self.mainframe, text="Output:").grid(column=2, row=1, sticky=W)
        
        self.num_remainder = StringVar()
        self.remainder_label = ttk.Label(self.mainframe, text="Remainder:")
        self.remainder_label.grid(column=0, row=2, sticky=E)
        self.remainder_label_output = ttk.Label(self.mainframe, textvariable=self.num_remainder)
        self.remainder_label_output.grid(column=1, row=2, sticky=(W, E))
        
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
            
        self.remove_remainder()
        num_to_split_entry.focus()
        root.bind("<Return>", self.percent_calc)
        
    def remove_remainder(self):
        self.remainder_label.grid_remove()
        self.remainder_label_output.grid_remove()
        
    def create_remainder(self):
        self.remainder_label.grid()
        self.remainder_label_output.grid()

    def percent_calc(self, *args):
        try:
            value = float(self.num_to_split.get())
            percent_value = float(self.percent_split_by.get())
            final_value = int(percent_value * value * 10000.0 + 0.5)/10000.0
                        
            self.num_split_output.set(final_value)
            self.num_remainder.set(int((value - final_value) * 10000.0 + 0.5)/10000.0)
                        
            if (float(self.num_remainder.get()) == 0 or float(self.num_remainder.get()) == value):
                self.remove_remainder()
                # print("Remainder - " + str(self.num_remainder.get()) + " - is 0 or equal to " + str(value))
            else:
                self.create_remainder()
                # print("Remainder - " + str(self.num_remainder.get()) + " - is not 0 or equal to " + str(value))
        except ValueError:
            pass

if __name__ == "__main__":
    root = Tk()
    MainMenu(root)
    root.mainloop()