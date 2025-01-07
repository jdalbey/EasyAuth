import customtkinter as ctk
import pyotp
import time
import pyperclip
from tkinter import messagebox
from PIL import Image, ImageTk
from tktooltip import ToolTip
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
# Tips on form fields https://www.pythontutorial.net/tkinter/tkinter-entry/
class AppView:
    def __init__(self, controller):
        self.controller = controller
        self.controller.set_view(self)
        self.root = ctk.CTk()
        self.root.title("Easy Auth")
        self.root.geometry('700x300')
        self.create_menu()
        self.create_widgets()

    def create_widgets(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(self.root)
        self.scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh_accounts()
        self.start_timer()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        # Create a frame to act as the menu bar
        menu_bar_frame = tk.Frame(self.root, bg="lightgray", relief="raised", bd=2)
        menu_bar_frame.pack(side="top", fill="x")

        # Add the "Add Account" button to the menu bar frame
        add_account_button = tk.Button(menu_bar_frame, text="Add Account", command=self.show_add_account_form, relief="groove",
                                       highlightthickness=0, bd=2)
        add_account_button.pack(side="left", padx=5)
        add_account_button.configure(highlightbackground="lightgray")  # To simulate rounded corners

        # center-aligned labels in a nested frame
        center_frame = tk.Frame(menu_bar_frame, bg="lightgray")
        center_frame.pack(side="left", expand=True)
        # Center-aligned label
        # Search field
        keyword = tk.StringVar()
        textbox = ttk.Entry(center_frame, textvariable=keyword)
        textbox.pack(side="left", padx=10)
        # search icon
        search_label = tk.Label(center_frame, text="Q")
        search_label.pack(side="right", padx=10)
        # Add a label for the "Timer" to the menu bar frame
        import customtkinter as ctk
        timer_font = ctk.CTkFont(family='Courier', weight="bold", size=24)
        # timer_label = tk.Label(menu_bar, text=" 30 ", font=timer_font, fg="yellow", bg="gray")
        # timer_label = tk.Label(menu_bar_frame, text=" 30 ", font=timer_font, bg="gray", fg="yellow")
        # timer_label.pack(side="right", padx=20)
        # timer_font=ctk.CTkFont(family='Courier',weight="bold", size=20)
        self.timer_label = ctk.CTkLabel(menu_bar_frame, text="30", font=timer_font, text_color="yellow", fg_color="gray",
                       corner_radius=15, anchor='s')
        self.timer_label.pack(side='right', padx=20, pady=1, ipady=3)
        # Tools menu
        menu_button = tk.Menubutton(menu_bar_frame, text="Tools")
        tools_menu = tk.Menu(menu_button, tearoff=0)

        def toggle_menu(event):
            if tools_menu.winfo_ismapped():
                # collapse the menu
                tools_menu.unpost()
            else:
                tools_menu.post(menu_button.winfo_rootx(), menu_button.winfo_rooty() + menu_button.winfo_height())

        menu_button.bind("<Button-1>", toggle_menu)  # Bind left mouse click to toggle_menu

        tools_menu.add_command(label="Backup/Restore", command=self.backup_restore)
        tools_menu.add_command(label="Import", command=self.import_accounts)
        tools_menu.add_command(label="Reorder Accounts", command=self.reorder_accounts)
        tools_menu.add_command(label="Providers", command=self.manage_providers)
        tools_menu.add_command(label="Settings", command=self.settings)
        tools_menu.add_command(label="About", command=self.show_about_dialog)
        #menu_bar.add_cascade(label="Tools", menu=tools_menu)
        menu_button.config(menu=tools_menu)
        menu_button.pack(side="right", padx=5)
        # Add Account button on the menu bar
        st = Style()
        st.configure('addButton', background='#345', foreground='black', font=('Arial', 14 ))
        # filter button
        filter_button = tk.Menubutton(menu_bar_frame, text="Filter")
        fmenu = tk.Menu(filter_button, tearoff=0)
        fmenu.add_command(label="Option 1")
        fmenu.add_command(label="Option 2")
        filter_button.config(menu=fmenu)
        filter_button.pack(side="right", padx=10)

        #add_account_button = tk.Button(menu_bar, text="Add Account", command=self.show_add_account_form, bg='#345', fg='black', font=('Arial', 14))
        #menu_bar.add_command(label="Add Account", command=add_account_button)
        #add_account_button.pack(side='left', padx=5)
        # Timer label on the right-hand side of the menu bar
        #timer_font = ctk.CTkFont(family='Courier', weight="bold", size=20)
        #self.timer_label = tk.Label(menu_bar, text=" 30 ", font=timer_font, fg="yellow", bg="gray")
        #self.timer_label.pack(side='right', padx=5)

        #self.root.config(menu=menu_bar)

    def backup_restore(self):
        print("Backup/Restore selected")

    def import_accounts(self):
        print("Import selected")

    def reorder_accounts(self):
        print("Reorder Accounts selected")

    def manage_providers(self):
        print("Providers selected")

    def settings(self):
        print("Settings selected")
    def show_about_dialog(self):
        tk.messagebox.showinfo("About", "Easy Auth\nVersion 1.0")

    # def create_widgets(self):
    #     self.scrollable_frame = ctk.CTkScrollableFrame(self.root)
    #     self.scrollable_frame.pack(fill='both', expand=True)

    #     self.add_button = ctk.CTkButton(self.root, text="Add Account", command=self.show_add_account_form)
    #     self.add_button.pack(side='left')

    #     # self.refresh_button = ctk.CTkButton(self.root, text="Refresh", command=self.refresh_accounts)
    #     # self.refresh_button.pack(side='left')

    #     self.timer_label = ctk.CTkLabel(self.root, text="Time remaining: 30")
    #     self.timer_label.pack(side='top')


    #     self.refresh_accounts()
    #     self.start_timer()
    # def create_widgets(self):
    #     top_frame = ctk.CTkFrame(self.root)
    #     top_frame.pack(side='top', fill='x', padx=10, pady=10)

    #     self.add_button = ctk.CTkButton(top_frame, text="Add Account", command=self.show_add_account_form)
    #     self.add_button.pack(side='left', padx=5)
    #     timer_font=ctk.CTkFont(family='Courier',weight="bold", size=20)
    #     self.timer_label = ctk.CTkLabel(top_frame, text=" 30 ", font=timer_font, text_color="yellow", fg_color = "gray", corner_radius=5)
    #     self.timer_label.pack(side='right', padx=5)

    #     self.scrollable_frame = ctk.CTkScrollableFrame(self.root)
    #     self.scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

    #     self.refresh_accounts()
    #     self.start_timer()

    def refresh_accounts(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        accounts = self.controller.get_accounts()
        for index, account in enumerate(accounts):
            secret_key = self.controller.secrets_manager.decrypt(account.secret)
            otp = pyotp.TOTP(secret_key).now()
            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.pack(fill='x', padx=5, pady=5)
            label = ctk.CTkLabel(frame, text=f"{account.provider} ({account.label}):")
            label.pack(side='left', padx=5)

            icon_image = Image.open("images/pencil_icon.png").resize((20, 20))
            edit_image = ctk.CTkImage(icon_image)
            edit_button = ctk.CTkButton(frame, text="", image=edit_image, fg_color="white",width=20, height=20, command=lambda account=account: self.show_edit_account_form(index,account))
            #edit_button.image = edit_image  # Keep a reference to avoid garbage collection
            edit_button.pack(side='right', padx=15)
            ToolTip(edit_button, msg="Edit account")

            icon_image = Image.open("images/copy_icon.png").resize((20, 20))
            copy_image = ctk.CTkImage(icon_image)
            # image_button = ctk.CTkButton(master=frame,text="", image=button_image)
            # image_button.pack(side="right", padx=5)
            copy_button = ctk.CTkButton(frame, text="", image=copy_image, fg_color="white", width=20, height=20, command=lambda otp=otp: self.copy_to_clipboard(otp))
            #copy_button.image = copy_photo  # Keep a reference to avoid garbage collection
            copy_button.pack(side='right', padx=5)
            ToolTip(copy_button, msg="Copy code to clipboard")

            otplabel = ctk.CTkLabel(frame, text=f"{otp}")
            otplabel.pack(side='right', padx=5)

    def copy_to_clipboard(self, otp):
        pyperclip.copy(otp)
        print(f"Copied OTP: {otp}")

    def start_timer(self):
        self.update_timer()

    def update_timer(self):
        time_remaining = 30 - (int(time.time()) % 30)
        self.timer_label.configure(text=f"{time_remaining}")
        if time_remaining == 30:
            self.refresh_accounts()
        self.root.after(1000, self.update_timer)  # Schedule the update_timer function to run after 1 second

    def show_add_account_form(self):
        self.add_account_window = ctk.CTkToplevel(self.root)
        self.add_account_window.title("New Account")

        ctk.CTkLabel(self.add_account_window, text="Create a New Account from:").pack(pady=10)
        message1 = "• Fill the form automatically from a QR code on the screen"
        ctk.CTkLabel(self.add_account_window, text=message1).pack(anchor='w', padx=20)
        ctk.CTkButton(self.add_account_window, text="Find QR code", command=self.controller.find_qr_code).pack(anchor='w', padx=40)
        message2 = "• Fill the form automatically from a QR image in a file"
        ctk.CTkLabel(self.add_account_window, text=message2).pack(anchor='w', padx=20)
        ctk.CTkButton(self.add_account_window, text="Open file", command=self.controller.open_qr_image).pack(anchor='w', padx=40)

        ctk.CTkLabel(self.add_account_window, text="• Enter the data manually").pack(anchor='w', padx=20)

        form_frame = ctk.CTkFrame(self.add_account_window)
        form_frame.pack(pady=10)

        ctk.CTkLabel(form_frame, text="Provider").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.provider_entry = ctk.CTkEntry(form_frame)
        self.provider_entry.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Label").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.label_entry = ctk.CTkEntry(form_frame)
        self.label_entry.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Secret Key").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.secret_key_entry = ctk.CTkEntry(form_frame)
        self.secret_key_entry.grid(row=2, column=1, padx=10, pady=5)

        button_frame = ctk.CTkFrame(self.add_account_window)
        button_frame.pack(pady=10)
       
        ctk.CTkButton(button_frame, text="Save", command=lambda: self.controller.save_account(self.provider_entry.get(), self.label_entry.get(), self.secret_key_entry.get())).pack(side='left', padx=20)
        ctk.CTkButton(button_frame, text="Cancel", command=self.add_account_window.destroy).pack(side='right', padx=20)

    def show_edit_account_form(self, index, account):
        self.edit_account_window = ctk.CTkToplevel(self.root)
        self.edit_account_window.title("Edit Account")

        form_frame = ctk.CTkFrame(self.edit_account_window)
        form_frame.pack(pady=10, padx=10, fill='x')

        ctk.CTkLabel(form_frame, text="Provider").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.provider_entry = ctk.CTkEntry(form_frame)
        self.provider_entry.grid(row=0, column=1, padx=10, pady=5)
        self.provider_entry.insert(0, account.provider)

        ctk.CTkLabel(form_frame, text="Label").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.label_entry = ctk.CTkEntry(form_frame)
        self.label_entry.grid(row=1, column=1, padx=10, pady=5)
        self.label_entry.insert(0, account.label)

        ctk.CTkLabel(form_frame, text="Secret Key").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.secret_key_entry = ctk.CTkEntry(form_frame)
        self.secret_key_entry.grid(row=2, column=1, padx=10, pady=5)
        self.secret_key_entry.insert(0, self.controller.secrets_manager.decrypt(account.secret))

        button_frame = ctk.CTkFrame(self.edit_account_window)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Save", command=lambda: self.controller.update_account(index, self.provider_entry.get(), self.label_entry.get(), self.secret_key_entry.get())).pack(side='left', padx=20)
        ctk.CTkButton(button_frame, text="Delete", command=lambda: self.confirm_delete_account(account)).pack(side='left', padx=20)
        ctk.CTkButton(button_frame, text="Cancel", command=self.edit_account_window.destroy).pack(side='right', padx=20)

    def confirm_delete_account(self, account):
        if messagebox.askokcancel("Delete Account", "Are you sure you want to delete this account?"):
            self.controller.delete_account(account)
            self.edit_account_window.destroy()
            self.refresh_accounts()

    def populate_add_account_form(self, provider, label, secret):
        self.provider_entry.delete(0, 'end')
        self.provider_entry.insert(0, provider)
        self.label_entry.delete(0, 'end')
        self.label_entry.insert(0, label)
        self.secret_key_entry.delete(0, 'end')
        self.secret_key_entry.insert(0, secret)

    
    def run(self):
        self.root.mainloop()