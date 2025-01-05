import customtkinter as ctk
import pyotp
import time
import threading
import pyperclip
class AppView:
    def __init__(self, controller):
        self.controller = controller
        self.root = ctk.CTk()
        self.root.title("EasyAuth")
        self.create_widgets()

    def create_widgets(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(self.root)
        self.scrollable_frame.pack(fill='both', expand=True)

        self.add_button = ctk.CTkButton(self.root, text="Add Account", command=self.controller.add_account)
        self.add_button.pack(side='left')

        self.update_button = ctk.CTkButton(self.root, text="Update Account", command=self.controller.update_account)
        self.update_button.pack(side='left')

        self.delete_button = ctk.CTkButton(self.root, text="Delete Account", command=self.controller.delete_account)
        self.delete_button.pack(side='left')

        self.refresh_button = ctk.CTkButton(self.root, text="Refresh", command=self.refresh_accounts)
        self.refresh_button.pack(side='left')

        self.timer_label = ctk.CTkLabel(self.root, text="Time remaining: 30")
        self.timer_label.pack(side='top')

        self.refresh_accounts()
        self.start_timer()

    def copy_to_clipboard(self, otp):
        pyperclip.copy(otp)
        print(f"Copied OTP: {otp}")

    def refresh_accounts(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        accounts = self.controller.get_accounts()
        for account in accounts:
            secret_key = self.controller.secrets_manager.decrypt(account.secret)
            otp = pyotp.TOTP(secret_key).now()
            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.pack(fill='x', padx=5, pady=5)
            label = ctk.CTkLabel(frame, text=f"{account.provider} ({account.label}): {otp}")
            label.pack(side='left', padx=5)
            #copy_button = ctk.CTkButton(frame, text="Copy", command=lambda otp=otp: self.copy_to_clipboard(otp))
            copy_button = ctk.CTkButton(frame, text="Copy")
            copy_button.pack(side='right', padx=5)

    # def start_timer(self):
    #     def update_timer():
    #         while True:
    #             time_remaining = 30 - (int(time.time()) % 30)
    #             self.timer_label.config(text=f"Time remaining: {time_remaining}")
    #             time.sleep(1)
    #             self.refresh_accounts()

    #     threading.Thread(target=update_timer, daemon=True).start()
    def start_timer(self):
        self.update_timer()

    def update_timer(self):
        time_remaining = 30 - (int(time.time()) % 30)
        self.timer_label.configure(text=f"Time remaining: {time_remaining}")
        if time_remaining == 30:
            self.refresh_accounts()
        self.root.after(1000, self.update_timer)  # Schedule the update_timer function to run after 1 second

    def run(self):
        self.root.mainloop()