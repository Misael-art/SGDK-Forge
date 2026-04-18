# script para redimenssionar imagens e converter para o formato de cores megadrive (16 cores) SGDK
# originalmente : O incrível script criado por Paulo Linhares
# pip install opencv-python
# conda install freetype --force-reinstall
#(type) CTRL + SHIFT + P
#(search for:) open settings
#(click:) Preferences: Open Settings (JSON)
# ---------------------------------------------------------#
from turtle import left
import cv2
import os
import numpy as np
from PIL import Image
import copy
import platform
import tkinter as tk
from tkinter import *
#from matplotlib import pyplot as plt
#from matplotlib import pyplot as plt
#from matplotlib import image 
# ---------------------------------------------------------#
# limpar terminal antes de executar 
print("\n" * os.get_terminal_size().lines)
#   Formatação de cores para o Print no terminal 
reset_color = '\033[0m'
red = '\033[1;31;40m'
green = '\033[1;32;40m'
yellow = '\033[1;33;40m'
blue = '\033[1;34;40m'
magenta = '\033[1;35;40m'
cyan = '\033[1;36;40m'
# INFORMAÇÕES INICIAIS DO ESCRIPT EXECUTADO
print(cyan + '*---      INFO SCRIPT :   ', os.path.basename(__file__).split('.')[0].upper(), '     ----------------------------*' + reset_color)
print(magenta + '|      Sistema Operacional :' + reset_color, cyan + os.name.upper() + reset_color)
print(magenta + '|      Arquitetura do Sistema :' + reset_color, cyan + platform.architecture()[0].upper() + reset_color)
print(magenta + '|      Sript excutado :     ' + reset_color, yellow +  os.path.basename(__file__) + reset_color)
print(magenta + '|      Localização :        ' + reset_color,  yellow +  (__file__) + reset_color)
print(cyan + '*-----------------------------------------------------------------*' + reset_color)
# ---------------------------------------------------------#
# Localização do diretório ROOT
if os.path.exists("\\".join(((os.path.realpath(__file__)).split('\\', 7)[0:-1])) + '\\core'):
    ROOT = "\\".join(((os.path.realpath(__file__)).split('\\', 7)[0:-1]))
if os.path.exists("\\".join(((os.path.realpath(__file__)).split('\\', 6)[0:-1])) + '\\core'):
    ROOT = "\\".join(((os.path.realpath(__file__)).split('\\', 6)[0:-1]))
if os.path.exists("\\".join(((os.path.realpath(__file__)).split('\\', 5)[0:-1])) + '\\core'):
    ROOT = "\\".join(((os.path.realpath(__file__)).split('\\', 5)[0:-1]))
if os.path.exists("\\".join(((os.path.realpath(__file__)).split('\\', 4)[0:-1])) + '\\core'):
    ROOT = "\\".join(((os.path.realpath(__file__)).split('\\', 4)[0:-1]))
if os.path.exists("\\".join(((os.path.realpath(__file__)).split('\\', 3)[0:-1])) + '\\core'):
    ROOT = "\\".join(((os.path.realpath(__file__)).split('\\', 3)[0:-1]))
if os.path.exists("\\".join(((os.path.realpath(__file__)).split('\\', 2)[0:-1])) + '\\core'):
    ROOT = "\\".join(((os.path.realpath(__file__)).split('\\', 2)[0:-1]))
elif str(os.path.exists(os.path.realpath(__file__))) + '\\core':
    ROOT = os.path.dirname(os.path.abspath(__file__))
else:
    print(u'Diretório ROOT não encontrado!')
    exit()
# -----------------------------------------------------------------#
pastaApp = ROOT

# ---------------------------------------------------------#
# App será o Pai do programa
app=tk.Tk()
app.title("Convert_image_for_genesis")
app.geometry("356x240")
#app.resizable(False, False)
app.configure(background='#FF00FF')
# ---------------------------------------------------------#
# Coleta de imagens
img=PhotoImage(file=pastaApp+'\\cuphead_idle_0001.png')
Sprite = Label(app, image=img)
Sprite.place(x=0, y=0)
Sprite.pack()
# ---------------------------------------------------------#
# coletar informações da imagem
img = cv2.imread(pastaApp+'\\cuphead_idle_0001.png')
height, width, channels = img.shape

