import os
import pickle
import time
import threading

import cohere


lock = threading.Lock()

cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"cache.pkl")

cohere_client = cohere.ClientV2()


def save_memory(key, val):
    while True:
        try:
            with lock:
                if os.path.exists(cache_path):
                    with open(cache_path, 'rb') as f:
                        memory = pickle.load(f)
                else:
                    memory = {}
                memory[str(key).strip()] = val
                with open(cache_path, 'wb') as f:
                    pickle.dump(memory, f)
            break
        except Exception as e:
            print(f"Error saving memory: {e}")
            time.sleep(1)
            continue

def load_memory(key, defval=None):
    while True:
        try:
            with lock:
                if os.path.exists(cache_path):
                    with open(cache_path, 'rb') as f:
                        memory = pickle.load(f)
                else:
                    memory = {}
            return memory.get(str(key).strip(), defval)
        except Exception as e:
            print(f"Error loading memory: {e}")
            time.sleep(1)
            continue


class SimpleCohereNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "system": ("STRING", {"default": "You are a friendly AI assistant."}),
                "text": ("STRING", {"default": "Hello, how are you?"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "cohere"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def cohere(self, system:str, text:str):
        key = f"cohere: system={system} , text={text}"
        response = load_memory(key)
        if response is not None:
            return (response.message.content[0].text, )
        
        if not response:
            response = cohere_client.chat(
                messages=[
                    {"role": "system", "content": str(system)},
                    {"role": "user", "content": str(text)},
                ],
                model="command-r-plus"
            )
        
        save_memory(key, response)


        return (response.message.content[0].text, )


NODE_CLASS_MAPPINGS = {
    "SimpleCohereNode": SimpleCohereNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleCohereNode": "SimpleCohereNode"
}


def simple_test():
    node = SimpleCohereNode()
    print(node.cohere("You are a friendly AI assistant.", "Hello, how are you?"))


#if __name__ == "__main__":
#    simple_test()