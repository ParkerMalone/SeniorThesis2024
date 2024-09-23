from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import os

class Processor:
    def __init__(self):
        self.root = Tk()
        self.root.title('Image Processing')
        self.root.geometry('500x500')

        #Defaults
        self.default_resolutionX = 640
        self.default_resolutionY = 480
        self.default_screenshot = 's'
        self.default_endRecord = 'q'
        self.default_image_prefix = 'img'
        self.default_start_number = 1

        #Set StringVar from default entries
        self.resolution_x = StringVar(value=str(self.default_resolutionX))
        self.resolution_y = StringVar(value=str(self.default_resolutionY))
        self.screenshot = StringVar(value=str(self.default_screenshot))
        self.endRecord = StringVar(value=str(self.default_endRecord))
        self.image_prefix = StringVar(value=str(self.default_image_prefix))
        self.start_number = StringVar(value=str(self.default_start_number))
        self.save_directory = StringVar(value=os.getcwd())

        #Register validation methods
        self.validate_resolution = self.root.register(self.validate_resolution)
        self.validate_single_char = self.root.register(self.validate_single_char)
        self.validate_number = self.root.register(self.validate_number)

        self.create_widgets()

    def create_widgets(self):
        #Resolution label
        Label(self.root, text="Video Resolution").grid(row=0, column=0)

        #X label and entry
        Label(self.root, text="X:").grid(row=1, column=0)
        Entry(self.root, textvariable=self.resolution_x, 
              validate='key', validatecommand=(self.validate_resolution, '%P')).grid(row=1, column=1)

        #Y label and entry
        Label(self.root, text="Y:").grid(row=2, column=0)
        Entry(self.root, textvariable=self.resolution_y, 
              validate='key', validatecommand=(self.validate_resolution, '%P')).grid(row=2, column=1)

        #Keybinds label
        Label(self.root, text="Keybinds").grid(row=3, column=0)

        #Screenshot label and entry
        Label(self.root, text="Screenshot:").grid(row=4, column=0)
        Entry(self.root, textvariable=self.screenshot, 
              validate='key', validatecommand=(self.validate_single_char, '%P')).grid(row=4, column=1)

        #End record label and entry
        Label(self.root, text="End Recording:").grid(row=5, column=0)
        Entry(self.root, textvariable=self.endRecord, 
              validate='key', validatecommand=(self.validate_single_char, '%P')).grid(row=5, column=1)

        #File Options label
        Label(self.root, text="File Options").grid(row=6, column=0)

        #File browser button
        Label(self.root, text="Save Directory:").grid(row=7, column=0)
        Entry(self.root, textvariable=self.save_directory, state='readonly').grid(row=7, column=1)
        Button(self.root, text="Browse", command=self.browse_directory).grid(row=7, column=2)

        #Image prefix label and entry
        Label(self.root, text="Image Prefix:").grid(row=8, column=0)
        Entry(self.root, textvariable=self.image_prefix).grid(row=8, column=1)

        #Starting number label and entry
        Label(self.root, text="Starting Number:").grid(row=9, column=0)
        Entry(self.root, textvariable=self.start_number, 
              validate='key', validatecommand=(self.validate_number, '%P')).grid(row=9, column=1)

        #Button to start the webcam
        Button(self.root, text="Start Webcam", command=self.start_webcam).grid(row=10, column=0, columnspan=2)

    def browse_directory(self):
        """Opens a file dialog for selecting a directory where images will be saved."""
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.save_directory.set(selected_directory)

    #Validation
    def validate_resolution(self, value_if_allowed):
        if value_if_allowed.isdigit() and 144 <= int(value_if_allowed) <= 4000:
            return True
        elif value_if_allowed == "": 
            return True
        return False

    def validate_single_char(self, value_if_allowed):
        if len(value_if_allowed) <= 1:
            return True
        return False

    def validate_number(self, value_if_allowed):
        if value_if_allowed.isdigit():
            return True
        elif value_if_allowed == "":
            return True
        return False

    def start_webcam(self):
        #Retrieve the resolution from the entry fields
        try:
            width = int(self.resolution_x.get())
            height = int(self.resolution_y.get())
        except ValueError:
            print("Please enter valid integers for the resolution.")
            return

        #Webcam Window
        webcam_window = Toplevel(self.root)
        webcam_window.title("Webcam Feed")
        webcam_window.geometry('640x480')

        #Start the webcam using OpenCV
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        #Display the webcam in the Tkinter window
        label = Label(webcam_window)
        label.pack(fill=BOTH, expand=YES)

        #Initialize screenshot counter
        try:
            frame_count = int(self.start_number.get())
        except ValueError:
            print("Please enter a valid starting number.")
            return

        frame = None  #Declare frame variable

        #Function to update the webcam feed
        def update_frame():
            nonlocal frame  #Use the frame variable from the outer scope
            ret, frame = cap.read()
            if ret:
                #Convert the frame to RGB
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                #Keep webcam window fixed size
                cv2image = cv2.resize(cv2image, (640, 480))

                #Convert the frame to a PhotoImage object
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)

                #Update the label with the current frame
                label.imgtk = imgtk
                label.config(image=label.imgtk)

            #Check for keypress events
            webcam_window.bind('<KeyPress>', key_press)

            #Continue updating the frame
            label.after(10, update_frame)

        #Handle key press events for screenshot and end recording
        def key_press(event):
            nonlocal frame_count, frame 
            screenshot_key = self.screenshot.get()
            end_record_key = self.endRecord.get()

            if event.char == screenshot_key:
                if frame is not None:
                    #Save the current frame as an image
                    filename = f"{self.image_prefix.get()}{frame_count}.png"
                    save_path = os.path.join(self.save_directory.get(), filename)
                    cv2.imwrite(save_path, frame)
                    print(f"Screenshot saved as {save_path}")
                    frame_count += 1
            elif event.char == end_record_key:
                #End the recording by closing the window
                on_closing()

        update_frame()

        #Release the webcam
        def on_closing():
            cap.release()
            webcam_window.destroy()

        webcam_window.protocol("WM_DELETE_WINDOW", on_closing)

#Run Processor class
if __name__ == "__main__":
    app = Processor()
    app.root.mainloop()