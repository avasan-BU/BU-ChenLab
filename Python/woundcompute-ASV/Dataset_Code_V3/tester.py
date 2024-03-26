
# Import module
import tkinter as tk

# Create object
window = tk.Tk()

# Adjust size
window.geometry( "200x200" )

# Change the label text
def show():
    label.config( text = clicked.get() )

# Dropdown menu options
options_image_type = [
    "Ph1",
    "BF",
]

# datatype of menu text
clicked = tk.StringVar()

# Create Label
label = tk.Label( window , text = "Yaml inputs" )
label.pack()

# initial menu text
clicked.set( "Ph1" )

# Create Dropdown menu
drop = tk.OptionMenu( window , clicked , *options_image_type )
drop.pack()

var1 = tk.IntVar()
c1 = tk.Checkbutton(window, text='Python',variable=var1, onvalue=1, offvalue=0)
c1.pack()

# Create button, it will change label text
button = tk.Button( window , text = "click Me" , command = show ).pack()

# Execute tkinter
window.mainloop()