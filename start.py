import os
import time
import webbrowser
import subprocess
import platform

def start_server():
    # Start the uvicorn server
    if platform.system() == "Windows":
        subprocess.Popen(["uvicorn", "main:app", "--reload"], shell=True)
    else:
        subprocess.Popen(["uvicorn", "main:app", "--reload"])

def open_browser():
    # Wait for the server to start
    time.sleep(5)
    # Open the URL in the default browser
    webbrowser.open("http://127.0.0.1:8000/docs#/default/generate_image_set_generate_image_set__post")

if __name__ == "__main__":
    start_server()
    open_browser()