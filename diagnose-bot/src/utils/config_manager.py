config = {
    'min_agents' : 3,
    'max_agents' : 5,
    'language' : 'en',
    'num_questions' : 5,
    'decision_scores' : {}
}

actual_doc = None

def get_config():
    return config

def update_config(new_config: dict):
    global config
    config.update(new_config)

def update_doc(new_doc: str):
    global actual_doc
    actual_doc = new_doc

def get_doc():
    return actual_doc