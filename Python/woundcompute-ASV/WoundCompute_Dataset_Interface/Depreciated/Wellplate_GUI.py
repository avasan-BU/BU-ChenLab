import tkinter as tk
from tkinter import ttk
import pandas as pd


class WellPlateInterface:
    def __init__(self, master):
        self.master = master
        self.master.title("96-Well Plate Layout")

        self.conditions = []
        self.wells = {}
        self.df = pd.DataFrame(columns=['Well', 'Condition'])

        self.create_widgets()
        self.create_plate()

    def create_widgets(self):
        ttk.Label(self.master, text="Number of Conditions:").grid(row=0, column=0, padx=5, pady=5)
        self.condition_entry = ttk.Entry(self.master)
        self.condition_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Set Conditions", command=self.set_conditions).grid(row=0, column=2, padx=5,
                                                                                         pady=5)

        self.condition_var = tk.StringVar()
        self.condition_dropdown = ttk.Combobox(self.master, textvariable=self.condition_var, state="readonly")
        self.condition_dropdown.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        ttk.Button(self.master, text="Assign Condition", command=self.assign_condition).grid(row=1, column=2, padx=5,
                                                                                             pady=5)
        ttk.Button(self.master, text="Unassign Wells", command=self.unassign_wells).grid(row=1, column=3, padx=5,
                                                                                         pady=5)
        ttk.Button(self.master, text="Done", command=self.close_interface).grid(row=1, column=4, padx=5, pady=5)

    def create_plate(self):
        self.plate_frame = ttk.Frame(self.master)
        self.plate_frame.grid(row=2, column=0, columnspan=5, padx=10, pady=10)

        for row in range(8):
            for col in range(12):
                well = f"{chr(65 + row)}{col + 1}"
                button = ttk.Button(self.plate_frame, text=well, width=10)  # Increased width
                button.grid(row=row, column=col, padx=1, pady=1)
                button.bind("<Button-1>", lambda e, w=well: self.toggle_selection(w))
                button.bind("<B1-Motion>", lambda e: self.drag_selection(e))
                button.bind("<ButtonRelease-1>", lambda e: self.end_selection())
                button.bind("<Control-Button-1>", lambda e, w=well: self.toggle_selection(w))
                self.wells[well] = {"button": button, "selected": False, "condition": None}

    def set_conditions(self):
        num_conditions = int(self.condition_entry.get())
        self.conditions = [f"Condition {i + 1}" for i in range(num_conditions)]
        self.condition_dropdown['values'] = self.conditions
        if self.conditions:
            self.condition_dropdown.set(self.conditions[0])

    def toggle_selection(self, well):
        if not self.wells[well]["selected"]:
            self.wells[well]["button"].state(["pressed"])
            self.wells[well]["selected"] = True
        else:
            self.wells[well]["button"].state(["!pressed"])
            self.wells[well]["selected"] = False

    def drag_selection(self, event):
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if widget in [self.wells[well]["button"] for well in self.wells]:
            well = widget.cget("text").split("\n")[0]
            if not self.wells[well]["selected"]:
                widget.state(["pressed"])
                self.wells[well]["selected"] = True

    def end_selection(self):
        pass  # Can be used to finalize selection if needed

    def assign_condition(self):
        condition = self.condition_var.get()
        for well in self.wells:
            if self.wells[well]["selected"]:
                self.wells[well]["condition"] = condition
                # Adjusted text formatting
                display_text = f"{well}\n{condition}"
                if len(display_text) > 15:
                    display_text = f"{well}\n{condition[:12]}..."
                self.wells[well]["button"].configure(text=display_text)

                # Update dataframe
                if well in self.df['Well'].values:
                    self.df.loc[self.df['Well'] == well, 'Condition'] = condition
                else:
                    new_row = pd.DataFrame({'Well': [well], 'Condition': [condition]})
                    self.df = pd.concat([self.df, new_row], ignore_index=True)

                # Deselect after assignment
                self.wells[well]["selected"] = False
                self.wells[well]["button"].state(["!pressed"])

        print(self.df)  # Print dataframe for demonstration

    def unassign_wells(self):
        for well in list(self.df['Well']):
            if well in [w for w in self.wells if self.wells[w]['selected']]:
                # Unassign the condition
                index = self.df[self.df['Well'] == well].index
                if len(index) > 0:
                    # Remove from dataframe
                    self.df.drop(index=index[0], inplace=True)

                # Reset button and deselect
                button_info = self.wells[well]
                button_info['condition'] = None
                button_info['button'].configure(text=f"{well}")
                button_info['selected'] = False
                button_info['button'].state(["!pressed"])

        print(self.df)  # Print dataframe for demonstration

    def close_interface(self):
        all_assigned = all(well["condition"] is not None for well in self.wells.values())

        if all_assigned:
            print(len(self.wells), " wells are assigned. Closing interface.")
            root.destroy()
        else:
            print("Not all wells are assigned.")


root = tk.Tk()
app = WellPlateInterface(root)
root.mainloop()