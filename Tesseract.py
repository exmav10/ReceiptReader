import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

im = Image.open("removed_noise.png") # the second one 
im = im.filter(ImageFilter.MedianFilter())
enhancer = ImageEnhance.Contrast(im)
im = enhancer.enhance(2) # Enchaces Contrast 
im.show()
im = im.convert('1')
text = pytesseract.image_to_string(im)
print(text)