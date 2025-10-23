from tkinter import *
from tkinter import ttk

class MenuHandler:
    '''
    General menu handler, takes takes root, menu, and arg1 and directs to target menu.
    
    arg1="" becomes optional since it technically has a default value (nothing).
    This means it only needs to be passed for Menus that need an additional arg.
    Useful for passing info to other menus without touching a global var.
    '''
    def change_menu(root, menu, arg1="", event=None): 
        match menu:
            case 0:
                MainMenu(root)
            case 1:
                PercentSplitMenu(root, arg1)
            case _: # <- Catch all just sends to HelpMenu
                HelpMenu(root)

class MainMenu:
    def __init__(self, root):
        root.title("NumUp - Main Menu")
        root.geometry("320x100")
        
        mainframe = ttk.Frame(root, padding="3 3 120 30")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        percent_split = ttk.Button(mainframe, text="Percent split", command=self.change_menu)
        percent_split.grid(column=1, row=1, sticky=(E))
        
        self.num_of_splits = StringVar()
        ttk.Entry(mainframe, width=8, textvariable=self.num_of_splits).grid(column=1, row=0, sticky=(W, E))
        
        ttk.Label(mainframe, text="Amount of splits:").grid(column=0, row=0, sticky=W)
        
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        percent_split.focus()
        root.bind("<Return>", self.change_menu)
        
    def change_menu(self, event=None):
        try:
            num_of_splits = int(self.num_of_splits.get()) # Grab the num from the user input                
            if num_of_splits > 20:
                raise TooHigh
            elif num_of_splits < 1:
                raise TooLow
        except ValueError: # Raise a ValueError if input is not an integer
            print("'" + str(self.num_of_splits.get()) + "' is an invaild input, please try again. Intergers only.")
            return
        except TooHigh: # Raise a TooHigh if input is greather than 20
            print("'" + str(self.num_of_splits.get()) + "' is too high, it must be at most 20 or less.")
            return
        except TooLow: # Raise a TooLow if input is less than 1
            print("'" + str(self.num_of_splits.get()) + "' is too low, it must be at least 1 or more.")
            return
        
        MenuHandler.change_menu(root, 1, num_of_splits) # Call next class *outside* of the try to avoid grabbing exception from it

