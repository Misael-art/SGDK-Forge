# programa para selecionar um conjunto de imagens de uma pasta no windows e exibir ela na tela usando o tkinter e opencv. dar opção de escolher o tamanho da imagem, tamanho da janela, palleta  de cores e conversão para o padrão do megadrive.
# autor: Misael Oliveira
# data: 06/08/2022
# versão: 1.0
# licença: GPLv3
#
# dependências: opencv, tkinter, python3

import tkinter
import cv2
import os
import numpy as np
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk

app = tk.Tk()
app.title("Convert Image for Genesis")
app.geometry("800x600")
font1=('times', 10, 'bold')
app.configure(background='#FF00FF')

button_inf_1 = tk.Button(app, text='chose img file', width=15,command = lambda:upload_file())
button_inf_1.grid(row=1,column=1) 
button_inf_1.place(x=0, y=0)

texto_inf_1 = tk.Label(app,text='chose image sprite and add',width=30,font=font1)  
texto_inf_1.grid(row=1,column=1)
texto_inf_1.place(x=130, y=0)

def upload_file():
    global img
    f_types = [('Jpg Files', '*.png'), ('All Files', '*.*')]
    filename = filedialog.askopenfilename(filetypes=f_types)
    img = ImageTk.PhotoImage(file=filename)

    #img=Image.open(filename)
    #img_resized=img.resize((100,100)) # new width & height
    #img=ImageTk.PhotoImage(img_resized)
# Reading width and height of uploaded image and then resizing to maintain aspect ration

    img = Image.open(filename)
    #width, height = img.size  
	#width_new = int(width/3)
	#height_new = int(height/3)
	#img_resized = img.resize((width_new,height_new))

    w, h = img.size 
    wpercent = (w/h)
    hpercent = (h/w)
    print(wpercent, 'wpercent', hpercent, 'hpercent')
    if w > h:
        w = int(hpercent * 100)
        print(w, 'w <<<<<<<<<<<' )
        h = 100
    else:
        h = int(wpercent * 100)
        w = 100
    img = img.resize((w, h), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    label_img = tk.Label(app, image=img)
    label_img.grid(row=1,column=1)
    label_img.place(x=0, y=0)
    label_img.pack()
    label_img.configure(background='#FF00FF')
    label_img.configure(width=w, height=h)
    label_img.configure(borderwidth=0)
    label_img.configure(highlightbackground='#FF00FF')
    label_img.configure(highlightcolor='#FF00FF')
    label_img.configure(relief='flat')
    label_img.configure(anchor='center')
    label_img.configure(justify='center')
    label_img.configure(text=''' ''')
    label_img.configure(compound='center')
    label_img.configure(font=font1)
    label_img.configure(foreground='#FF00FF')
    label_img.configure(background='#FF00FF')
    label_img.configure(disabledforeground='#FF00FF')
    label_img.configure(disabledbackground='#FF00FF')
    label_img.configure(cursor='fleur')
    label_img.configure(takefocus=True)
    label_img.configure(state='normal')
    label_img.configure(highlightthickness=1)
    label_img.configure(wraplength=None)
    label_img.configure(justify='left')


    button_inf_2 =tk.Button(app,image=img) # using Button 
    button_inf_2.grid(row=3,column=1)
    button_inf_2.place(x=500, y=300)
    button_inf_2.configure(background='#FF00FF')

    Sprite =tk.Button(app,image=img) # using Button 
    Sprite.grid(row=3,column=1)
    Sprite.place(x=0, y=50)
    Sprite.pack()


app.mainloop()  # Keep the window open