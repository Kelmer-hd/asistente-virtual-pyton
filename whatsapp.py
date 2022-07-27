import webbrowser
import pyautogui as at
import time

#definimos una funcion que me permite tomar un contacto y un mensaje para el envio de msm
def send_message(contact, message):
    webbrowser.open(f"https://web.whatsapp.com/send?phone={contact}&text={message}")
    time.sleep(20) #pausar un momento el programa hasta que habra whartapp o cargue
    at.press('enter')

    

