# https://tkdocs.com/tutorial/firstexample.html

from tkinter import *
from tkinter import ttk

root = Tk()
root.title("thresholding")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


# widgets 

threshold_lower = StringVar()
threshold_upper = StringVar()

def update_lower(*args): 
    try:
        value = int(float(threshold_lower.get()))
        threshold_lower.set(value)

        if value > int(float(threshold_upper.get())):
            threshold_upper.set(value)
    except ValueError: 
        pass

def update_upper(*args): 
    try:
        value = int(float(threshold_upper.get()))
        threshold_upper.set(value)

        if value < int(float(threshold_lower.get())):
            threshold_lower.set(value)
    except ValueError: 
        pass   

lower_entry = ttk.Entry(mainframe, width=7, textvariable=threshold_lower)
lower_entry.grid(column=2, row=1, sticky=(W,E))

upper_entry = ttk.Entry(mainframe, width=7, textvariable=threshold_upper)
upper_entry.grid(column=2, row=2, sticky=(W,E))



# label tied to the same variable as the scale, so auto-updates
# num = StringVar()
# ttk.Label(root, textvariable=num).grid(column=0, row=0, sticky='we')

# label that we'll manually update via the scale's command callback
# manual = ttk.Label(root)
# manual.grid(column=0, row=1, sticky='we')

# def update_lbl(val):
#   manual['text'] = "Scale at " + val

lower_scale = ttk.Scale(root, orient='horizontal', length=200, from_=0, to=255, variable=threshold_lower, command=update_lower)
lower_scale.grid(column=0, row=3, sticky='we')
lower_scale.set(125)

upper_scale = ttk.Scale(root, orient='horizontal', length=200, from_=0, to=255, variable=threshold_upper, command=update_upper)
upper_scale.grid(column=0, row=4, sticky='we')
upper_scale.set(175)

root.mainloop()
