from PIL import Image, ImageEnhance
import pytesseract
import time
import numpy

# im = Image.open('./pic/2.png')
# w, h = im.size
# print(w, h)
#
# im_pixel = im.load()
# print(im_pixel[50, 10])
#
# lim = im.convert('L')
# flag = 140
# table = []
#
# for i in range(256):
#     if i < flag:
#         table.append(0)
#     else:
#         table.append(1)
#
# bim = lim.point(table, '1')
# bim.save('./pic2/4.png')

im = Image.open('./pic2/4.png')
# im.show()
data = im.getdata()
print(list(data))
w, h = im.size
black_point = 0
for x in range(1, w-1):
    for y in range(1, h-1):
        mid_pixel = data[w*y + x]

        if mid_pixel == 0:
            top_pixel = data[w*(y-1) + x]
            left_pixel = data[w*y + (x-1)]
            down_pixel = data[w*(y+1) + x]
            right_pixel = data[w*y + (x+1)]

            if top_pixel < 10:
                black_point += 1
            if left_pixel < 10:
                black_point += 1
            if down_pixel < 10:
                black_point += 1
            if right_pixel < 10:
                black_point += 1

            if black_point < 2:
                im.putpixel((x, y), 255)

            black_point = 0
im.show()
im.save('./pic2/5.png')


#
# enh_con = ImageEnhance.Contrast(im)
# contrast = 1.5
# image_contracted = enh_con.enhance(contrast)
# image_contracted.show()
#
# enh_bri = ImageEnhance.Brightness(image_contracted)
# brightness = 1.5
# image_brightened = enh_bri.enhance(brightness)
# image_brightened.show()
#
# enh_col = ImageEnhance.Color(image_brightened)
# color = 1.5
# image_colored = enh_col.enhance(color)
# image_colored.show()
#
# enh_sha = ImageEnhance.Sharpness(image_colored)
# sharpness = 3.png.0
# image_sharped = enh_sha.enhance(sharpness)
# image_sharped.show()
#
# im2 = image_sharped.convert('L')
# im2.show()
#
#
text = pytesseract.image_to_string(im2, lang='chi_sim')
print(text)

