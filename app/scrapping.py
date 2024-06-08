from selenium.webdriver import Chrome  # for typing in parameters
from pynput import keyboard, mouse  # for typing and constants
from typing import Tuple, Any  # for typing
from pathlib import Path  # for home dir
import constants
import platform
import requests  # for handling requests
import time  # for sleeping the program when needed

global pause  # this variable helps to know if the program should continue or not
pause = False

# using Ctrl or Cmd depending on the platform
CTRL_VALUE = keyboard.Key.cmd.value if platform.system() == 'darwin' else keyboard.Key.ctrl.value


def on_press(key: Any):  # when '1' is pressed, then go to the next step
  if str(key)[1] == "1":
    global pause
    pause = False

# makes focus on specific point


def focus(m: mouse.Controller, position: Tuple[int, int]):
  m.position = position  # moves the mouse to the position
  m.press(mouse.Button.left)  # press left click
  m.release(mouse.Button.left)  # release left click


# makes a pause until variables 'pause' has changed
def make_pause():
  global pause
  pause = True
  while pause:
    pass

# makes a ctrl + v command


def hotKey(m: mouse.Controller, k: keyboard.Controller, position: Tuple[int, int], key: str | keyboard.Key | keyboard.KeyCode):
  focus(m, position)  # focus the input
  time.sleep(0.5)  # some time while focusing
  # pressing ctrl + v
  k.press(CTRL_VALUE)
  k.press(key)
  k.release(key)
  k.release(CTRL_VALUE)


def open_window(dr: Chrome, url: str):  # opens a new window
  dr.execute_script(f'window.open("{url}")')


def switch_window(dr: Chrome):  # switch to the last window
  dr.switch_to.window(dr.window_handles[-1])


def createCard(word: str, dr: Chrome, m: mouse.Controller, k: keyboard.Controller):
  # STEP 1 -- Write the word on Anki
  focus(m, constants.positions["word"])
  time.sleep(0.5)  # some time while focusing input
  k.type(word)

  # STEP 2 -- Open translators for meanings
  open_window(dr, f'https://www.deepl.com/es/translator#en/es/{word}')
  open_window(dr, f'https://translate.google.com/?hl=es&sl=en&tl=es&text={word}&op=translate')

  l = keyboard.Listener(on_press=on_press)
  l.start()  # starts keyboard listener

  # STEP 3 -- Write the meaning (manually)
  make_pause()

  # STEP 4 -- Close the translators
  switch_window(dr)
  dr.close()
  switch_window(dr)
  dr.close()

  # STEP 5 -- Write the word on ChatGPT
  #time.sleep(2)  # some time while closing translators tabs

  #focus(m, constants.positions["chatgpt"])  # focuses the ChatGPT input
  #time.sleep(0.2)  # some time while focusing input
  #k.type(f'word: {word}')
  #k.press(keyboard.Key.enter.value)
  #k.release(keyboard.Key.enter.value)

  # pause while ChatGPT processes the result
  make_pause()

  # STEP 6 -- Write the IPA, example, example meaning and synonyms on Anki

  # focuses Anki Tab
  focus(m, constants.positions["IPA"])
  time.sleep(0.3)  # some time while focusing Anki tab
  m.scroll(0, -10)  # scroll down
  time.sleep(0.5)  # some time while scrolling

  hotKey(m, k, constants.positions["IPA"], 'v')  # pastes IPA in its corresponding field
  make_pause()  # pause while copying example

  hotKey(m, k, constants.positions["example"], 'v')  # pastes example in its corresponding field
  make_pause()  # pause while copying example meaning

  # pastes example meaning in its corresponding field
  hotKey(m, k, constants.positions["meaning"], 'v')
  make_pause()  # pause thile copying synonyms

  # pastes the synonyms in its corresponding field
  hotKey(m, k, constants.positions["synonyms"], 'v')
  time.sleep(1)

  # STEP 7 - look for image and audio for the card

  switch_window(dr)
  open_window(dr, f'https://www.google.com/search?q={word}&udm=2')  # opens image results

  sw = False  # bool to know if the mp3 could not be downloaded
  # makes the requests to Google for the pronunciation of the word
  r = requests.get(
    f'https://ssl.gstatic.com/dictionary/static/pronunciation/2022-03-02/audio/{word[:2]}/{word}_en_us_1.mp3')
  if r.status_code == 200:  # if status is 200, then write the file into Downdloads
    with open(f'{Path.home()}/Downloads/{word}_en_us_1.mp3', 'wb') as file_stream:
      file_stream.write(r.content)
      print(f'mp3 file of word: {word} downloaded succesfully')
  else:  # if mp3 could not be downloaded, then search for audios on the web
    sw = True
    print(f'Failed to download mp3 file from Google - Word: {word}')
    open_window(dr, 'https://www.naturalreaders.com/online/')

  make_pause()  # pause while choosing image and audio

  # STEP 8 -- closing image and audio tabs

  switch_window(dr)
  dr.close()
  if sw:  # closing audio tab only if it was created
    dr._switch_to.window(dr.window_handles[-1])
    dr.close()

  switch_window(dr)  # switch to ChatGPT window again

  # STEP 9 -- Add the card to the deck

  # focus example field (it could be any part of the anki window)
  focus(m, constants.positions["example"])
  time.sleep(0.5)  # some time while focusing
  # pressing ctrl + Enter for adding the card
  k.press(CTRL_VALUE)
  k.press(keyboard.Key.enter.value)
  k.release(keyboard.Key.enter.value)
  k.release(CTRL_VALUE)

  time.sleep(0.2)  # some time while saving the card
  m.scroll(0, 10)  # scroll up to the first field again
  l.stop()  # stops keyboard listener

  time.sleep(0.5)  # sleeps 1 second before next word
  # click 3 times the word input
  focus(m, constants.positions["word"])
  hotKey(m, k, constants.positions["word"], keyboard.Key.backspace)
