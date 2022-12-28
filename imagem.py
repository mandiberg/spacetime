from wand.image import Image
from wand.drawing import Drawing
ny = Image(filename ='/Users/michaelmandiberg/Documents/GitHub/spacetime/inbox/TC_00657.JPG')
 
print(ny.height, ny.width)

from moviepy.editor import TextClip
print ( TextClip.list("font") )

# export MAGICK_HOME=/opt/homebrew

with Image(filename='/Users/michaelmandiberg/Documents/GitHub/spacetime/inbox/TC_00657.JPG') as img:
    with Drawing() as context:
        context.font_family = 'monospace'
        context.font_size = 25
        metrics = context.get_font_metrics(img,
                                           "How BIG am I?",
                                           multiline=False)
        print(metrics)

# from wand.image import Image
# from wand.drawing import Drawing
# ny = Image(filename =’new york.jpg’)
draw = Drawing()
draw.font_size = 20
draw.text(100, 100, 'This is New York City!')
draw(ny)
ny.save(filename='text new york.jpg')