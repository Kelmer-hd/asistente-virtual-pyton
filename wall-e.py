from requests import request
import speech_recognition as sr
import time
import subprocess as sub
import pyttsx3
import pywhatkit
import wikipedia
import datetime
import keyboard
import os
from tkinter import *
from PIL import Image, ImageTk
from pygame import mixer
import threading as tr
import whatsapp as whapp
#import browser
import database
from chatterbot import ChatBot
from chatterbot import preprocessors
from chatterbot.trainers import ListTrainer                                                                                                                                    
main_window = Tk()
main_window.title("Wall-E")

main_window.geometry("1000x650")
main_window.resizable(0, 0)
main_window.configure(bg='#DBD4B4')

comandos = """
    Comandos que puedes usar:
    - Reproduce..(canción)
    - Busca...(algo)
    - Abre...(página web o app)
    - Archivo...(nombre)
"""

label_title = Label(main_window, text="WALL-E", bg="#DBD4B4", fg="#2c3e50",
                    font=('Arial', 30, 'bold'))
label_title.pack(pady=10)

canvas_comandos = Canvas(bg="#DBD4B4", height=200, width=250)
canvas_comandos.place(x=0, y=0)
canvas_comandos.create_text(90, 80, text=comandos,
                            fill="#434343", font='Arial 10')

text_info = Text(main_window, bg="#DBD4B4", fg="black")
text_info.place(x=0, y=210, height=440, width=250)


walle_gif_path = "Images/juanita.gif"
info_gif = Image.open(walle_gif_path)
git_nframes = info_gif.n_frames

walle_gif_list = [PhotoImage(file=walle_gif_path, format=f'gif -index {i}') for i in range(git_nframes)]
label_gif = Label(main_window)
label_gif.pack()

def animate_gif(index):
    frame = walle_gif_list[index]
    index += 1
    if index == git_nframes:
        index = 0
    label_gif.configure(image=frame)
    main_window.after(50, animate_gif, index)

animate_gif(0)


def mexican_voice():
    change_voice(0)


def english_voice():
    change_voice(1)


def change_voice(id):
    engine.setProperty('voice', voices[id].id)
    engine.setProperty('rate', 145)
    talk("Hola soy walli!")


name = "walle"
listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 145)


def charge_data(name_dict, name_file):
    try:
        with open(name_file) as f:
            for line in f:
                (key, val) = line.split(",")
                val = val.rstrip("\n")
                name_dict[key] = val
    except FileNotFoundError as e:
        pass


sites = dict()
charge_data(sites, "pages.txt")
files = dict()
charge_data(files, "archivos.txt")
programs = dict()
charge_data(programs, "apps.txt")
contacts = dict()
charge_data(contacts, "contacts.txt")


