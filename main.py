from js import handTrack, setTimeout, requestAnimationFrame, player, document, console
from pyodide import create_once_callable
import asyncio

video = document.getElementById("video")
canvas = document.getElementById("canvas")
update_note = document.getElementById("update_note")
context = canvas.getContext("2d")

isVideo = False
model = None
last_position = 0
direction = "stop"

modelParams = {
  "flipHorizontal": True,
  "maxNumBoxes": 20,
  "iouThreshold": 0.5,
  "scoreThreshold": 0.6,
}

def toggle_video(evt=None):
  global isVideo
  player.jump()

  if not isVideo:
    update_note.innerText = "Starting video"
    pyscript.run_until_complete(start_video())
  else:
    update_note.innerText = "Stopping video"
    handTrack.stopVideo(video)
    isVideo = False
    update_note.innerText = "Video stopped"

async def start_video():
  global isVideo
  update_note.innerText = "Initializing video..."
  status = await handTrack.startVideo(video)
  if status:
    update_note.innerText = "Video started. Tracking gestures..."
    isVideo = True
    await run_detection()
  else:
    update_note.innerText = "Please enable webcam permissions."

def sync_run_detection(evt=None):
  pyscript.run_until_complete(run_detection())

async def run_detection():
  global model, isVideo, last_position, direction

  predictions = await model.detect(video)
  model.renderPredictions(predictions, canvas, context, video)

  if predictions:
    curr_position = predictions[0].bbox[0] + (predictions[0].bbox[2] / 2)
    delta = last_position - curr_position
    last_position = curr_position

    if abs(delta) < 2:
      direction = "stop"
    elif delta > 0:
      direction = "left"
    else:
      direction = "right"

    for prediction in predictions:
      if prediction.label == 'open':
        player.jump()
      elif prediction.label == 'close':
        player.crouch()

  if isVideo:
    await requestAnimationFrame(create_once_callable(sync_run_detection))

def handle_model(lmodel):
  global model
  model = lmodel
  update_note.innerText = "Model loaded. Ready!"

async def start():
  model = await handTrack.load(modelParams)
  handle_model(model)

pyscript.run_until_complete(start())