# set 
background_color = imgs[0][0][0]
autodetect_backgroud_color: bool = True
#tamanho_padding = 1000
tamanho_padding = 1000
numero_de_cores = 16
limitar_cores = True

def limit_colors(img, numero_de_cores):
  img = img.astype(np.int32)
  img[img > numero_de_cores] = numero_de_cores
  img[img < 0] = 0
  return img.astype(np.uint8)

def concat_img(imgs):
  return cv2.hconcat(imgs)

def change_bg(img):
  if not np.all([ 255, 0, 255] == background_color):
    return modify_color(img, background_color, [ 255, 0, 255])
  return img
                                          
def convert_colors(image, k):
    i = np.float32(image).reshape(-1,3)
    condition = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,20,1.0)
    ret,label,center = cv2.kmeans(i, k , None, condition,10,cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    final_img = center[label.flatten()]
    final_img = final_img.reshape(image.shape)
    return final_img

def count_colors(img):
  unique, counts   = np.unique(img.reshape(-1, img.shape[-1]), axis=0, return_counts=True)
  return len(counts)

def modify_color(img, color_before, color_after):
  color_change = np.copy(img)
  for i in range(len(img)):
        for j in range(len(img[i])):
            if np.all(img[i][j] == color_before):
              color_change[i][j] = color_after
  return color_change

def get_pallet(img):
  unique, counts   = np.unique(img.reshape(-1, img.shape[-1]), axis=0, return_counts=True)
  pal = np.full((20, 1, 3), [0, 0, 0], dtype=np.uint8)
  for color in unique:
    pixel_array = np.full((20, 20, 3), color, dtype=np.uint8)
    pal = np.concatenate((pal, pixel_array), axis=1)
  return unique, pal

def save_result2(img, name, sprinte_count):
  if not os.path.exists('/content/output/'):
    os.makedirs('/content/output/')
  # cv2.imwrite('/content/output/' + str(name) + '.png', img)


def save_8bpp(img, name):
  if not os.path.exists('/content/output/'):
    os.makedirs('/content/output/')
  img_path = '/content/output/' + str(name) + '.png'

  img = img_to_gen(img)

  img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  img = Image.fromarray(img)
  palette = convert_palette(img)
  if 768 % len(palette) != 0:
    raise Exception('error', 'invalid palette size')
  
  scale = 768//len(palette)
  
  img1 = img.convert(mode='RGB')

  p_img = Image.new('P', (16, 16))
  p_img.putpalette(palette*scale)
  conv = img1.quantize(palette=p_img, dither=0)
  conv.save(img_path)
  return conv

def convert_1d_to_2d(l, cols):
    return [l[i:i + cols] for i in range(0, len(l), cols)]

def convert_palette(img):
  img = img.quantize()
  unique = convert_1d_to_2d(img.getpalette(),3)
  buffer = copy.copy(unique[0])
  k = 0
  for i in range(len(unique)):
    if np.all(unique[i] == [0xe0, 0x0, 0xe0]):
      unique[i] = buffer
      k = k + 1
  if k > 0:
    unique[0] = [0xe0, 0x0, 0xe0]

  unique = [j for sub in unique for j in sub]
  return unique


def get_gen_color(r, g, b):
  VDPPALETTE_REDMASK=0x000E
  VDPPALETTE_GREENMASK=0x00E0
  VDPPALETTE_BLUEMASK=0x0E00
  RGBPALETTE_REDMASK=0xFF0000
  RGBPALETTE_GREENMASK=0xff00
  RGBPALETTE_BLUEMASK=0xFF

  color = (r << 16) & RGBPALETTE_REDMASK | (g << 8) & RGBPALETTE_GREENMASK | b & RGBPALETTE_BLUEMASK

  color = (((color >> (20)) & VDPPALETTE_REDMASK) | ((color >> ((1 * 4) + 4)) & VDPPALETTE_GREENMASK) | ((color << 4) & VDPPALETTE_BLUEMASK))

  color = (((color & VDPPALETTE_REDMASK) << 20 ) | ((color & VDPPALETTE_GREENMASK) << 8 ) | ((color & VDPPALETTE_BLUEMASK)>> 4 ))

  r = color >> 16 & 0xFF
  g = color >>8 & 0xFF
  b = color & 0xFF
  return r, g, b

def img_to_gen(img):
  img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  for i in range(len(img2)):
    for j in range(len(img2[i])):
      img2[i][j] = img2[i][j] & 0xe0e0e0

  img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2BGR)
  return img2


