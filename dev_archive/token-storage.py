import gi.repository
gi.require_version('Secret','1')
from gi.repository import Secret

service = Secret.Service.get_sync(Secret.ServiceFlags.NONE, None)
service.load_collections_sync(None)
collections = service.get_collections()
service.unlock_sync(collections, None)

default_collection = Secret.Collection.for_alias_sync(
    service, "default", Secret.CollectionFlags.NONE, None)

def store_token(token_id, token_value):
    # Create schema attributes
    attributes = {
        "type": "token",
        "application": "org.redpoint.easyauth",
        "token_id": token_id
    }
    
    # Create secret
    secret = Secret.Value.new(token_value, len(token_value), "text/plain")
    
    # Create properties for the item
    properties = {
        "org.freedesktop.Secret.Item.Label": f"Token {token_id}",
        "org.freedesktop.Secret.Item.Type": "org.freedesktop.Secret.Generic"
    }
    
    # Store the secret
    default_collection.create_item_sync(
        properties,
        attributes,
        secret,
        Secret.ItemCreateFlags.REPLACE,
        None
    )
def get_token(token_id):

    items = default_collection.search_sync(
        None,
        {
            "type": "token",
            "application": "org.redpoint.easyauth",
            "token_id": token_id,
        },
        Secret.SearchFlags.NONE,
        None,
    )
    if items:
        item = items[0]
        item.load_secret_sync(None)

        return item.get_secret().get_text()

# Example usage
store_token("my_token_1", "secretvalue456")
retrieved = get_token("my_token_1")
print(f"Retrieved token: {retrieved}")
