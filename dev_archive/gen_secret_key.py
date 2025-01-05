import pyotp
import base64

# Generate 5 valid shared secret key values in base32
shared_secrets = []
for _ in range(5):
    item = pyotp.random_base32()
    shared_secrets.append(base64.b32encode(item.encode()).decode())

print(shared_secrets)

fields = pyotp.parse_uri('otpauth://hotp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXP&issuer=Secure%20App&counter=0')
print (fields.name)
print (fields.secret)
print (fields.issuer)
print ()
key = "JBSWY3DPEHPK3PXP"
totp = pyotp.TOTP(key)
print(f"Current OTP for {key}:  {totp.now()}")

act1 = pyotp.totp.TOTP('JBSWY3DPEHPK3PXP').provisioning_uri(name='alice@google.com', issuer_name='Secure App')
print (act1)