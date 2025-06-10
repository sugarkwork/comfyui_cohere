import os
import pickle
import time
import threading

import cohere


lock = threading.Lock()

cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"cache.pkl")


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
        api_key = os.environ.get("COHERE_API_KEY", None)
        if api_key is None:
            api_key = os.environ.get("CO_API_KEY", None)
        if api_key is None:
            raise Exception("COHERE_API_KEY is not set")
        self.client = cohere.ClientV2(api_key)

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
            return (response, )
        
        if not response:
            messages=[]

            if system:
                messages.append({"role": "system", "content": str(system)})
            messages.append({"role": "user", "content": str(text)})
            
            response = self.client.chat(
                messages=messages,
                model="command-a-03-2025"
            )
        
            save_memory(key, response.message.content[0].text)

        return (response.message.content[0].text, )


NODE_CLASS_MAPPINGS = {
    "SimpleCohereNode": SimpleCohereNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleCohereNode": "SimpleCohereNode"
}


def simple_test():
    os.environ["COHERE_API_KEY"] = ""
    node = SimpleCohereNode()
    print(node.cohere("日本語で話すアシスタントです", "Hello, how are you?"))


#if __name__ == "__main__":
#    simple_test()
