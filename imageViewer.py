import sys
import PIL
import watchdog
from pathlib import Path
from pathlib import PurePath
from PIL import Image
from PIL import ImageTk
from tkinter import Tk
from tkinter import Label

from watchdog import events
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from threading import Timer

if len(sys.argv) < 2:
  print("Usage imageViewer.py image.XXXX")
  sys.exit(1)

imageFilename = Path(sys.argv[1])
if not imageFilename.exists():
  print("Image file does not exist.")
  sys.exit(1)

changeTimer = None

def changeImageSize(newSize):
  global image
  global label
  newImage = ImageTk.PhotoImage(image.resize(newSize, PIL.Image.NEAREST))
  label.configure(width=newSize[0], height=newSize[1], image=newImage)
  label.image = newImage
  window.geometry("{}x{}".format(newSize[0], newSize[1]))

def plusPressed(event):
  global imageSize
  imageSize = (imageSize[0] * 2, imageSize[1] * 2)
  changeImageSize(imageSize)
  print("pressed {}".format(repr(event.char)))

def minusPressed(event):
  global imageSize
  imageSize = (int(imageSize[0] / 2), int(imageSize[1] / 2))
  changeImageSize(imageSize)
  print("pressed {}".format(repr(event.char)))

def refreshImage():
  global imageFilename
  global image
  global changeTimer
  changeTimer = None
  image = Image.open(imageFilename)
  changeImageSize(imageSize)
  print("Refreshed!")

class FileChangedHandler:
  def __init__(self, filename):
    self.filename = filename

  def dispatch(self, filename):
    if filename.event_type != "modified":
      return

    global changeTimer

    assert hasattr(filename, "src_path"), "Event doesn't have src_path!"
    if PurePath(filename.src_path) == PurePath(self.filename):
      if changeTimer is not None:
        changeTimer.cancel()

      changeTimer = Timer(0.1, refreshImage)
      changeTimer.start()

def mainWindow():
  global imageSize
  global image
  global label
  global window
  global observer
  global fileChangedHandler

  window = Tk()
  window.title(imageFilename)
  
  print("Loading {}...".format(imageFilename))
  
  image = Image.open(imageFilename)
  aspectRatio = image.size[ 0 ] / image.size[ 1 ]
  print("AR {}".format(aspectRatio))
  
  imageSize = (200, int(200 / aspectRatio))
  photo = ImageTk.PhotoImage(image.resize(imageSize, PIL.Image.NEAREST))
  
  label = Label(image=photo)
  label.image = photo
  label.pack()
  
  window.geometry("{}x{}".format(imageSize[0], imageSize[1]))
  window.bind("<+>", plusPressed)
  window.bind("<minus>", minusPressed)

  observer = watchdog.observers.Observer()
  fileChangedHandler = FileChangedHandler(imageFilename)
  observer.schedule(fileChangedHandler, str(imageFilename.parent), recursive=False)
  observer.start()

  window.mainloop()


mainWindow()
