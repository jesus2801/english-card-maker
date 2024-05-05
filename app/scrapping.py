from selenium.webdriver import Chrome
from pynput import keyboard, mouse
from pathlib import Path
import requests
import time
from typing import Tuple, Any

global pause
pause = False


def on_press(key: Any):
  if str(key)[1] == "1":
    global pause
    pause = False


def focus(m: mouse.Controller, position: Tuple[int, int]):
  m.position = position
  m.press(mouse.Button.left)
  m.release(mouse.Button.left)


def make_pause():
  global pause
  pause = True
  while pause:
    pass


def CtrlV(m: mouse.Controller, k: keyboard.Controller, position: Tuple[int, int]):
  focus(m, position)
  time.sleep(0.5)
  k.press(keyboard.Key.ctrl.value)
  k.press('v')
  k.release('v')
  k.release(keyboard.Key.ctrl.value)


def open_window(dr: Chrome, url: str):
  dr.execute_script(f'window.open("{url}")')


def switch_window(dr: Chrome):
  dr.switch_to.window(dr.window_handles[-1])


def createCard(word: str, dr: Chrome, m: mouse.Controller, k: keyboard.Controller):
  # STEP 1 -- Write the word on Anki
  focus(m, (2444, 375))
  time.sleep(1)  # some time while focusing input
  k.type(word)

  # STEP 2 -- Open translators for meanings
  open_window(dr, f'https://www.deepl.com/es/translator#en/es/{word}')
  open_window(dr, f'https://translate.google.com/?hl=es&sl=en&tl=es&text={word}&op=translate')

  l = keyboard.Listener(on_press=on_press)
  l.start()

  # STEP 3 -- Write the meaning (manually)
  make_pause()

  # closing the translator
  switch_window(dr)
  dr.close()
  switch_window(dr)
  dr.close()

  # STEP 4 -- Write the word on ChatGPT
  time.sleep(2)

  focus(m, (780, 980))
  time.sleep(0.2)
  k.type(f'word: {word}')
  k.press(keyboard.Key.enter.value)
  k.release(keyboard.Key.enter.value)

  # pause while ChatGPT process the result, then copy IPA
  make_pause()

  focus(m, (2440, 490))
  time.sleep(0.3)
  m.scroll(0, -10)
  time.sleep(0.5)

  CtrlV(m, k, (2440, 490))  # IPA
  make_pause()

  CtrlV(m, k, (2440, 572))  # example
  make_pause()

  CtrlV(m, k, (2440, 640))  # example meaning
  make_pause()

  CtrlV(m, k, (2440, 720))  # synonyms
  make_pause()

  switch_window(dr)
  open_window(dr, f'https://www.google.com/search?q={word}&udm=2')

  sw = False
  r = requests.get(f'https://ssl.gstatic.com/dictionary/static/pronunciation/2022-03-02/audio/{word[:2]}/{word}_en_us_1.mp3')
  if r.status_code == 200:
    with open(f'{Path.home()}/Downloads/{word}_en_us_1.mp3', 'wb') as file_stream:
      file_stream.write(r.content)
      print(f'mp3 file of word: {word} downloaded succesfully')
  else:
    sw = True
    print(f'Failed to download mp3 file from Google - Word: {word}')
    open_window(dr, f'https://www.google.com/search?q={word}+pronunciation+in+english')

  make_pause()

  switch_window(dr)
  dr.close()
  if sw:
    dr._switch_to.window(dr.window_handles[-1])
    dr.close()

  switch_window()

  focus(m, (2440, 572))  # example
  time.sleep(0.5)
  k.press(keyboard.Key.ctrl.value)
  k.press(keyboard.Key.enter.value)
  k.release(keyboard.Key.enter.value)
  k.release(keyboard.Key.ctrl.value)

  time.sleep(0.2)
  m.scroll(0, 10)

  time.sleep(1)
