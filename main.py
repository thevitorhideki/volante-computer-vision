#!/usr/bin/python
# -*- coding: utf-8 -*-

# Programa simples com camera webcam e opencv que emula precionamento de teclas

import cv2
import os,sys, os.path
import numpy as np

#importes para emular precionamento de teclas
from pynput.keyboard import Key, Controller
import pynput
import time
import random

keys = [
    Key.up,                                 # UP
    Key.down,                               # DOWN
    Key.left,                               # LEFT
    Key.right,                              # RIGHT
    # pynput.keyboard.KeyCode.from_char('S'),  # A
    # pynput.keyboard.KeyCode.from_char('W'),  # B
    # pynput.keyboard.KeyCode.from_char('a'),  # X
    #Key.enter,                              # START
    #Key.shift_r,                            # SELECT
]

#Inicializa o controle 
keyboard = Controller()

#filtro baixo
red_lower_hsv1 = np.array([160,130,120])
red_upper_hsv1 = np.array([180,205,255])
#filtro alto
red_lower_hsv2 = np.array([0,130,120])
red_upper_hsv2 = np.array([10,205,255])

blue_lower_hsv = np.array([100, 130, 70])
blue_upper_hsv = np.array([130, 205, 255])

def filtro_de_cor(img_bgr, low_hsv, high_hsv):
    """ retorna a imagem filtrada """
    img = cv2.cvtColor(img_bgr,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img, low_hsv, high_hsv)
    return mask 

def mascara_or(mask1, mask2):

    """ retorna a mascara or"""
    mask = cv2.bitwise_or(mask1, mask2)
    return mask

def mascara_and(mask1, mask2):
     """ retorna a mascara and"""
     mask = cv2.bitwise_and(mask1, mask2)
     
     return mask

def desenha_cruz(img, cX,cY, size, color):
     """ faz a cruz no ponto cx cy"""
     cv2.line(img,(cX - size,cY),(cX + size,cY),color,5)
     cv2.line(img,(cX,cY - size),(cX, cY + size),color,5)    

def escreve_texto(img, text, origem, color):
     """ faz a cruz no ponto cx cy"""
 
     font = cv2.FONT_HERSHEY_SIMPLEX
     
     cv2.putText(img, str(text), origem, font,1,color,2,cv2.LINE_AA)

def contornos(mask):
    """ retorna a lista de contornos"""
    contornos, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    
    maior = None
    maior_area = 0
    for c in contornos:
        area = cv2.contourArea(c)
        
        if area > maior_area:
            maior_area = area
            maior = c
    
    M = cv2.moments(maior)
    
    # Verifica se existe alguma para calcular, se sim calcula e exibe no display
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        
        # cv2.drawContours(contornos_img, [maior], -1, [255, 0, 0], 5)
       
        #faz a cruz no centro de massa

        
        # Para escrever vamos definir uma fonte 
        # texto = cY , cX
        # origem = (0,50)
        # escreve_texto(contornos_img, texto, origem, (0,255,0))
            
    else:
    # se não existe nada para segmentar
        cX, cY = 0, 0
        # Para escrever vamos definir uma fonte 
        texto = ' '
        origem = (0,50)
        # escreve_texto(contornos_img, texto, origem, (0,0,255))
        
    return cX, cY

def image_da_webcam(img):
    """
    ->>> !!!! FECHE A JANELA COM A TECLA ESC !!!! <<<<-
        deve receber a imagem da camera e retornar uma imagems filtrada.
    """  
    mask_hsv_blue = filtro_de_cor(img, blue_lower_hsv, blue_upper_hsv)
    
    mask_hsv_red1 = filtro_de_cor(img, red_lower_hsv1, red_upper_hsv1)
    mask_hsv_red2 = filtro_de_cor(img, red_lower_hsv2, red_upper_hsv2)
    mask_hsv = mascara_or(mask_hsv_red1, mask_hsv_red2)

    # contornos_img_red = contornos(mask_hsv)[0]
    cXr, cYr = contornos(mask_hsv)
    # contornos_img_blue = contornos(mask_hsv_blue)[0]
    cXb, cYb = contornos(mask_hsv_blue)
    # img = cv2.bitwise_or(contornos_img_red, contornos_img_blue)
    
    return cXr, cYr, cXb, cYb

cv2.namedWindow("original")
# define a entrada de video para webcam
vc = cv2.VideoCapture(0)

#vc = cv2.VideoCapture("video.mp4") # para ler um video mp4 

#configura o tamanho da janela 
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    webcam = image_da_webcam(frame)
    cXr, cYr, cXb, cYb = webcam
    angulo = np.rad2deg(np.arctan2(cYr - cYb, cXr - cXb))
    cv2.line(frame, (cXr, cYr), (cXb, cYb), (255, 255, 255), 5)

    if angulo <= -20:
        keyboard.press(Key.right)
        time.sleep(0.1)
        keyboard.release(Key.right)
        print('direita')
    elif angulo >= 20:
        keyboard.press(Key.left)
        time.sleep(0.1)
        keyboard.release(Key.left)
        print('esquerda')
    else:
        keyboard.press(Key.up)
        time.sleep(0.1)
        keyboard.release(Key.up)
        print('frente')

    #cv2.imshow("preview", img)
    cv2.imshow("original", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("original")
vc.release()
