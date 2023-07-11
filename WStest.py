import board
import neopixel
import time


detectlights = 100

pixels = neopixel.NeoPixel(board.D18, detectlights, brightness=1)

for a in range (0,10):
    pixels.fill((0,0,0))
    time.sleep(2)
    pixels.fill((0,0,255))
    time.sleep(2)
    pixels.fill((0,255,0))
    time.sleep(2)
    pixels.fill((0,255,255))
    time.sleep(2)
    pixels.fill((255,0,0))
    time.sleep(2)
    pixels.fill((255,0,255))
    time.sleep(2)
    pixels.fill((255,255,0))
    time.sleep(2)
    pixels.fill((255,255,255))
    time.sleep(2)

        

