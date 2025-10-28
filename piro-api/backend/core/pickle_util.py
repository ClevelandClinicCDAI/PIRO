import pickle
import base64


# Serialize an object into a plain text
def obj_to_txt(obj):
    message_bytes = pickle.dumps(obj)
    base64_bytes = base64.b64encode(message_bytes)
    txt = base64_bytes.decode("ascii")
    return txt


# De-serialize an object from a plain text
def txt_to_obj(txt):
    base64_bytes = txt.encode("ascii")
    message_bytes = base64.b64decode(base64_bytes)
    obj = pickle.loads(message_bytes)
    return obj


# class for demonstration
class DemoPickle:
    def __init__(self):
        # It has some data which can be serialized
        self.some_data = "hello"

    def say_hello(self):
        print(self.some_data)


# Creating an instance of Demo class
# obj = DemoPickle()

# Serializing the object into a plain text
# obj_string = obj_to_txt(obj)

# De-serializing the plain text into another object
# obj2 = txt_to_obj(obj_string)

# Checking the the new object is working
# It should print: Hello
# obj2.say_hello()
