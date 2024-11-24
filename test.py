    
import platform
import time

def play_beep():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 500)
    elif platform.system() == "Darwin":
        import os
        os.system('echo -n "\a"')


while True:
    print("beep")
    play_beep()
    time.sleep(2)
