import pyotp
import time
import pyperclip
from tkinter import messagebox
from PIL import Image, ImageTk
from tktooltip import ToolTip
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
import customtkinter as ctk
from CTkMenuBar import *

# Tips on form fields https://www.pythontutorial.net/tkinter/tkinter-entry/
class AppView:
    def __init__(self, controller):
        self.controller = controller
        self.controller.set_view(self)
        self.root = ctk.CTk()
        self.root.title("Easy Auth")
        self.root.geometry('700x300')
        self.create_ctkmenubar()
        self.create_menu()
        self.create_widgets()

    def create_ctkmenubar(self):
        menu = CTkMenuBar(self.root, bg_color="lightgray")
        menuitem_file = menu.add_cascade("File")
        menuitem_tools = menu.add_cascade("Tools")
        menuitem_help = menu.add_cascade("Help")

        dropdown_file = CustomDropdownMenu(widget=menuitem_file)
        dropdown_file.add_option(option="Backup/Restore", command=self.backup_restore)
        dropdown_file.add_option(option="Import", command=self.import_accounts)

        dropdown_file.add_separator()

        dropdown_file.add_option(option="Settings", command=lambda: tk.messagebox.showinfo("Settings", "Settings will appear here."))

        dropdown_tools = CustomDropdownMenu(widget=menuitem_tools)
        dropdown_tools.add_option(option="Reorder Accounts", command=self.reorder_accounts)
        dropdown_tools.add_option(option="Providers", command=self.manage_providers)

        dropdown_help = CustomDropdownMenu(widget=menuitem_help)
        dropdown_help.add_option(option="Quick Start")
        dropdown_help.add_option(option="User Guide")
        dropdown_help.add_option(option="About", command=self.show_about_dialog)

    def create_widgets(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(self.root)
        self.scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh_accounts()
        self.start_timer()

    def create_menu(self):
        #menu_bar = tk.Menu(self.root)
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
        timer_font = ctk.CTkFont(family='Courier', weight="bold", size=24)
        self.timer_label = ctk.CTkLabel(menu_bar_frame, text="30", font=timer_font, text_color="yellow", fg_color="gray",
                       corner_radius=15, anchor='s')
        self.timer_label.pack(side='right', padx=20, pady=1, ipady=3)

        # st = Style()
        # st.configure('addButton', background='#345', foreground='black', font=('Arial', 14 ))
        # filter button
        filter_button = tk.Menubutton(menu_bar_frame, text="Filter")
        fmenu = tk.Menu(filter_button, tearoff=0)
        fmenu.add_command(label="Provider A-Z")
        fmenu.add_command(label="User A-Z")
        fmenu.add_command(label="Last used ^")
        fmenu.add_command(label="Last used v")
        filter_button.config(menu=fmenu)
        filter_button.pack(side="right", padx=10)


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
        self.root.option_add('*Dialog.msg.font', 'Helvetica 10')
        tk.messagebox.showinfo("About", "Easy Auth\nVersion 0.0.1\nhttps://github.com/jdalbey/EasyAuth")
        self.root.option_clear()

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
        Form_AddAccount(self.root,self.controller)

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

class Form_AddAccount:
        def __init__ (self, root,controller):
            self.add_account_window = ctk.CTkToplevel(root)
            self.add_account_window.title("New Account")
            self.controller = controller
            self.create_add_account_form()

        def is_form_filled(self,*args):
            # Check if all fields have a value
            all_filled = all(var.get().strip() for var in self.form_vars)
            self.save_button["state"] = "normal" if all_filled else "disabled"

        def create_add_account_form(self):
            # List of StringVars, one for each field
            self.form_vars = []

            ctk.CTkLabel(self.add_account_window, text="There are 3 ways to create a new account:").pack(pady=10)
            message1 = "1) Fill the form automatically from a QR code on the screen."
            ctk.CTkLabel(self.add_account_window, text=message1).pack(anchor='w', padx=20)
            ctk.CTkButton(self.add_account_window, text="Find QR code", command=self.controller.find_qr_code).pack(anchor='w',
                                                                                                                   padx=40)
            message2 = "2) Fill the form automatically from a QR image in a file."
            ctk.CTkLabel(self.add_account_window, text=message2).pack(anchor='w', padx=20)
            ctk.CTkButton(self.add_account_window, text="Open file", command=self.controller.open_qr_image).pack(anchor='w',
                                                                                                                 padx=40)

            ctk.CTkLabel(self.add_account_window, text="3) Enter the data manually.").pack(anchor='w', padx=20)

            form_frame = ctk.CTkFrame(self.add_account_window)
            form_frame.pack(pady=10)

            ctk.CTkLabel(form_frame, text="Provider").grid(row=0, column=0, padx=10, pady=5, sticky='e')
            var = tk.StringVar()
            self.form_vars.append(var)
            var.trace_add("write", self.is_form_filled)
            self.provider_entry = ctk.CTkEntry(form_frame, textvariable=var)
            self.provider_entry.grid(row=0, column=1, padx=10, pady=5)

            ctk.CTkLabel(form_frame, text="Label").grid(row=1, column=0, padx=10, pady=5, sticky='e')
            self.label_entry = ctk.CTkEntry(form_frame)
            self.label_entry.grid(row=1, column=1, padx=10, pady=5)

            ctk.CTkLabel(form_frame, text="Secret Key").grid(row=2, column=0, padx=10, pady=5, sticky='e')
            self.secret_key_entry = ctk.CTkEntry(form_frame)
            self.secret_key_entry.grid(row=2, column=1, padx=10, pady=5)

            button_frame = ctk.CTkFrame(self.add_account_window)
            button_frame.pack(pady=10)

            self.save_button = ctk.CTkButton(button_frame, text="Save",
                          command=lambda: self.controller.save_fields(self.provider_entry.get(), self.label_entry.get(),
                                                                      self.secret_key_entry.get()))
            self.save_button.pack(side='left', padx=20)
            self.save_button["state"] = "disabled"
            ctk.CTkButton(button_frame, text="Cancel", command=self.add_account_window.destroy).pack(side='right', padx=20)
            self.is_form_filled()
