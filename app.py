from PIL import Image, GifImagePlugin
from flask import Flask, request, flash, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import main as STEG
import os

UPLOAD_FOLDER       =   f'{os.path.dirname(os.path.realpath(__file__))}/static/images/'
ALLOWED_EXTENSIONS  =   set(['png', 'jpg', 'jpeg', 'gif', 'bmp'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Operators = ["N","R","G","B","OE"]
for ii in 'RGB':
    for i in range(8):
        Operators.append(f'{ii}{i}')

def log(arg = None):
    print(f'🚀🚀🚀\n{arg}\n🚀🚀🚀')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['POST','GET'])
@app.route('/index', methods = ['POST','GET'])
def index(filename = None):
    if request.method != 'POST':
        return render_template("upload.html")

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if not file and not allowed_file(file.filename):
        return redirect(request.url)

    filename = secure_filename(file.filename)
    imagepath = f'{UPLOAD_FOLDER}{filename}'
    file.save(imagepath)
    image = Image.open(imagepath)
    nframes = STEG.GetNFrames(image)
    if nframes > 0:
        for i in range(0,nframes):
            image.seek(i)
            image.save(f'{UPLOAD_FOLDER}F{i}{filename}')

    return redirect(url_for('info',image=imagepath.split('/')[-1]))

@app.route('/index/info', methods=['POST','GET'])
def info(i=0):
    path = request.args['image']
    with open(f'{UPLOAD_FOLDER}{path}','rb') as image:
        Strings = STEG.Strings(image.read())
    with Image.open(f'{UPLOAD_FOLDER}{path}') as image:
        Frames = STEG.GetNFrames(image)
        Exif = STEG.GetExif(image)
        image = STEG.Convert(image)
        if request.method == 'POST':
            if 'FRAME' not in request.form:
                return redirect(request.url)
            i = request.form['FRAME']
            if i == '':
                return redirect(request.url)
            if int(i) > Frames-1 or int(i) < 0: i = '0'
            if request.form['switch'] == 'continue':
                frameimage = f'F{i}{path}'
                image.seek(int(i))
                STEG.Generate(image,UPLOAD_FOLDER,f'F{i}{path}')
                return redirect(url_for('switch', image = frameimage))
        frameimage = f'F{i}{path}'
    return render_template("info.html",img=frameimage,Exif=Exif,Frames=Frames-1,Frame=i,path=path,Strings=Strings)

@app.route('/index/switch', methods=['POST','GET'])
def switch():
    path = request.args['image']
    RenderImage = f'{path}'
    if request.method == 'POST':
        image = Image.open(f'{UPLOAD_FOLDER}{path}')
        image = STEG.Convert(image)
        NewImage = Image.new(image.mode, image.size, color='white')
        color = request.form['color']
        startpoint = request.form['startpoint']
        row_order = request.form['row_order']
        bit = request.form['bit']
        message = STEG.SignificantBit(image,color,row_order,startpoint,bit)
        with open(f'{UPLOAD_FOLDER}{color}{startpoint}{row_order}{path.split(".")[0]}.txt', 'w') as f:
            f.write(message)
            text = f'{color}{startpoint}{row_order}{path}'
        return redirect(url_for('result', text = text))
    return render_template('switch.html',img=RenderImage,filters=Operators)

@app.route('/index/result', methods = ['GET'])
def result():
    text = request.args['text']
    path = f"{UPLOAD_FOLDER}{text.split('.')[0]}.txt"
    with open(path, "r") as f:
        Text, B, H, U =  f.read(), '', '', ''
        for _ in range(0,(8*(len(Text)//8)),8):
            Group = int(f'{Text[_:_+8]}',2)
            if Group != 0:
                H += format(Group,"#02x")[2:].upper() +  ' '
                U += chr(Group)
                B += f'{Text[_:_+8]}' + ' '
    return render_template("result.html",Hex=H,Binary=B,Unicode=U,Path=path)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
