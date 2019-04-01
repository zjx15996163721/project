from PIL import Image, ImageEnhance
import pytesseract
im = Image.open('./pic2/7.png')
# im.show()
data = im.getdata()
print(list(data))
w, h = im.size
black_point = 0
for x in range(1, w-1):
    for y in range(1, h-1):
        mid_pixel = data[w*y + x]

        if mid_pixel == 255:
            top_pixel = data[w*(y-1) + x]
            left_pixel = data[w*y + (x-1)]
            down_pixel = data[w*(y+1) + x]
            right_pixel = data[w*y + (x+1)]

            if top_pixel == 0:
                black_point += 1
            if left_pixel == 0:
                black_point += 1
            if down_pixel == 0:
                black_point += 1
            if right_pixel == 0:
                black_point += 1

            if black_point > 2:
                im.putpixel((x, y), 0)

            black_point = 0
# im.save('./pic2/7.png')
text = pytesseract.image_to_string(im, lang='chi_sim')
print(text)