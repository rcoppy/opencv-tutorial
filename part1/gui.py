# https://tkdocs.com/tutorial/firstexample.html

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import numpy as np
import cv2 as cv
from PIL import Image, ImageTk

capture_max_width =  512
capture_max_height = 512
is_output_grayscale = True

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

# https://www.geeksforgeeks.org/file-explorer-in-python-using-tkinter/
def handle_load_image_button():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select an image",
                                          filetypes = (("Image files",
                                                        ["*.jpg", "*.jpeg"]),
                                                       ("all files",
                                                        "*.*")))
      
    loaded_image = cv.imread(filename=filename)

    update_raw_frame(loaded_image)
    update_camera_capture_label()


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

photo_button = ttk.Button(mainframe, text="new capture", command=handle_capture_button)
photo_button.grid(column=0, row=8, sticky='we')

camera_capture = ttk.Label(mainframe, image=label_image)
camera_capture.grid(column=0, row=7, sticky='we')


# widgets 

threshold_lower = StringVar()
threshold_upper = StringVar()
blur_kernel = StringVar()
highpass_kernel = StringVar()
highpass_sigma = StringVar()
is_background_dark = IntVar()

# https://stackoverflow.com/questions/50508452/implementing-photoshop-high-pass-filter-hpf-in-opencv
def highpass(img, sigma):
    # kernel = int(float(blur_kernel.get()))
    return img - cv.GaussianBlur(img, (0,0), sigma) + 127

# https://rsdharra.com/blog/lesson/9.html
def lowpass(img):
    kernel = np.ones((5,5), np.float32)/25

    # Apply convolution between image and 5x5 Kernel
    return cv.filter2D(img, -1, kernel)

def convert_grayscale_cv_to_tk(frame): 
    copy = np.copy(frame)
    cv.cvtColor(copy, cv.COLOR_GRAY2BGR)

    # cv.imshow("post converted", copy)
    print("converted back to tk")

    return ImageTk.PhotoImage(
        Image.fromarray(copy)
    )