def add_padding(imgs, size):
  imgs2=[]
  for imgl in imgs:
    for img in imgl:
        print(img, type(img), 'img')
        print(size, type(size), 'size')
        #print(img.shape)
        #imgs2.append(cv2.copyMakeBorder(img, size, size, size, size, cv2.BORDER_CONSTANT, value=(0, 0, 0)))
        imgs2.append(cv2.copyMakeBorder(img.copy(), size, size, size, size, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0)))

  return imgs2


if autodetect_backgroud_color:
  background_color = img[0][0][0]
if tamanho_padding > 0:
  imgs = add_padding(img, tamanho_padding)

def crop_images(imgs, xmin, xmax, ymin, ymax):
  imgs_crop = []
  if ymin < 0:
    pixel_array = np.full((-ymin, xmax-xmin, 3), background_color, dtype=np.uint8)
    for img in imgs:
      img = cv2.vconcat(pixel_array, img)
    ymax = ymax - ymin
    ymin = 0  
  ximg = tuple(imgs[0].shape[1::-1])[0]
  if xmax > ximg:
    pixel_array = np.full((ymax - ymin, xmax-ximg, 3), background_color, dtype=np.uint8)
    for img in imgs:
      img = cv2.hconcat(img, pixel_array)     
  for img in imgs:
    imgs_crop.append(img[ymin:ymax, xmin:xmax])
  return imgs_crop

def change_bg(img):
  if not np.all([ 255, 0, 255] == background_color):
    return modify_color(img, background_color, [ 255, 0, 255])
  return img

def find_bounds(imgs):
  xmin =len(imgs[0][0])
  xmax = 0
  ymin =len(imgs[0])
  ymax = 0
  for img in imgs:
    for i in range(len(img)):
      for j in range(len(img[i])):
          if not np.all(img[i][j] == background_color):
            if j < xmin:
              xmin = j
            if j > xmax:
              xmax = j
            if i < ymin:
              ymin = i
            if i > ymax:
              ymax = i
  return xmin, xmax+1, ymin, ymax+1
print(cyan + '*---      INFO IMAGEM :   ', os.path.basename(__file__).split('.')[0].upper(), '     ----------------------------*' + reset_color)
print(magenta + '|      Altura :' + reset_color, cyan + str(height) + reset_color)
print(magenta + '|      Largura :' + reset_color, cyan + str(width) + reset_color)
print(magenta + '|      Canais :' + reset_color, cyan + str(channels) + reset_color)
print(cyan + '*-----------------------------------------------------------------*' + reset_color)

# ---------------------------------------------------------#


# funções do checkbutton
def convert_tiles ( min, max, x_y = 'x'):
  if (max - min) % 8 != 0:
    if x_y == 'x':
      max = max + 8 - (max - min) % 8
    else:
      min = min - 8+ (max - min) % 8
  if x_y == 'x':
    return max
  else:
    return min
# ---------------------------------------------------------#
# exucutar funções do checkbutton
xmin, xmax, ymin, ymax = find_bounds(img)
xmax = convert_tiles(xmin, xmax, 'x')
ymin = convert_tiles(ymin, ymax, 'y')
print(find_bounds(imgs), 'find_bounds(imgs)')
#  
# ---------------------------------------------------------#
# formação dos quadros filhos
quadro1=Frame(app, width=95, height=256, bg='#C0C0C0')
quadro1.place(x=0, y=0)
# ---------------------------------------------------------#
quadro2=Frame(app, width=5, height=256, bg='#DCDCDC')
quadro2.place(x=95, y=0)
#CHECKBUTTONS
var1=IntVar()
ajust_size=Checkbutton(app, text="Convert tiles", variable=var1, onvalue=1, offvalue=0, command=convert_tiles)
ajust_size.pack(side=LEFT)


app.mainloop()