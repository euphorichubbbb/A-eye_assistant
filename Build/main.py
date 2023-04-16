from flask import Flask
from flask import render_template
from flask import request
from flask import Flask, redirect, request

from pytesseract import Output
import cv2
import pytesseract
import pyttsx3
from werkzeug.utils import secure_filename

myconfig = r"--psm 11 --oem 3"


global file

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def website():
    if request.method == "POST":
        image = request.files['file']
        if image.filename == '':
            print("File name is invalid")
            return redirect(request.url)
        filename = secure_filename(image.filename)
        image.save(filename)
        global file
        file = filename
        return render_template("Home.html", filename=filename)
    return render_template("Home.html")

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("About.html")

def tts():
    img = cv2.imread(filename=file)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    height, width = img.shape

    data = pytesseract.image_to_data(img, config=myconfig,  output_type=Output.DICT)

    words = []
    amount_boxes = len(data['text'])
    for i in range(amount_boxes):
        if float(data['conf'][i]) > 90:
            (x, y, width, height) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            img = cv2.rectangle(img, (x,y), (x+width, y+height), (0, 255, 0), 2)
            img = cv2.putText(img, data['text'][i], (x, y+height+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2, cv2.LINE_AA)
            words.append(data['text'][i])
    if len(words) == 0:
        engine = pyttsx3.init()
        engine.say("Could not read text")
        engine.runAndWait()
    else:
        text = ' '.join(words)
        text = text.capitalize()
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    return "The text is " + text

app.jinja_env.globals.update(tts=tts)


if __name__ == "__main__":
    app.run(debug=True)