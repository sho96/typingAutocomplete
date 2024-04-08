from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
import pyautogui as pag
import pyperclip as ppc
from threading import Thread
import keyboard
import time
import gc

from pynput import keyboard as pynput_keyboard

systemprompt = """
You are an helpful AI.
Your job is to write a prompt of the continuation of the sentence that user provides.
Your answer should ONLY contain the continueing part of the sentence.
User can't help you complete your answer.
You must NOT add "Here's my continuation: ", "Sure, " , "Conitnuation: " or anything similar to your prompt.
"""
#Write your answer in the user's native language.
#You must not add anything else than the continueing part of the sentence to your answer.
#But if user is clearly asking you a question, you may answer it.
#You are a helpful assistant that writes the continueing part of the sentence that user provides.
#You must only respond with the continueing part of the sentence and nothing else.

prompt = ChatPromptTemplate.from_messages([
    ("system", systemprompt),
    ("user", "{input}")
])

#llm = Ollama(
#    model="llama2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
#)

typedSoFar = ""

llm = prompt | Ollama(
    model="mistral"
)

def generate_text(prompt, max_tokens=500):
    #return llm(prompt, options={"maxTokens": max_tokens}).replace("\n", " ")
    return llm.invoke({"input": prompt, "num_prompts": max_tokens}).replace("\n", "\n")

def writeThread(msg, batchSize=100):
    originalClipboard = ppc.paste()
    ppc.copy(msg)
    pag.keyDown("ctrl")
    pag.press("v")
    ppc.copy(originalClipboard)
    pag.keyUp("ctrl")
    #for i in range(0, len(msg), batchSize):
    #    pag.keyUp("ctrl")
    #    keyboard.write(msg[i:i+batchSize])
    #    time.sleep(0.01)

def on_press(key):
    global typedSoFar
    if key == pynput_keyboard.Key.esc:
        return False
    if key == pynput_keyboard.Key.space:
        typedSoFar += " "
    if key == pynput_keyboard.Key.backspace:
        typedSoFar = typedSoFar[:-1]
    hasChar = False
    try:
        typedSoFar += key.char
        hasChar = True
    except:
        pass
    if len(typedSoFar) > 0 and hasChar:
        print("last character: ", typedSoFar[-1], ord(typedSoFar[-1]), ord("∟"))
        if ord(typedSoFar[-1]) == 28: # ctrl+\
            print("reset")
            pag.keyUp("ctrl")
            pag.write("rst")
            time.sleep(0.1)
            pag.press("backspace")
            pag.press("backspace")
            pag.press("backspace")
            typedSoFar = ""
        elif ord(typedSoFar[-1]) == 17: # ctrl+Q
            pag.keyUp("ctrl")
            pag.write(".")
            print("generating...")
            #generate_text(typedSoFar + "...")
            generated = generate_text(typedSoFar)
            print(generated)
            pag.press("backspace")
            Thread(target=writeThread, args=(generated,)).start()
            gc.collect()
        elif ord(typedSoFar[-1]) == 22: # ctrl+V
            typedSoFar = ppc.paste()
            print(f"buffer updated to: {typedSoFar}")
            

    
    typedSoFar = typedSoFar[-5000:]
    #print(typedSoFar)
    return True


with pynput_keyboard.Listener(on_press=on_press) as listener:
    listener.join()