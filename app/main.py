import scrapping
from selenium import webdriver
from pynput import mouse, keyboard
import time


def run():
  with open('docs/oxford-american-english-B2.txt', 'r') as file:
    for line in file:
      l = line.strip()
      scrapping.createCard(l)


if __name__ == '__main__':
  dr = webdriver.Chrome()
  #dr.get('https://chatgpt.com/')
  dr.get('https://google.com')

  m = mouse.Controller() 
  k = keyboard.Controller()
  time.sleep(2)
  scrapping.createCard('focus', dr, m, k)
  # run()
