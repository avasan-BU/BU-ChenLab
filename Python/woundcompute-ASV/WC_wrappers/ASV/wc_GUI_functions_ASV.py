# Name: GUI_functions
#
# Version: 1.3
#
# Author: Anish Vasan
#
# Organization: Chen/Eyckmans Lab, Boston University
#
# Date: 20241031

import tkinter
from tkinter.filedialog import askdirectory
from tkinter import simpledialog
import os
import pandas as pd
import sys
import re
from tkinter import ttk
from pathlib import Path
from tkinter import font as tkfont


# GUI Functions
def io_function(section2: bool) -> (Path, Path):
    """Prompt user for input folder that contains a .nd file"""
    # prompt user for the file directory. Will open as a popup window named "tk"
    tk_root = tkinter.Tk()
    print("Please open the directory that contains your .nd file")
    path_input = askdirectory(title='Select Input Folder with .nd file')  # shows dialog box and return the path
    if path_input == "":
        print("No folder selected. Program exiting.")
        quit()
    else:
        print("Inputted path:", path_input)

    if section2:
        path_output = os.path.join(path_input, 'Sorted')

        if os.path.exists(path_output):
            path_out_new = simpledialog.askstring('Output folder', 'Enter new output folder name')
            # path_out_new = input('Enter new output folder name')
            if path_out_new == "":
                print("No folder selected. Program exiting.")
                quit()
            path_output = os.path.join(path_input, path_out_new)

        # create a new  output directory

        os.makedirs(path_output)
    else:
        path_output = path_input
    tk_root.destroy()
    return Path(path_input), Path(path_output)


def input_gui() -> (str, bool, int, str, bool, bool, bool):
    # Create object
    window = tkinter.Tk()

    # Adjust size
    # window.geometry("400x400")

    # Close window after storing variables
    def accept():
        window.destroy()

    def killmenow():
        sys.exit()

    # Menu for Microscope Type

    # Dropdown menu options

    options_ms_choice = [
        "General",
        "Cytation"
    ]

    # datatype of menu text
    ms_choice_clicked = tkinter.StringVar()

    # Create Label
    label_microscope_type = tkinter.Label(window, text="Microscope:")
    label_microscope_type.pack()

    # initial menu text
    ms_choice_clicked.set("General")

    # Create Dropdown menu
    drop_ms_choice = tkinter.OptionMenu(window, ms_choice_clicked, *options_ms_choice)
    drop_ms_choice.pack()

    # Menu for Image Type

    # Dropdown menu options
    options_image_type = [
        "ph1",
        "BF",
    ]

    # datatype of menu text
    image_type_clicked = tkinter.StringVar()

    # Create Label
    label_image_type = tkinter.Label(window, text="Image Type:")
    label_image_type.pack()

    # initial menu text
    image_type_clicked.set("ph1")

    # Create Dropdown menu
    drop_image_type = tkinter.OptionMenu(window, image_type_clicked, *options_image_type)
    drop_image_type.pack()

    # Menu for Imaging Interval

    imaging_interval_var = tkinter.StringVar()
    imaging_interval_var.set("0.5")
    label_imaging_interval = tkinter.Label(window, text="Imaging Interval (hours):")
    label_imaging_interval.pack()
    vcmd = (window.register(validate_float), '%d', '%P')
    imaging_interval = tkinter.Entry(window, textvariable=imaging_interval_var, validate="key", validatecommand=vcmd)
    imaging_interval.pack()

    # Menu for number of Parallel Processes

    # datatype of menu text

    cpu_threshold_clicked = tkinter.IntVar(value=80)

    # Create Label
    label_cpu_threshold = tkinter.Label(window, text="Max CPU% Usage:")
    label_cpu_threshold.pack()

    # Create Dropdown menu
    scale_cpu_threshold = tkinter.Scale(window, from_=1, to=100, orient="horizontal", variable=cpu_threshold_clicked)
    scale_cpu_threshold.pack(side="top", fill="x")

    # Menu for Pillar Tracking
    # Create checkbox
    option_track_pillars = tkinter.BooleanVar()
    option_track_pillars.set(True)
    checkbox_track_pillars = tkinter.Checkbutton(window, text='Track Pillars', variable=option_track_pillars, onvalue=True, offvalue=False)
    checkbox_track_pillars.pack()

    # Menu for Code Sections to run
    # Create checkbox
    sections = ["Sort and Arrange Files", "Run parallel WoundComputes", "Extract Data to Excel", "Visualized Data"]
    checkboxes = []
    checkbox_options = []

    for section in sections:
        option = tkinter.BooleanVar()
        option.set(True)
        checkbox = tkinter.Checkbutton(window, text=section, variable=option, onvalue=True, offvalue=False)
        checkbox.pack()
        checkboxes.append(checkbox)
        checkbox_options.append(option)


    # Create button to accept variables inputted
    tkinter.Button(window, text="Proceed", command=accept).pack()
    tkinter.Button(window, text="Quit", command=killmenow).pack()
    # Execute tkinter
    window.mainloop()

    # Convert imaging interval to float
    try:
        imaging_interval_float = float(imaging_interval_var.get())
    except ValueError:
        imaging_interval_float = 0.0  # Default value if conversion fails

    return image_type_clicked.get(), option_track_pillars.get(), cpu_threshold_clicked.get(), ms_choice_clicked.get(), imaging_interval_float, checkbox_options[0].get(), checkbox_options[1].get(), checkbox_options[2].get(), checkbox_options[3].get()

