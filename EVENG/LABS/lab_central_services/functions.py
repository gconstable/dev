import json

def get_api_command_node(data):
    # Convert incoming keys to a set for easy comparison
    incoming_keys = set(data.keys())
    print(data)
    print(incoming_keys)
    # Define your "fingerprints" for each action
    actions = {
        "ADD": 
            {
                "template",
                "delay",
                "name",
                "node_type",
                "top",
                "left",
                "console",
                "config",
                "ethernet",
                "serial",
                "image",
                "icon",
                "ram",
                "cpu",
                "nvram",
                "idlepc",
                "slot"
            },
        "UPDATE": {"id", "field", "value"},
        "DELETE": {"id"}
    }

    for command, required_keys in actions.items():
        if incoming_keys == required_keys:
            return command
            
    return "UNKNOWN_ACTION"

def get_api_command_n2c(data):
    # Convert incoming keys to a set for easy comparison
    incoming_keys = set(data.keys())

    # Define your "fingerprints" for each action
    actions = {
        "ADD": {"src", "src_label", "dst", "dst_label", "media"},
        "UPDATE": {"id", "field", "value"},
        "DELETE": {"id"}
    }

    for command, required_keys in actions.items():
        if incoming_keys == required_keys:
            return command
            
    return "UNKNOWN_ACTION"

def get_api_command_n2n(data):
    # Convert incoming keys to a set for easy comparison
    incoming_keys = set(data.keys())

    # Define your "fingerprints" for each action
    actions = {
        "ADD": {"src", "src_label", "dst", "dst_label", "media"},
        "UPDATE": {"id", "field", "value"},
        "DELETE": {"id"}
    }

    for command, required_keys in actions.items():
        if incoming_keys == required_keys:
            return command
            
    return "UNKNOWN_ACTION"

