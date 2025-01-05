import tkinter as tk
import time
def hide_window(root):
    root.withdraw()  # window completely disappears (not just minimized)

def restore_window(root):
    root.deiconify()

def shrink_and_restore(root):
    hide_window(root)
    time.sleep(3)
    restore_window(root)
    #root.after(3000, lambda: restore_window(root))

root = tk.Tk()
root.geometry("400x400")

shrink_button = tk.Button(root, text="Shrink", command=lambda: shrink_and_restore(root))
shrink_button.pack()

root.mainloop()