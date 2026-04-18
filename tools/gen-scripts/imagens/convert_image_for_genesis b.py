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


# criar tela do tkinter e componentes para escolher imagens 
app=tk.Tk()
app.title("Convert Image for Genesis")
text = tk.Text(app, height=12)
text.grid(column=0, row=0, sticky='nsew')
app.geometry("800x600")
app.resizable(False, False)
app.configure(background='#FF00FF')

ent1=tk.Entry(app,font=40)
ent1.grid(row=2,column=2)

def open_img_file():
    img_file = fd.askopenfilename(filetypes=(("images files", "*.png"), ("All files", "*.*")))
    text.delete("1.0", tk.END)
    text.insert(tk.END, img_file)


def browsefunc():
    filename = tkinter.filedialog.askopenfilename(filetypes=(("tiff files","*.tiff"),("All files","*.*")))
    ent1.insert(tk.END, filename) # add this

filetypes = ( ('images files', '*.png'), ('All files', '*.*') )
f = fd.askopenfile(filetypes=filetypes, initialdir="#Specify the file path")
text.insert('1.0', f.readlines())
open_button = ttk.Button(app, text='Open a File', command=open_text_file)
open_button.grid( sticky='w' , padx=800, pady=600) 

def get_image_one(self):
    # Select image file types, returned image should be used as source of Image widget.
    Tk().withdraw() # avoids window accompanying tkinter FileChooser
    img = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    self.first_image.source = img

def get_image_two(self):
    Tk().withdraw()
    img = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    self.first_image.source = img

#b1=tk.Button(app,text="Imagens",font=40, command=browsefunc)
#b1.grid(row=2,column=4)
app.mainloop()