import keyboard
import time
from selenium.webdriver import Chrome
from pynput import keyboard, mouse

global pause
pause = False


def on_press(key):
  if str(key)[1] == "1":
    global pause
    pause = False


def CtrlV(m: mouse.Controller, k: keyboard.Controller, p):
  m.position = p  # IPA
  m.press(mouse.Button.left)
  m.release(mouse.Button.left)
  time.sleep(1)
  k.press(keyboard.Key.ctrl.value)
  k.press('v')
  k.release('v')
  k.release(keyboard.Key.ctrl.value)


def createCard(word: str, dr: Chrome, m: mouse.Controller, k: keyboard.Controller):
  # STEP 1 -- Write the word on Anki
  m.position = (2444, 375)
  m.press(mouse.Button.left)
  m.release(mouse.Button.left)
  time.sleep(1)  # some time while focusing input
  k.type(word)

  # STEP 2 -- Open translators for meanings
  dr.execute_script(f'window.open("https://www.deepl.com/es/translator#en/es/{word}")')
  dr.execute_script(
    f'window.open("https://translate.google.com/?hl=es&sl=en&tl=es&text={word}&op=translate")')

  l = keyboard.Listener(on_press=on_press)
  l.start()

  # STEP 3 -- Write the meaning (manually)
  global pause
  pause = True
  while pause:
    pass

  # closing the translator
  dr.switch_to.window(dr.window_handles[-1])
  dr.close()
  dr._switch_to.window(dr.window_handles[-1])
  dr.close()

  # STEP 4 -- Write the word on ChatGPT
  time.sleep(2)

  m.position = (780, 980)
  m.press(mouse.Button.left)
  m.release(mouse.Button.left)
  k.type(f'word: {word}')
  k.press(keyboard.Key.enter.value)
  k.release(keyboard.Key.enter.value)

  # pause while ChatGPT process the result, then copy IPA
  pause = True
  while pause:
    pass

  CtrlV(m, k, (2440, 490))  # IPA

  pause = True
  while pause:
    pass

  CtrlV(m, k, (2440, 572))  # example

  pause = True
  while pause:
    pass

  CtrlV(m, k, (2440, 640))  # example meaning

  pause = True
  while pause:
    pass

  CtrlV(m, k, (2440, 720))  # synonyms

  pause = True
  while pause:
    pass
