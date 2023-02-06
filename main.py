from PIL import Image, ImageOps, ExifTags
import re

def Convert(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image

def GetNFrames(image):
    try:
        return image.n_frames
    except AttributeError:
        count = 0
        try:
            while True:
                image.seek(count)
                count = count + 1
        except EOFError:
            return count

def GetExif(image):
    img_exif, exiflist = image.getexif(), []
    if img_exif is None:
        return 'None'
    else:
        for key, val in img_exif.items():
            if key in ExifTags.TAGS:
                exiflist.append(f'{ExifTags.TAGS[key]}:{val}')
        return exiflist

def Negative(img:Image) -> Image:
    xs, ys = img.size
    res_img = Image.new(img.mode, (xs, ys))
 
    for x in range(xs):
        for y in range(ys):
            r, g, b, *a = img.getpixel((x, y))
            res_img.putpixel((x, y), (255-r, 255-g, 255-b))
 
    return res_img

def Channel(img:Image, color:int) -> Image:
    xs, ys = img.size
    res_img = Image.new(img.mode, (xs, ys))
 
    for x in range(xs):
        for y in range(ys):
            c = img.getpixel((x, y))[color]
            res_img.putpixel((x, y), (c, c, c))
 
    return res_img

def BitPlane(img:Image, color:int, plane:int) -> Image:
    xs, ys = img.size
    res_img = Image.new(img.mode, (xs, ys))
 
    for x in range(xs):
        for y in range(ys):
            c = img.getpixel((x,y))[color]
            c = int(format(c, '08b')[plane]) * 255
            res_img.putpixel((x,y), (c, c, c))
    return res_img

def StereogramSolver(image, result_image, shift = 0):
    x, y = image.size
    clone = image.copy()
    for i in range(x):
        for j in range(y):
            r, g, b = image.getpixel((i,j))
            if i + shift >= x:
                rs, gs, bs = clone.getpixel((x - (i + shift),j))
            else:
                rs, gs, bs = clone.getpixel((i + shift,j))
            result_image.putpixel((i,j),(abs(rs - r), abs(gs - g), abs(bs - b)))
    return result_image

def SignificantBit(image, color_order = 'RGB', row_order = True, startpoint = 0, bit = 0):
    color_order = color_order.upper()
    x, y = image.size
    x, y = range(x), range(y)
    r,g,b = 0,1,2
    bit = int(bit)
    try:
        if bit > 7 or bit < 0: bit = 0
    except ValueError: bit = 0

    if startpoint == 1: x = reversed(x)
    elif startpoint == 2: y = reversed(y)
    elif startpoint == 3: x, y = reversed(x), reversed(y)
    
    color_orders = {
        'RGB': [r ,g ,b],'RBG': [r ,b ,g],
        'BRG': [b ,r ,g],'BGR': [b ,g ,r],
        'GRB': [g ,r ,b],'GBR': [g ,b ,r]
    }

    order = color_orders[color_order]
    message = ''
    if row_order == 'True':
        for i in y:
            for ii in x:
                colors = image.getpixel((ii,i))
                f = format(colors[order[0]], '#010b')[2:][bit]
                s = format(colors[order[1]], '#010b')[2:][bit]
                t = format(colors[order[2]], '#010b')[2:][bit]
                message = message+f+s+t
    else:
        for i in x:
            for ii in y:
                colors = image.getpixel((i,ii))
                f = format(colors[order[0]], '#010b')[2:][bit]
                s = format(colors[order[1]], '#010b')[2:][bit]
                t = format(colors[order[2]], '#010b')[2:][bit]
                message = message+f+s+t
    return message

def OddEven(img: Image) -> Image:
    xs, ys = img.size
    res_img = Image.new(img.mode, (xs, ys))

    for x in range(xs):
        for y in range(ys):
            r, g, b = img.getpixel((x,y))
            r = (r % 2) * 255
            g = (g % 2) * 255
            b = (b % 2) * 255
            res_img.putpixel((x,y), (r,g,b))
    return res_img

def Strings(F):
    result = ''
    for _ in F:
        _ = chr(int(_))
        if _.isascii():
            result += f'{_}'
    result = re.sub(r"\s+", "", result)
    return result

def Generate(img: Image, SavePath, ImageName):
    Negative(img).save(f'{SavePath}N{ImageName}')
    Channel(img, 0).save(f'{SavePath}R{ImageName}')
    Channel(img, 1).save(f'{SavePath}G{ImageName}')
    Channel(img, 2).save(f'{SavePath}B{ImageName}')
    OddEven(img).save(f'{SavePath}OE{ImageName}')
    for i in range(0,8):
        BitPlane(img, 0, i).save(f'{SavePath}R{i}{ImageName}')
        BitPlane(img, 1, i).save(f'{SavePath}G{i}{ImageName}')
        BitPlane(img, 2, i).save(f'{SavePath}B{i}{ImageName}')

def Messages():
    print('Какую операцию хотите провести?\n')
    print('Negative')
    print('Channel')
    print('BitPlane')
    print('StereogramSolver')
    print('SignificantBit')
    print('exit - выход из программы\n')

if __name__ == "__main__":
    while True:
        try:
            file = input('Введите названия файла:\n$ ')
            if file == 'exit':
                exit()
            else:
                Original_Image = Image.open(file)
                break
        except FileNotFoundError:
                print('файл не найден')
    Result_Image = Image.new(Original_Image.mode, Original_Image.size, color = 'white')

    Messages()
    ChannelMessage = 'Выберите индекс цвета (0, 1, 2): '
    BitPlaneMessage = 'Введите просматриваемый бит (0 - 7): '
    StereogramMessage = 'Введите смещенеие: '
    SignificantBitMessages = [
            'Введите порядок цвета: ',
            'Чтение по рядам? (True, False): ',
            'Точка старта? (0,1,2,3): ',
            'Введите просматриваемый бит (0 - 7): ']
    

    while True:
        enter = input('Выберите операцию.\n$ ')
        if enter == 'Negative':
            Negative(Original_Image).show()     
        elif enter == 'Channel':
            Channel(Original_Image, int(input(ChannelMessage))).show()
        elif enter == 'BitPlane': 
            BitPlane(Original_Image, int(input(ChannelMessage)), int(input(BitPlaneMessage))).show()
        elif enter == 'StereogramSolver':
            StereogramSolver(Original_Image, Result_Image, int(input(StereogramMessage))).show()
        elif enter == 'SignificantBit':
            a = SignificantBit(Original_Image, input(SignificantBitMessages[0]), input(SignificantBitMessages[1]), input(SignificantBitMessages[2]), input(SignificantBitMessages[3]))
            f = open("result.txt", "x")
            f.write(a)
            f.close()
        elif enter == 'exit':
            exit()
        else:
            print('Такой операции не существует')