class PercentSplitMenu:
    def __init__(self, root, num_of_splits):
        for widget in entries + labels: # Destory any pre existing widgets
            widget.destroy()
        labels.clear() # Clear lists for labels and entries
        entries.clear()
                
        root.title("NumUp - Split by percent")
        
        '''
        Since the number of splits is dynamic you have to obviously make the size dynamic.
        --> Technically I could leave it dynamic resize, but it looks better like this
            with resizing locked.
        
        The math behind the height is pretty simple; all I did was let the window
        dynamically resize for num_of_splits = 0 and 20 (the highest allowed). Then
        screenshot both and paste into a image editor and get the height via that.
        Combine going by the padding and ignoring extra space on the 0 screenshot (85px),
        then take that number and subtract it from the full height of the 20 num_of_splits
        screenshot (705px). In the end we get this; (705-85)/20, which gives us 31px as
        the height of a single row of the dynamic widgets. Then we multiply the row height
        (31px) by the num_of_splits and finally add the base height (85) to it.
        
        P.S. Don't include the title bar (32px standard)
        '''
        root.geometry(f"500x{85 + 31 * num_of_splits}")
        
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.num_to_split = StringVar()
        num_to_split_entry = ttk.Entry(mainframe, width=6, textvariable=self.num_to_split)
        num_to_split_entry.grid(column=1, row=0, sticky=(W, E))

        ttk.Button(mainframe, text="Calculate", command=self.percent_calc).grid(column=2, row=(num_of_splits + 2))
        ttk.Button(mainframe, text="Return", command=lambda: MenuHandler.change_menu(root, 0), width=10).grid(column=3, row=0)
        ttk.Button(mainframe, text="Help", command=lambda: MenuHandler.change_menu(root, -1), width=10).grid(column=3, row=(num_of_splits + 2))
        
        self.round_integer = BooleanVar()
        ttk.Checkbutton(mainframe, text="Round to integer", variable=self.round_integer).grid(column=2, row=0)

        ttk.Label(mainframe, text="Number to split:").grid(column=0, row=0, sticky=W)
                
        for i in range(num_of_splits): # Generate input fields based on user's input
            ttk.Label(mainframe, text=f"Split percent {i + 1}:").grid(column=0, row=(i + 1), sticky=W)
            entry = ttk.Entry(mainframe)
            entry.grid(column=1, row=(i + 1), sticky=(W, E))
            entries.append(entry)
            ttk.Label(mainframe, text="Output:", anchor="center").grid(column=2, row=(i + 1))
            output_label = ttk.Entry(mainframe) # Make outputs ttk.Entry to allow user to select and copy output
            output_label.config(state="readonly", takefocus=0, background=root.cget("background"))
            output_label.grid(column=3, row=(i + 1), sticky=(W, E))
            labels.append(output_label)
        
        self.remainder_label = ttk.Label(mainframe, text="Remainder:")
        self.remainder_label.grid(column=0, row=(num_of_splits + 2), sticky=E)
        self.remainder_label_output = ttk.Entry(mainframe) # Same as output_label, ttk.Entry so user can copy
        self.remainder_label_output.config(state="readonly", takefocus=0, background=root.cget("background"))
        self.remainder_label_output.grid(column=1, row=(num_of_splits + 2), sticky=(W, E))
        
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        self.destory_remainder() # Destroy remainder and labels AFTER the above grid_configure
        for i, label in enumerate(labels):
            num = i
            self.destroy_output(num)
        
        num_to_split_entry.focus()
        root.bind("<Return>", self.percent_calc)
        
    def destory_remainder(self):
        self.remainder_label.grid_remove()
        self.remainder_label_output.grid_remove()
        
    def create_remainder(self):
        self.remainder_label.grid()
        self.remainder_label_output.grid()

    def destroy_output(self, num):
        labels[num].grid_remove()
    
    def create_output(self, num):
        labels[num].grid()

    def percent_calc(self):
        total_split_off = 0
        try:
            value = float(self.num_to_split.get())
        except ValueError:
            print("Invaild input")
            return
        
        for i, entry in enumerate(entries):
            try:
                percent_value = float(entry.get())
                if percent_value == 0:
                    continue
                
                if percent_value >= 1 or percent_value <= -1: # If greater than or equal to 1 assume it's meant to be a percent e.g. 20 = 0.2
                    percent_value = 0.01 * percent_value
                
                if percent_value > 0:
                    percent_value = min(1, percent_value) # Clamp down to 1 to make sure it's not over 100%
                    final_value = int(percent_value * value * 10000.0 + 0.5)/10000.0
                else:
                    percent_value = max(-1, percent_value) # Clamp up to -1 to make sure it's not over -100%
                    final_value = int(percent_value * value * 10000.0 - 0.5)/10000.0
                                
                if self.round_integer.get(): # Round if true - call .get() to get the actual value
                    final_value = round(final_value)
                
                total_split_off += final_value # Add up total to get remainder later
                
                num = i # Have to pass i as a var, num here, otherwise it wont work
                self.create_output(num)
                labels[i].config(state="normal") # Set to normal to edit
                labels[i].delete(0, END) # Delete string to make sure no overlap
                labels[i].insert(0, str(final_value)) # Insert the string
                labels[i].config(state="readonly") # Turn back to read only
            except ValueError:
                num = i
                self.destroy_output(num)
        
        if total_split_off == 0 or total_split_off == value: # Check if the total_split_off is nothing or it's the same as the value
            self.destory_remainder() # If either are true, destory the remainder
        else: # If neither are true, calculate the remainder and create it
            self.remainder_label_output.config(state="normal")
            self.remainder_label_output.delete(0, END)
            if self.round_integer.get(): # Round remainder if true
                self.remainder_label_output.insert(0, round(int(value - total_split_off)))
            else:
                self.remainder_label_output.insert(0, int((value - total_split_off) * 10000.0 + 0.5)/10000.0)
            self.remainder_label_output.config(state="readonly")
            self.create_remainder()

class HelpMenu:
    def __init__(self, root):
        hmenu = Toplevel(root)
        hmenu.title("NumUp - Help")
        hmenu.geometry("1280x720")
        hmenu.resizable(width=False, height=False)
        
        mainframe = ttk.Frame(hmenu, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        hmenu.columnconfigure(0, weight=1)
        hmenu.rowconfigure(0, weight=1)

class TooHigh(Exception): # Exceptions for MainMenu.change_menu
    pass
class TooLow(Exception):
    pass

if __name__ == "__main__":
    root = Tk()
    root.resizable(width=False, height=False)
    entries = []
    labels = []
    MenuHandler.change_menu(root, 0)
    root.mainloop()