def extract_red_from_frame(frame):
    red = frame[:,:,2].copy()

    # cv.imshow("red channel", red)

    return red

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
    blur_kernel_int = int(float(blur_kernel.get()))
    morph_kernel_int = int(float(highpass_kernel.get()))

    copy = constrain_image_to_max_res(copy, capture_max_width, capture_max_height)
    red_raw = extract_red_from_frame(copy)

    # blur = cv.blur(copy, (kernel, kernel))
    # hp = highpass(blur, 3)
    # hp = cv.cvtColor(hp, cv.COLOR_BGR2GRAY)

    # cv.imshow("highpass", hp)

    # cv.bilateralFilter

    red_equalized = cv.equalizeHist(red_raw)
    # cv.imshow('equalized', copy)

    # red_blurred = cv.blur(red_equalized, (blur_kernel_int, blur_kernel_int))
    denoised_red = cv.bilateralFilter(red_equalized, blur_kernel_int, sigmaColor=30, sigmaSpace=30) # cv.blur(blur, (2 * blur_kernel_int, 2 * blur_kernel_int))

    #sigmaColor = 30 # int(float(threshold_lower.get()))
    #sigmaSpace = 30 # int(float(threshold_upper.get()))

    # blur = cv.bilateralFilter(blur, kernel, sigmaColor=sigmaColor, sigmaSpace=sigmaSpace)

    #ret, result = cv.threshold(blur, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)

    morph_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (morph_kernel_int, morph_kernel_int))
    
    morphed = cv.morphologyEx(denoised_red, cv.MORPH_OPEN, morph_kernel)
    morphed = cv.morphologyEx(morphed, cv.MORPH_CLOSE, morph_kernel)
    morphed = cv.dilate(morphed, morph_kernel)
    morphed = cv.equalizeHist(morphed)

    contrast = int(float(threshold_lower.get()))
    brightness = int(float(threshold_upper.get()))

    morphed = cv.convertScaleAbs(morphed, alpha=-1, beta=55)
    morphed = cv.equalizeHist(morphed)

    # ret, outline = cv.threshold(morphed, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    outline = cv.Canny(morphed, 64, 250)
    outline = cv.dilate(outline, 2*morph_kernel)
    outline = cv.GaussianBlur(outline, (9, 9), sigmaX=3, sigmaY=3)

    cv.imshow('outline', outline)
    cv.imshow('morphed', morphed)
    
    maybe_inverted = morphed if is_background_dark.get() == 1 else cv.bitwise_not(morphed)
    maybe_inverted_outline = cv.bitwise_not(outline) if is_background_dark.get() == 0 else outline

    composite = lowpass(np.uint8(cv.subtract(maybe_inverted, maybe_inverted_outline)))
    composite = cv.convertScaleAbs(composite, alpha=contrast, beta=brightness)

    cv.imshow('composite', composite)

    # denoised_red = cv.bilateralFilter(red_equalized, 2 * blur_kernel_int, sigmaColor=sigmaColor, sigmaSpace=sigmaSpace) # cv.blur(blur, (2 * blur_kernel_int, 2 * blur_kernel_int))

    features = cv.dilate(
        cv.bitwise_not(
            highpass(composite, 3)
        ), 3 * morph_kernel)

    #ret, features = cv.threshold(features, 0, 255, cv.THRESH_OTSU)

    #features = cv.morphologyEx(features, cv.MORPH_OPEN, morph_kernel)
    #features = cv.morphologyEx(features, cv.MORPH_CLOSE, morph_kernel)
    # features = cv.erode(features, morph_kernel)

    # features = np.uint8(cv.multiply(features, features))

    # feature_edges = cv.dilate(cv.Canny(features, int(float(threshold_lower.get())), int(float(threshold_upper.get()))), morph_kernel)
    # cv.imshow('features', features)
    # cv.imshow('features subtracted', cv.subtract(features, feature_edges))

    ret, final = cv.threshold(composite, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    # final = np.uint8(255 * cv.divide(denoised_red, features))

    # final = cv.equalizeHist(copy)
    
    # ret, copy = cv.threshold(copy, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)

    # grayscale = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    # edges = cv.Canny(grayscale, int(float(threshold_lower.get())), int(float(threshold_upper.get())))
    
    #cv.imshow('processed', edges)

    print("frame processed")

    return final

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

        # if value > int(float(threshold_upper.get())):
        #     threshold_upper.set(value)

        update_camera_capture_label()
    except ValueError: 
        pass

def update_upper(*args): 
    try:
        value = int(float(threshold_upper.get()))
        threshold_upper.set(value)

        # if value < int(float(threshold_lower.get())):
        #     threshold_lower.set(value)

        update_camera_capture_label()
    except ValueError: 
        pass    

def update_highpass(*args): 
    try:
        value = int(float(highpass_kernel.get()))
        highpass_kernel.set(value)

        highpass_label.config(text=f"morph kernel size ({value})")

        update_camera_capture_label()
    except ValueError: 
        pass 

def update_blur(*args): 
    try:
        value = int(float(blur_kernel.get()))
        blur_kernel.set(value)

        blur_label.config(text=f"blur kernel size ({value})")

        update_camera_capture_label()
    except ValueError: 
        pass 

def update_highpass_sigma(*args): 
    try:
        value = int(float(highpass_sigma.get()))
        highpass_sigma.set(value)

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
        new_image = convert_grayscale_cv_to_tk(processed_frame) if is_output_grayscale else convert_cv_to_tk(processed_frame)
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

lower_scale = ttk.Scale(mainframe, orient='horizontal', length=200, from_=-70, to=70, variable=threshold_lower, command=update_lower)
lower_scale.grid(column=0, row=3, sticky='we')
lower_scale.set(64)

upper_scale = ttk.Scale(mainframe, orient='horizontal', length=200, from_=-255, to=255, variable=threshold_upper, command=update_upper)
upper_scale.grid(column=0, row=4, sticky='we')
upper_scale.set(250)

blur_label = ttk.Label(mainframe, width=20, text="blur kernel size")
blur_label.grid(column=0, row=5, sticky='we')
blur_scale = ttk.Scale(mainframe, orient='horizontal', length=200, from_=0, to=60, variable=blur_kernel, command=update_blur)
blur_scale.grid(column=1, row=5, sticky='we')
blur_scale.set(38)

highpass_label = ttk.Label(mainframe, width=20, text="morph kernel size")
highpass_label.grid(column=0, row=6, sticky='we')
highpass_scale = ttk.Scale(mainframe, orient='horizontal', length=200, from_=0, to=60, variable=highpass_kernel, command=update_highpass)
highpass_scale.grid(column=1, row=6, sticky='we')
highpass_scale.set(3)

# ttk.Label(mainframe, width=20, text="highpass sigma").grid(column=0, row=6, sticky='we')
# spin_box = ttk.Spinbox(
#     mainframe,
#     from_=0,
#     to=10,
#     textvariable=highpass_sigma,
#     wrap=True,
#     command=update_highpass_sigma)
# spin_box.grid(column=1, row=6, sticky='we')
# spin_box.set(3)

button_load_image = ttk.Button(mainframe, text="Load image from disk", command=handle_load_image_button)
button_load_image.grid(column=0, row=9, sticky='we')

# ttk.Label(mainframe, text="background is dark").grid(column=0, row=10, sticky='we')
background_toggle = ttk.Checkbutton(mainframe, text="background is dark", variable=is_background_dark, onvalue=1, offvalue=0, command=update_camera_capture_label)
background_toggle.grid(column=0, row=10, sticky='we')

root.bind("<Destroy>", capture.release)
root.mainloop()

