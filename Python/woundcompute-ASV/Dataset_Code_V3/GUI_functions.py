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

# GUI Functions
def io_function(section2: bool) -> (str, str):
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
    return path_input, path_output


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
    option_section2 = tkinter.BooleanVar()
    option_section3 = tkinter.BooleanVar()
    option_section4 = tkinter.BooleanVar()

    option_section2.set(True)
    option_section3.set(True)
    option_section4.set(True)

    check_s2 = tkinter.Checkbutton(window, text='Sort and Arrange Files', variable=option_section2, onvalue=True,
                             offvalue=False)

    check_s3 = tkinter.Checkbutton(window, text='Run parallel WoundComputes', variable=option_section3, onvalue=True,
                             offvalue=False)
    check_s4 = tkinter.Checkbutton(window, text='Run extract_data', variable=option_section4, onvalue=True,
                             offvalue=False)

    check_s2.pack()
    check_s3.pack()
    check_s4.pack()

    # Create button to accept variables inputted
    tkinter.Button(window, text="Proceed", command=accept).pack()
    tkinter.Button(window, text="Quit", command=killmenow).pack()
    # Execute tkinter
    window.mainloop()

    return image_type_clicked.get(), option_track_pillars.get(), cpu_threshold_clicked.get(), ms_choice_clicked.get(), option_section2.get(), option_section3.get(), option_section4.get()

class WellPlateInterface:
    def __init__(self, master_in, stage_pos_map_in, basename_in):
        self.master = master_in
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
        ttk.Button(self.master, text="Select/Deselect All Wells", command=self.toggle_all_selection).grid(row=1,
                                                                                                          column=4,
                                                                                                          padx=5,
                                                                                                          pady=5)
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
