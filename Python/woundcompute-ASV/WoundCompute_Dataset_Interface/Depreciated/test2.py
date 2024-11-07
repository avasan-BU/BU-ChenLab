import tkinter as tk
from tkinter import ttk
import pandas as pd
import re


class WellPlateInterface:
    def __init__(self, master, stage_pos_map_in, basename):
        self.master = master
        self.master.title("96-Well Plate Layout")

        self.conditions = []
        self.wells = {}
        self.df = pd.DataFrame(columns=['Well', 'Condition'])

        # Filter stage_pos_map
        self.stage_pos_map_in = self.filter_stage_pos_map(stage_pos_map_in)

        # Extract positions for the given basename
        self.allowed_wells = set(self.stage_pos_map_in[basename].values())

        self.create_widgets()
        self.create_plate()

    def filter_stage_pos_map(self, stage_pos_map_in):
        pattern = re.compile(r'^[A-H]\d{2}$')
        return {
            key: {k: v for k, v in value.items() if pattern.match(v)}
            for key, value in stage_pos_map_in.items()
        }

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
        ttk.Button(self.master, text="Unassign Condition", command=self.unassign_wells).grid(row=1, column=3, padx=5,
                                                                                         pady=5)
        ttk.Button(self.master, text="Select/Deselect All Wells", command=self.toggle_all_selection).grid(row=1, column=4,
                                                                                                    padx=5, pady=5)
        ttk.Button(self.master, text="Finish Assignment", command=self.end_selection).grid(row=1, column=5, padx=5,
                                                                                           pady=5)


    def create_plate(self):
        self.plate_frame = ttk.Frame(self.master)
        self.plate_frame.grid(row=2, column=0, columnspan=6, padx=10, pady=10)

        for row in range(8):
            for col in range(12):
                well = f"{chr(65 + row)}{col + 1:02}"  # Format to two digits
                button = ttk.Button(self.plate_frame, text=well, width=10)
                button.grid(row=row, column=col, padx=1, pady=1)

                if well not in self.allowed_wells:
                    button.state(["disabled"])
                else:
                    button.bind("<Button-1>", lambda e, w=well: self.toggle_selection(w))
                    button.bind("<B1-Motion>", lambda e: self.drag_selection(e))
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

    def toggle_all_selection(self):
        select_all = not all(well["selected"] for well in self.wells.values() if well["button"].instate(["!disabled"]))

        for well in self.allowed_wells:
            if well in self.wells:
                if select_all:
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
        assigned_wells_count = len([w for w in self.wells.values() if w['condition'] is not None])

        print(f"Assigned Wells: {assigned_wells_count}, Allowed Wells: {len(self.allowed_wells)}")  # Debugging line

        if assigned_wells_count == len(self.allowed_wells):  # All wells assigned
            print("All conditions assigned.")
            root.quit()  # Terminate the main loop and close the interface
        else:
            print("Not all wells are assigned yet.")

    def assign_condition(self):
        condition = self.condition_var.get()
        for well in self.allowed_wells:  # Ensure only allowed wells are processed
            if well in self.wells and self.wells[well]["selected"]:
                self.wells[well]["condition"] = condition
                display_text = f"{well}\n{condition}"
                if len(display_text) > 15:
                    display_text = f"{well}\n{condition[:12]}..."
                self.wells[well]["button"].configure(text=display_text)

                if well in self.df['Well'].values:
                    self.df.loc[self.df['Well'] == well, 'Condition'] = condition
                else:
                    new_row = pd.DataFrame({'Well': [well], 'Condition': [condition]})
                    self.df = pd.concat([self.df, new_row], ignore_index=True)

                # Deselect after assignment
                self.wells[well]["selected"] = False
                self.wells[well]["button"].state(["!pressed"])

    def unassign_wells(self):
        for well in list(self.df['Well']):
            if well in [w for w in self.allowed_wells if w in self.wells and self.wells[w]['selected']]:
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

    def get_assigned_dataframe(self):
        return self.df


# Example usage
stage_pos_map = {
    'tissue_bi': {1: 'Drift', 2: 'A01', 3: 'A04', 4: 'A05', 5: 'A07', 6: 'A08', 7: 'A09', 8: 'A10', 9: 'A11', 10: 'A12',
                  11: 'B12', 12: 'B10', 13: 'B09', 14: 'B07', 15: 'B06', 16: 'B05', 17: 'B04', 18: 'B03', 19: 'B02',
                  20: 'C01', 21: 'C03', 22: 'C08', 23: 'C09', 24: 'C10', 25: 'C11', 26: 'C12', 27: 'D12', 28: 'D11'}
}

root = tk.Tk()
app = WellPlateInterface(master=root,
                         stage_pos_map_in=stage_pos_map,
                         basename='tissue_bi')
root.mainloop()

# Access the dataframe after closing the interface
assigned_df = app.get_assigned_dataframe()
print(assigned_df)
