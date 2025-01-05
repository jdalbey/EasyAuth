#from gi.repository import Secret
import gi.repository
gi.require_version('Secret','1')
from gi.repository import Secret
"""This seems to work but means the secrets are stored in the keyring and the other fields have to be stored elsewhere.
I don't want to have to manage two distinct stores.
"""
class SecretsManager:
    def __init__(self):
        self.schema = Secret.Schema.new("org.example.Secret",
                                        Secret.SchemaFlags.NONE,
                                        {"shared_key": Secret.SchemaAttributeType.STRING})

    def encrypt(self, label, secret):
        """Secret.password_store_sync() parameters:
1. schema: Schema object defining attributes structure
2. {"username": "bill"}: Dictionary of attributes to identify/search the secret
3. Secret.COLLECTION_DEFAULT: Which keyring collection to use (default is user's login keyring)
4. "Token": Display name/label for the secret
5. "M7KP": The actual secret value to store
6. None: GCancellable object for cancelling operation (None means not cancellable)
"""
        secret = Secret.Value.new(secret, len(secret), "text/plain")
        Secret.password_store_sync(self.schema, {"label": label}, Secret.COLLECTION_DEFAULT, "token", secret, None)
        return secret  # Placeholder, should return encrypted secret

    def decrypt(self, encrypted_secret):
        return Secret.password_lookup_sync(self.schema, {"shared_key": "value1"}, None)


