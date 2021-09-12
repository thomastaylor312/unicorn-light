#!/usr/bin/env python3

from flask import Flask
from flask import request
import colorsys
import unicornhat

app = Flask(__name__)
DEFAULT_BRIGHTNESS = 0.3
DEFAULT_COLOR = (255, 255, 255)
# We don't actually support value because homebridge doesn't
DEFAULT_VALUE = 1.0

# Initialize the unicornhat
unicornhat.set_layout(unicornhat.AUTO)
unicornhat.rotation(0)
unicornhat.off()


def is_on():
    # Because we either use all the pixels or none of them (right now), if a pixel is completely
    # off, the light is off
    r, g, b = unicornhat.get_pixel(0, 0)
    return r != 0 or g != 0 or b != 0


def get_current_color():
    # Returns the current color in HSV.
    rgb = unicornhat.get_pixel(0, 0)
    color = tuple(i/255
                  for i in rgb)
    return colorsys.rgb_to_hsv(*color)


@app.route("/", methods=["GET"])
def get_on():
    return {
        "status": "ON" if is_on() else "OFF"
    }


@app.route("/", methods=["POST"])
def on():
    # If it is not already on, turn it on
    if not is_on():
        unicornhat.brightness(DEFAULT_BRIGHTNESS)
        unicornhat.set_all(*DEFAULT_COLOR)
        unicornhat.show()
    return {
        "message": "Light is on"
    }


@app.route("/", methods=["DELETE"])
def off():
    unicornhat.off()
    return {
        "message": "Light is off"
    }


@app.route("/hue", methods=["GET"])
def get_hue():
    h, _, _ = get_current_color()
    return {
        "hue": h * 360
    }


@app.route("/hue", methods=["POST"])
def set_hue():
    _, s, _ = get_current_color()
    # TODO: Error handling of malformed bodies
    data = request.get_json()
    # Expect hue in arcdegrees, so the point around the circle is divided by 360
    converted = tuple(round(i * 255)
                      for i in colorsys.hsv_to_rgb(min(data['hue'], 360)/360, s, DEFAULT_VALUE))
    unicornhat.set_all(*converted)
    unicornhat.show()
    return {
        "message": "Success"
    }


@app.route("/saturation", methods=["GET"])
def get_saturation():
    _, s, _ = get_current_color()
    return {
        "saturation": s * 100
    }


@app.route("/saturation", methods=["POST"])
def set_saturation():
    h, _, _ = get_current_color()
    # TODO: Error handling of malformed bodies
    data = request.get_json()
    converted = tuple(round(i * 255)
                      for i in colorsys.hsv_to_rgb(h, min(data['saturation'], 100)/100, DEFAULT_VALUE))
    unicornhat.set_all(*converted)
    unicornhat.show()
    return {
        "message": "Success"
    }


@app.route("/brightness", methods=["GET"])
def get_brightness():
    return {
        "brightness": unicornhat.get_brightness() * 100
    }


@app.route("/brightness", methods=["POST"])
def set_brightness():
    # TODO: Error handling of malformed bodies
    data = request.get_json()
    unicornhat.brightness(min(data["brightness"], 100)/100)
    unicornhat.show()
    return {
        "message": "Success"
    }
