"""
    Import the tkinter module.
    Create an instance of the main application window using tk.Tk().
    Define a function on_drop(event) to handle the drop event.
    Retrieve the file path of the dropped image from the event.
    Process the dropped image (in this case, print the file path).
    Register the application window as a drop target for files using root.drop_target_register('DND_Files').
    Bind the on_drop function to the <<Drop>> event using root.dnd_bind('<<Drop>>', on_drop).
    Start the main event loop using root.mainloop().
"""
# May not be useful because some QR codes aren't displayed as draggable images.
# Find_qr_code is more reliable.
from tkinterdnd2 import TkinterDnD, DND_FILES  # Import the necessary modules

root = TkinterDnD.Tk()  # Use TkinterDnD.Tk() instead of tk.Tk()

def on_drop(event):
    # Get the file path of the dropped image
    file_path = event.data

    # Process the dropped image here
    print("Image dropped:", file_path)

# Register the window as a drop target for files
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()