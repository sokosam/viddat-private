import os
from PIL import Image, ImageDraw, ImageFont

def thumbnail_generator(text, output_path, file_name ="out", red_text = False, newSize = None, name= "NAME", picture_path = "default.png"):
        #textwrap
        dir_path = os.path.dirname(os.path.realpath(__file__))
        conjoin = lambda a : os.path.join(dir_path,r"thumbnail_static",a ) 
        conjoinFont = lambda a: os.path.join(dir_path, r"fonts", a)

        def textWrap(body_text, width =450, textFont = ImageFont.truetype(conjoinFont("Helvetica-Bold-Font.ttf"), size = 27)):
            lines = []
            current_line = ""

            for word in body_text.split():
                if  textFont.getlength(text = current_line + word)<= width - 40:
                    current_line += word + " "
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "

            # Add the last line
            lines.append(current_line.strip())

            return lines
        
        # Create a transparent background image
        trbg = Image.new('RGBA', (550, 700), (255, 0, 0, 0))
        draw = ImageDraw.Draw(trbg)

        # Calculate the position to center the rounded rectangle
        width = 450
        height = 120 + ((len(textWrap(text)) + 1) * 28)
        if not red_text: height = 90 + ((len(textWrap(text)) + 1) * 28)
        x = (trbg.width - width) // 2
        y = (trbg.height - height) // 2

        logoXPos = x + 10 
        logoYPos = y + 10  

        posterX = x + 60
        posterY = y + 17 

        # Draw a rounded rectangle with white fill color
        draw.rounded_rectangle([x, y, x + width, y + height], fill="white", radius=12)

        # Load and resize the overlay image
        overlay = Image.open(conjoin(picture_path)).convert("RGBA")
        new_size = (50 , 50)
        resized_overlay = overlay.resize(new_size)
        trbg.paste(resized_overlay, (logoXPos , logoYPos ), resized_overlay)

        #anchor pos of likes and comments
        bottomIconXPos = x
        bottomIconYPos = y + height

        #likes image
        like = Image.open(conjoin("likes.png")).convert("RGBA")
        resized_like = (100, 36)
        new_like = like.resize(resized_like)
        trbg.paste(new_like, (bottomIconXPos + 20, bottomIconYPos - 40), new_like)

        #comment image
        comment = Image.open(conjoin("comments.png")).convert("RGBA")
        new_comment= comment.resize(resized_like)
        trbg.paste(new_comment, (bottomIconXPos + 140, bottomIconYPos - 40), new_comment)

        #share image
        share = Image.open(conjoin("share.png")).convert("RGBA")
        new_share = share.resize((int(resized_like[0]*1.15) , int(resized_like[1]*1.15)))
        trbg.paste(new_share, (bottomIconXPos + width - 110, bottomIconYPos - 41), new_share)


        #Add text to the image
        Helvetica = ImageFont.truetype(conjoinFont("Helvetica-Bold-Font.ttf"), size = 27)
        Verdana = ImageFont.truetype(conjoinFont("verdana.ttf"), size= 20)
        draw.text((posterX  + 8 , posterY - 5), name, (0, 0, 0), font=Verdana)

        #verified badge
        verified_overlay = Image.open(conjoin("verified.png")).convert("RGBA")
        new_awards_size = (22, 22)
        resized_verified_overlay = verified_overlay.resize(new_awards_size)
        trbg.paste(resized_verified_overlay, (int(posterX + Verdana.getlength(text=name) + 12), posterY - 3 ), resized_verified_overlay)     

        #award overlay
        awards_overlay = Image.open(conjoin("awards.png"))
        new_awards_size = (225, 24)
        resized_awards_overlay = awards_overlay.resize(new_awards_size)
        trbg.paste(resized_awards_overlay, (posterX + 5, posterY + 20), resized_awards_overlay)


        body_text = textWrap(text)

        Xpos = x + 15
        Ypos = posterY + 55

        for line in body_text:
            draw.text((Xpos + 5, Ypos), line, (0, 0, 0), font=Helvetica)
            Ypos += 28

        if red_text: draw.text((Xpos + 5, Ypos + 4), f"{red_text}", (215, 0, 64), font=Helvetica)

        (w,h) = trbg.size

        
        if newSize: trbg = trbg.resize((int(w*newSize/1080) , int(h*newSize/1080)))

        # Save the output image
        trbg.save(os.path.join(output_path, f"{file_name}.png"))