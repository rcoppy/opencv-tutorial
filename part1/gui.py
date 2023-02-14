# https://tkdocs.com/tutorial/firstexample.html

from tkinter import *
from tkinter import ttk

import numpy as np
import cv2 as cv
from PIL import Image, ImageTk

capture_max_width =  1024
capture_max_height = 768

blank_buffer = np.zeros((255, 255, 3), dtype='uint8')
blank_buffer[:] = (128, 23, 200)

capture = cv.VideoCapture(0)
cv_raw_frame = np.copy(blank_buffer)

root = Tk()
root.title("thresholding")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

label_image = ImageTk.PhotoImage(
    Image.fromarray(blank_buffer)
)

def constrain_image_to_max_res(frame, hres, vres):
    copy = np.copy(frame)

    if copy.shape[1] > hres: 
        height = copy.shape[0] * (hres / copy.shape[1])
        copy = cv.resize(copy, (hres, int(height)), cv.INTER_AREA)

    if copy.shape[0] > vres: 
        width = copy.shape[1] * (vres / copy.shape[0])
        copy = cv.resize(copy, (int(width), vres), cv.INTER_AREA)

    return copy

def handle_capture_button(*args):
    try: 
        update_raw_frame(get_new_capture())
        update_camera_capture_label()
    except ValueError:
        pass    

photo_button = ttk.Button(root, text="new capture", command=handle_capture_button)
photo_button.grid(column=0, row=6, sticky='we')

camera_capture = ttk.Label(root, image=label_image)
camera_capture.grid(column=0, row=5, sticky='we')


# widgets 

threshold_lower = StringVar()
threshold_upper = StringVar()
blur_kernel = StringVar()

# https://stackoverflow.com/questions/50508452/implementing-photoshop-high-pass-filter-hpf-in-opencv
def highpass(img, sigma):
    return img - cv.GaussianBlur(img, (0,0), sigma) + 127

def convert_grayscale_cv_to_tk(frame): 
    copy = np.copy(frame)
    cv.cvtColor(copy, cv.COLOR_GRAY2BGR)

    # cv.imshow("post converted", copy)
    print("converted back to tk")

    return ImageTk.PhotoImage(
        Image.fromarray(copy)
    )

def convert_cv_to_tk(frame):
    copy = np.copy(frame)

    # swap the red and blue channels
    # https://stackoverflow.com/questions/38538952/how-to-swap-blue-and-red-channel-in-an-image-using-opencv
    red = copy[:,:,2].copy()
    blue = copy[:,:,0].copy()

    copy[:,:,0] = red
    copy[:,:,2] = blue
    
    return ImageTk.PhotoImage(
        Image.fromarray(copy)
    )

def process_frame(frame):
    copy = np.copy(frame) 
    kernel = int(float(blur_kernel.get()))

    copy = constrain_image_to_max_res(copy, capture_max_width, capture_max_height)

    hp = highpass(copy, 3)
    cv.imshow("highpass", hp)

    blur = cv.blur(copy, (kernel, kernel))
    
    # grayscale = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    # edges = cv.Canny(grayscale, int(float(threshold_lower.get())), int(float(threshold_upper.get())))
    
    #cv.imshow('processed', edges)

    print("frame processed")

    return blur

    # cv.imshow('capture', frame)

def get_new_capture(): 
    
    isTrue, frame = capture.read()
    
    if isTrue:
        cv.imshow('raw capture', constrain_image_to_max_res(frame, capture_max_width, capture_max_height))
        return frame
        # grayscale = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # edges = cv.Canny(grayscale, threshold_lower, threshold_upper)

        # cv.imshow('capture', frame)
    
    print("failed to get new capture")
    return cv_raw_frame

def update_lower(*args): 
    try:
        value = int(float(threshold_lower.get()))
        threshold_lower.set(value)

        if value > int(float(threshold_upper.get())):
            threshold_upper.set(value)

        update_camera_capture_label()
    except ValueError: 
        pass

def update_upper(*args): 
    try:
        value = int(float(threshold_upper.get()))
        threshold_upper.set(value)

        if value < int(float(threshold_lower.get())):
            threshold_lower.set(value)

        update_camera_capture_label()
    except ValueError: 
        pass    

def update_blur(*args): 
    try:
        value = int(float(blur_kernel.get()))
        blur_kernel.set(value)

        update_camera_capture_label()
    except ValueError: 
        pass 

def update_raw_frame(frame):
    global cv_raw_frame
    cv_raw_frame = np.copy(frame)

def update_camera_capture_label(*args): 
    try: 
        cv.imshow("raw preprocessed on update", cv_raw_frame)
        processed_frame = process_frame(cv_raw_frame)
        new_image = convert_cv_to_tk(processed_frame)
        camera_capture.configure(image=new_image)
        camera_capture.image = new_image 
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

lower_scale = ttk.Scale(mainframe, orient='horizontal', length=200, from_=0, to=255, variable=threshold_lower, command=update_lower)
lower_scale.grid(column=0, row=3, sticky='we')
lower_scale.set(125)

upper_scale = ttk.Scale(mainframe, orient='horizontal', length=200, from_=0, to=255, variable=threshold_upper, command=update_upper)
upper_scale.grid(column=0, row=4, sticky='we')
upper_scale.set(175)

ttk.Label(mainframe, width=20, text="blur kernel size").grid(column=0, row=5, sticky='we')
blur_scale = ttk.Scale(mainframe, orient='horizontal', length=200, from_=1, to=60, variable=blur_kernel, command=update_blur)
blur_scale.grid(column=1, row=5, sticky='we')
blur_scale.set(3)




root.bind("<Destroy>", capture.release)
root.mainloop()

