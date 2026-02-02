memory_store = {}

def get_history(session_id):
    return memory_store.get(session_id, [])

def save_history(session_id, history):
    memory_store[session_id] = history