def talk(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

    
def read_and_talk():
    text = text_info.get("1.0", "end")
    talk(text)


def write_text(text_wiki):
    text_info.insert(INSERT, text_wiki)


def listen(phrase=None):
    listener = sr.Recognizer()    
    with sr.Microphone() as source:            
        listener.adjust_for_ambient_noise(source)
        talk(phrase)
        pc = listener.listen(source)
    try:
        rec = listener.recognize_google(pc, language="es")
        rec = rec.lower()
    except sr.UnknownValueError:
        print("No te entendí, intenta de nuevo")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return rec

# Funciones asociadas a las palabras claves


def reproduce(rec):
    music = rec.replace('reproduce', '')
    print("Reproduciendo " + music)
    talk("Reproduciendo " + music)
    pywhatkit.playonyt(music)


def busca(rec):
    search = rec.replace('busca', '')
    wikipedia.set_lang("es")
    wiki = wikipedia.summary(search, 1)
    talk(wiki)
    write_text(search + ": " + wiki)


def abre(rec):
    task = rec.replace('abre', '').strip()

    if task in sites:
        for task in sites:
            if task in rec:
                sub.call(f'start chrome.exe {sites[task]}', shell=True)
                talk(f'Abriendo {task}')
    elif task in programs:
        for task in programs:
            if task in rec:
                talk(f'Abriendo {task}')
                os.startfile(programs[task])
    else:
        talk("Lo siento, parece que aún no has agregado esa app o página web, \
            usa los botones de agregar!")


def archivo(rec):
    file = rec.replace('archivo', '').strip()
    if file in files:
        for file in files:
            if file in rec:
                sub.Popen([files[file]], shell=True)
                talk(f'Abriendo {file}')
    else:
        talk("Lo siento, parece que aún no has agregado ese archivo, \
            usa los botones de agregar!")


def escribe(rec):
    try:
        with open("nota.txt", 'a') as f:
            write(f)

    except FileNotFoundError as e:
        file = open("nota.txt", 'a')
        write(file)

def enviar_mensaje(rec):
    talk("¿A quién quieres enviar el mensaje?")
    contact = listen("Te escucho")
    contact = contact.strip()

    if contact in contacts:
        for cont in contacts:
            if cont == contact:
                contact = contacts[cont] #sccedemos al contacto
                talk("¿Qué mensaje quieres enviarle?") 
                message = listen("Te escucho")
                talk("Enviando mensaje...")
                whapp.send_message(contact, message)
    else:
        talk("Parece qué aún no has agregado a ese contacto, usa el botón de agregar!")

def cierra(rec):
    for task in programs:
        kill_task = programs[task].split('\\')
        kill_task = kill_task[-1]
        if task in rec:
            sub.call(f'TASKKILL /IM {kill_task} /F', shell=True)
            talk(f'Cerrando {task}')
        if 'todo' in rec:
            sub.call(f'TASKKILL /IM {kill_task} /F', shell=True)
            talk(f'Cerrando {task}')
    if 'ciérrate' in rec:
        talk('Adiós!')
        sub.call('TASKKILL /IM wall-e.exe /F', shell=True)
        
def buscame(rec):
    something = rec.replace('búscame', '').strip()
    talk("Buscando " + something)
    browser.search(something)    

# Diccionario con palabras claves
key_words = {
    'reproduce': reproduce,
    'busca': busca,
    'abre': abre,
    'archivo': archivo,
    'escribe': escribe,
    'mensaje': enviar_mensaje,
    'cierra': cierra,
    'ciérrate': cierra,
    'búscame': buscame

}


def run_walle():
    chat = ChatBot("walle", database_uri=None)
    trainer = ListTrainer(chat)
    trainer.train(database.get_questions_answers())
    talk("Te escucho...")
    while True:
        try:
            rec = listen("")
        except UnboundLocalError:
            talk("No te entendí, intenta de nuevo")
            continue
        if 'busca' in rec:
            key_words['busca'](rec)
            break
        elif rec.split()[0] in key_words:
            key = rec.split()[0]        
            key_words[key](rec)
        else:
            print("Tú: ", rec)
            answers = chat.get_response(rec)
            print("walle: ", answers)
            talk(answers)
            if 'chao' in rec:
                break
    main_window.update() #refrescar el programa 

def write(f):
    talk("¿Qué quieres que escriba?")
    rec_write = listen("Te escucho")
    f.write(rec_write + os.linesep)
    f.close()
    talk("Listo, puedes revisarlo")
    sub.Popen("nota.txt", shell=True)


def open_w_files():
    global namefile_entry, pathf_entry
    window_files = Toplevel()
    window_files.title("Agrega archivos")
    window_files.configure(bg="#434343")
    window_files.geometry("300x200")
    window_files.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(window_files)} center')

    title_label = Label(window_files, text="Agrega un archivo",
                        fg="white", bg="#434343", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_files, text="Nombre del archivo",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    name_label.pack(pady=2)

    namefile_entry = Entry(window_files)
    namefile_entry.pack(pady=1)

    path_label = Label(window_files, text="Ruta del archivo",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    path_label.pack(pady=2)

    pathf_entry = Entry(window_files, width=35)
    pathf_entry.pack(pady=1)

    save_button = Button(window_files, text="Guardar", bg='#16222A',
                         fg="white", width=8, height=1, command=add_files)
    save_button.pack(pady=4)


def open_w_apps():
    global nameapps_entry, patha_entry
    window_apps = Toplevel()
    window_apps.title("Agrega apps")
    window_apps.configure(bg="#434343")
    window_apps.geometry("300x200")
    window_apps.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(window_apps)} center')

    title_label = Label(window_apps, text="Agrega una app",
                        fg="white", bg="#434343", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_apps, text="Nombre de la app",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    name_label.pack(pady=2)

    nameapps_entry = Entry(window_apps)
    nameapps_entry.pack(pady=1)

    path_label = Label(window_apps, text="Ruta de la app",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    path_label.pack(pady=2)

    patha_entry = Entry(window_apps, width=35)
    patha_entry.pack(pady=1)

    save_button = Button(window_apps, text="Guardar", bg='#16222A',
                         fg="white", width=8, height=1, command=add_apps)
    save_button.pack(pady=4)


def open_w_pages():
    global namepages_entry, pathp_entry
    window_pages = Toplevel()
    window_pages.title("Agrega páginas web")
    window_pages.configure(bg="#434343")
    window_pages.geometry("300x200")
    window_pages.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(window_pages)} center')

    title_label = Label(window_pages, text="Agrega una página web",
                        fg="white", bg="#434343", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_pages, text="Nombre de la página",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    name_label.pack(pady=2)

    namepages_entry = Entry(window_pages)
    namepages_entry.pack(pady=1)

    path_label = Label(window_pages, text="URL de la página",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    path_label.pack(pady=2)

    pathp_entry = Entry(window_pages, width=35)
    pathp_entry.pack(pady=1)

    save_button = Button(window_pages, text="Guardar", bg='#16222A',
                         fg="white", width=8, height=1, command=add_pages)
    save_button.pack(pady=4)

def open_w_contacts():
    global namecontact_entry, phone_entry
    window_contacts = Toplevel()
    window_contacts.title("Agrega un contacto")
    window_contacts.configure(bg="#434343")
    window_contacts.geometry("300x200")
    window_contacts.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(window_contacts)} center')

    title_label = Label(window_contacts, text="Agrega un contacto",
                        fg="white", bg="#434343", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_contacts, text="Nombre del contacto",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    name_label.pack(pady=2)

    namecontact_entry = Entry(window_contacts)
    namecontact_entry.pack(pady=1)

    phone_label = Label(window_contacts, text="Número celular (con código del país).",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    phone_label.pack(pady=2)

    phone_entry = Entry(window_contacts, width=35)
    phone_entry.pack(pady=1)

    save_button = Button(window_contacts, text="Guardar", bg='#16222A',
                         fg="white", width=8, height=1, command=add_contacts)
    save_button.pack(pady=4)


def add_files():
    name_file = namefile_entry.get().strip()
    path_file = pathf_entry.get().strip()

    files[name_file] = path_file
    save_data(name_file, path_file, "archivos.txt")
    namefile_entry.delete(0, "end")
    pathf_entry.delete(0, "end")


def add_apps():
    name_file = nameapps_entry.get().strip()
    path_file = patha_entry.get().strip()

    programs[name_file] = path_file
    save_data(name_file, path_file, "apps.txt")
    nameapps_entry.delete(0, "end")
    patha_entry.delete(0, "end")


def add_pages():
    name_page = namepages_entry.get().strip()
    url_pages = pathp_entry.get().strip()

    sites[name_page] = url_pages
    save_data(name_page, url_pages, "pages.txt")
    namepages_entry.delete(0, "end")
    pathp_entry.delete(0, "end")

def add_contacts():
    name_contact = namecontact_entry.get().strip()
    phone = phone_entry.get().strip()

    contacts[name_contact] = phone
    save_data(name_contact, phone, "contacts.txt")
    namecontact_entry.delete(0, "end")
    phone_entry.delete(0, "end")


def save_data(key, value, file_name):
    try:
        with open(file_name, 'a') as f:
            f.write(key + "," + value + "\n")
    except FileNotFoundError:
        file = open(file_name, 'a')
        file.write(key + "," + value + "\n")


def talk_pages():
    if bool(sites) == True:
        talk("Has agregado las siguientes páginas web")
        for site in sites:
            talk(site)
    else:
        talk("Aún no has agregado páginas web!")


def talk_apps():
    if bool(programs) == True:
        talk("Has agregado las siguientes apps")
        for app in programs:
            talk(app)
    else:
        talk("Aún no has agregado apps!")


def talk_files():
    if bool(files) == True:
        talk("Has agregado los siguientes archivos")
        for file in files:
            talk(file)
    else:
        talk("Aún no has agregado archivos!")

def talk_contacts():
    if bool(contacts) == True:
        talk("Has agregado los siguientes contactos")
        for cont in contacts:
            talk(cont)
    else:
        talk("Aún no has agregado contactos!")


def give_me_name():
    talk("Hola, ¿cómo te llamas?")
    name = listen("Te escucho")
    name = name.strip()
    talk(f"Bienvenido {name}")

    try:
        with open("name.txt", 'w') as f:
            f.write(name)
    except FileNotFoundError:
        file = open("name.txt", 'w')
        file.write(name)


def say_hello():

    if os.path.exists("name.txt"):
        with open("name.txt") as f:
            for name in f:
                talk(f"Hola, bienvenido {name}")
    else:
        give_me_name()


def thread_hello():
    t = tr.Thread(target=say_hello)
    t.start()


thread_hello()


button_voice_mx = Button(main_window, text="Voz Español", fg="white", bg="#45a247",
                         font=("Arial", 10, "bold"), command=mexican_voice)
button_voice_mx.place(x=800, y=100, width=150, height=40)
button_voice_us = Button(main_window, text="Voz USA", fg="white", bg="#4286f4",
                         font=("Arial", 10, "bold"), command=english_voice)
button_voice_us.place(x=800, y=155, width=150, height=40)
button_listen = Button(main_window, text="Escuchar", fg="white", bg="#1565C0",
                       font=("Arial", 15, "bold"), width=30, height=1, command=run_walle)
button_listen.pack(side=BOTTOM, pady=10)
button_speak = Button(main_window, text="Hablar", fg="white", bg="#0083B0",
                      font=("Arial", 10, "bold"), command=read_and_talk)
button_speak.place(x=800, y=205, width=150, height=40)

button_add_files = Button(main_window, text="Agregar archivos", fg="white", bg="#4286f4",
                          font=("Arial", 10, "bold"), command=open_w_files)
button_add_files.place(x=800, y=260, width=150, height=40)
button_add_apps = Button(main_window, text="Agregar apps", fg="white", bg="#4286f4",
                         font=("Arial", 10, "bold"), command=open_w_apps)
button_add_apps.place(x=800, y=310, width=150, height=40)
button_add_pages = Button(main_window, text="Agregar páginas", fg="white", bg="#4286f4",
                          font=("Arial", 10, "bold"), command=open_w_pages)
button_add_pages.place(x=800, y=360, width=150, height=40)

button_add_contacts = Button(main_window, text="Agregar contactos", fg="white", bg="#4286f4",
                          font=("Arial", 10, "bold"), command=open_w_contacts)
button_add_contacts.place(x=800, y=410, width=150, height=40)


#botones de agragregacion bonones
button_tell_pages = Button(main_window, text="Páginas agregadas", fg="white", bg="#2c3e50",
                           font=("Arial", 8, "bold"), command=talk_pages)
button_tell_pages.place(x=300, y=450, width=150, height=40)
button_tell_apps = Button(main_window, text="Apps agregadas", fg="white", bg="#2c3e50",
                          font=("Arial", 8, "bold"), command=talk_apps)
button_tell_apps.place(x=550, y=450, width=150, height=40)
button_tell_files = Button(main_window, text="Archivos agregados", fg="white", bg="#2c3e50",
                           font=("Arial", 8, "bold"), command=talk_files)
button_tell_files.place(x=300, y=500, width=150, height=40)

button_tell_files = Button(main_window, text="Contactos agregados", fg="white", bg="#2c3e50",
                           font=("Arial", 8, "bold"), command=talk_contacts)
button_tell_files.place(x=550, y=500, width=150, height=40)

main_window.mainloop()
