import gi.repository
gi.require_version('Secret','1')
from gi.repository import Secret
""" Reference
https://gnome.pages.gitlab.gnome.org/libsecret/libsecret-python-examples.html
"""
# Create a new Secret Service
service = Secret.Service.get_sync(Secret.ServiceFlags.NONE, None)

# Create a new Collection
#collection = Secret.Collection.new_sync(service, "my_collection", Secret.CollectionFlags.NONE, None)

# Define the secret
secret_value = "Snoopy loves me"
#secret = Secret.new(secret_value.encode(), len(secret_value), "text/plain")
secret = Secret.Value.new(secret_value, len(secret_value), "text/plain")
print (secret.get_text())
print (secret.get())
# Store the secret in the collection
item = Secret.Item.create_sync(
    collection,
    "Snoopy_secret",
    {"application": "MyApp"},
    secret,
    None
)

# Retrieve the secret
retrieved_secret = item.get_secret().get_text()

# Print the retrieved secret
print(retrieved_secret)