#Function to validate input values are float only
def validate_float(action, value_if_allowed):
    # Allow empty field
    if value_if_allowed == "" or value_if_allowed == ".":
        return True
    try:
        float(value_if_allowed)
        return True
    except ValueError:
        return False

class WellPlateInterface:
    def __init__(self, master_in, path_input_in, stage_pos_map_in, basename_in):
        self.master = master_in
        self.master.title("96-Well Plate Layout: " + basename_in)

        self.conditions = []
        self.wells = {}
        self.df = pd.DataFrame(columns=['Well', 'Condition_Number', 'Condition_Name'])

        # Filter stage_pos_map
        self.stage_pos_map_out = self.filter_stage_pos_map(stage_pos_map_in)

        if self.stage_pos_map_out == {}:
            print("Error: Invalid stage position map. Assigning all wells to condition 1.")
            self.df = pd.DataFrame({'Well': list(stage_pos_map_in.values()), 'Condition_Number': 1, 'Condition_Name': 'Condition_1'})
            self.master.quit()

        # Extract positions for the given basename
        self.allowed_wells = set(self.stage_pos_map_out.values())

        self.create_widgets()
        self.create_plate()

    def filter_stage_pos_map(self, stage_pos_map_in):
        pattern = re.compile(r'([A-H]\d{2})')
        stage_pos_map_out = {k: pattern.search(v).group(1) for k, v in stage_pos_map_in.items() if pattern.search(v)}
        print(f"Filtered stage position map: {stage_pos_map_out}")
        return stage_pos_map_out


    def create_widgets(self):
        # Entry for number of conditions
        ttk.Label(self.master, text="Number of Conditions (Integer Only):").grid(row=0, column=0, padx=5, pady=5)
        self.condition_entry = ttk.Entry(self.master, width=5)
        self.condition_entry.grid(row=0, column=1, padx=5, pady=5)
        self.condition_entry.insert(0, "1")
        ttk.Button(self.master, text="Set", command=self.update_conditions).grid(row=0, column=2, padx=5, pady=5)

        # Frame for condition names
        self.condition_frame = ttk.Frame(self.master)
        self.condition_frame.grid(row=1, column=0, columnspan=6, padx=5, pady=5)
        self.condition_entries = []

        # Condition dropdown
        self.condition_var = tkinter.StringVar()
        self.condition_dropdown = ttk.Combobox(self.master, textvariable=self.condition_var, state="readonly")
        self.condition_dropdown.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Buttons
        ttk.Button(self.master, text="Assign Condition", command=self.assign_condition).grid(row=2, column=2, padx=5,
                                                                                             pady=5)
        ttk.Button(self.master, text="Unassign Wells", command=self.unassign_wells).grid(row=2, column=3, padx=5,
                                                                                         pady=5)
        ttk.Button(self.master, text="Finish Assignment", command=self.end_selection).grid(row=2, column=4, padx=5,
                                                                                           pady=5)
        ttk.Button(self.master, text="Select/Deselect All", command=self.toggle_all_selection).grid(row=2, column=5,
                                                                                                    padx=5, pady=5)

        # Initial update
        self.update_conditions()

        # Bind the update_dropdown method to the condition entries
        self.master.bind("<<ConditionNameChanged>>", self.update_dropdown)


    def update_conditions(self):
        try:
            num_conditions = int(self.condition_entry.get())
        except ValueError:
            print("Please enter a valid number")
            return

        # Clear existing entries
        for widget in self.condition_frame.winfo_children():
            widget.destroy()
        self.condition_entries.clear()

        # Create new entries in 4 columns
        for i in range(num_conditions):
            row = i // 4
            col = i % 4
            ttk.Label(self.condition_frame, text=f"Condition {i + 1}:").grid(row=row, column=col * 2, padx=5, pady=2,
                                                                             sticky='e')
            entry = ttk.Entry(self.condition_frame)
            entry.insert(0, f"Condition_{i + 1}")
            entry.grid(row=row, column=col * 2 + 1, padx=5, pady=2, sticky='w')
            entry.bind("<KeyRelease>", lambda e, idx=i: self.on_condition_change(e, idx))
            self.condition_entries.append(entry)

        self.update_dropdown()

    def on_condition_change(self, event, index):
        self.update_well_assignments(index)
        self.master.event_generate("<<ConditionNameChanged>>")

    def update_dropdown(self, event=None):
        self.conditions = [entry.get() for entry in self.condition_entries]
        self.condition_dropdown['values'] = self.conditions
        if self.conditions:
            current_value = self.condition_var.get()
            if current_value not in self.conditions:
                self.condition_dropdown.set(self.conditions[0])

    def create_plate(self):
        self.plate_frame = ttk.Frame(self.master)
        self.plate_frame.grid(row=3, column=0, columnspan=6, padx=10, pady=10)

        for row in range(8):
            for col in range(12):
                well = f"{chr(65 + row)}{col + 1:02}"  # Format to two digits
                button = tkinter.Button(self.plate_frame, text=well, width=15, height=3, wraplength=100)
                button.grid(row=row, column=col, padx=1, pady=1)

                if well not in self.allowed_wells:
                    button.config(state=tkinter.DISABLED, disabledforeground='grey')
                    italic_font = tkfont.Font(button, button.cget("font"))
                    italic_font.configure(slant="italic")
                    button.configure(font=italic_font)
                else:
                    button.bind("<Button-1>", lambda e, w=well: self.toggle_selection(w))
                    button.bind("<B1-Motion>", lambda e: self.drag_selection(e))
                    button.bind("<Control-Button-1>", lambda e, w=well: self.toggle_selection(w))

                self.wells[well] = {"button": button, "selected": False, "condition": None}

    def toggle_selection(self, well):
        if well in self.allowed_wells:  # Only allow selection of enabled wells
            if not self.wells[well]["selected"]:
                self.wells[well]["button"].config(bg='light blue')
                self.wells[well]["selected"] = True
            else:
                self.wells[well]["button"].config(bg='SystemButtonFace')
                self.wells[well]["selected"] = False

    def toggle_all_selection(self):
        select_all = not all(well_info["selected"] for well_name, well_info in self.wells.items() if well_name in self.allowed_wells)

        for well in self.allowed_wells:
            if well in self.wells:
                if select_all:
                    self.wells[well]["button"].config(bg='light blue')
                    self.wells[well]["selected"] = True
                else:
                    self.wells[well]["button"].config(bg='SystemButtonFace')
                    self.wells[well]["selected"] = False

    def drag_selection(self, event):
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if widget in [self.wells[well]["button"] for well in self.allowed_wells]:
            well = widget.cget("text").split("\n")[0]
            if not self.wells[well]["selected"]:
                widget.config(bg='light blue')
                self.wells[well]["selected"] = True

    def end_selection(self):
        assigned_wells_count = len([w for w in self.wells.values() if w['condition'] is not None])

        print(f"Assigned Wells: {assigned_wells_count}, Allowed Wells: {len(self.allowed_wells)}")  # Debugging line

        if assigned_wells_count == len(self.allowed_wells):  # All wells assigned
            print("All conditions assigned.")
            self.master.quit()  # Terminate the main loop and close the interface
        else:
            print("Not all wells are assigned yet.")

    def update_well_assignments(self, index):
        condition_name = self.condition_entries[index].get()
        condition_number = index + 1

        for well, info in self.wells.items():
            if info['condition'] == self.conditions[index]:
                info['condition'] = condition_name
                display_text = f"{well}\n{condition_name}"
                info['button'].config(text=display_text)

                if well in self.df['Well'].values:
                    self.df.loc[self.df['Well'] == well, 'Condition_Name'] = condition_name
                    self.df.loc[self.df['Well'] == well, 'Condition_Number'] = condition_number

        # Update the conditions list and dropdown
        self.conditions[index] = condition_name
        self.condition_dropdown['values'] = self.conditions
        if self.condition_var.get() == self.conditions[index]:
            self.condition_var.set(condition_name)

    def assign_condition(self):
        condition_name = self.condition_var.get()
        condition_number = self.conditions.index(condition_name) + 1
        for well in self.allowed_wells:
            if well in self.wells and self.wells[well]["selected"]:
                self.wells[well]["condition"] = condition_name
                display_text = f"{well}\n{condition_name}"
                self.wells[well]["button"].config(text=display_text)

                if well in self.df['Well'].values:
                    self.df.loc[self.df['Well'] == well, 'Condition_Number'] = condition_number
                    self.df.loc[self.df['Well'] == well, 'Condition_Name'] = condition_name
                else:
                    new_row = pd.DataFrame(
                        {'Well': [well], 'Condition_Number': [condition_number], 'Condition_Name': [condition_name]})
                    self.df = pd.concat([self.df, new_row], ignore_index=True)

                # Deselect after assignment
                self.wells[well]["selected"] = False
                self.wells[well]["button"].config(bg='SystemButtonFace')

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
                button_info['button'].config(text=f"{well}", bg='SystemButtonFace')
                button_info['selected'] = False

    def get_assigned_dataframe(self):
        return self.df

