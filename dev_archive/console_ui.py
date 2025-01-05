import json
from otp_mgrV1 import OTPManager
from secrets_manager import SecretsManager

def main():
    otp_manager = OTPManager()

    def add_new():
        # Option to add a new account
        if input("Do you want to add a new account? (y/n): ").lower() == 'y':
            new_entry = otp_manager.add_account()
            print(f"Account added with: {new_entry}")

    # Load accounts
    accounts = otp_manager.load_accounts()
    if not accounts:
        print("No accounts found. Please add a new account.")
    else:
        print("Accounts:")
        for idx, account in enumerate(accounts):
            print(f"{idx + 1}. {account['issuer']} {account['label']}")

        choice = int(input("Select an account to generate OTP: "))
        if choice > 0 and choice <= len(accounts):
            choice -= 1  # because list is 0-based
            otp = otp_manager.generate_otp(accounts[choice]['label'])
            print(f"OTP for {accounts[choice]['label']}: {otp}")
            exit()
        else:
            print("Invalid choice.")

    add_new()

if __name__ == '__main__':
    main()