from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
from geopy.extra.rate_limiter import RateLimiter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from geopy.geocoders import Nominatim
from tkinter import filedialog
from moviepy.editor import *
import reverse_geocode
import tkinter as tk
import pandas as pd
import datetime
import os

#implicit depdency to ffmpeg, conda package


def save2csv(filename, MediaCreateDate, MediaModifyDate, location):
    if not os.path.isdir('save'):
        os.mkdir('save')
    pathFile = 'save/data.csv'
    house_number = address.get('house_number', '')
    street_name = address.get('road', '')
    city = address.get('city', '')
    state = address.get('state', '')
    zipcode = address.get('postcode')
    raw_data = {'filename': [filename], 'MediaCreateDate': [MediaCreateDate], 'MediaModifyDate': [MediaModifyDate], \
                'House Number': [house_number], 'Street Name': [street_name], 'City': [city], 'State': [state], 'ZIP code': [zipcode]}
    df = pd.DataFrame(raw_data)
    # append data frame to CSV file
    if os.path.exists(pathFile):
        df.to_csv(pathFile, mode='a', index=False, header=False, encoding='utf-8')
    else:
        df.to_csv(pathFile, index=False, encoding='utf-8')
        
def add_caption(fileName, FILE_FORMAT = ""):
    try :
        date = reformatDate(data['DateCreated'])
        gps = f"""{data['GPSLatitudeRef']} {data['GPSLatitude'][0]}° {data['GPSLatitude'][1]}\' {data['GPSLatitude'][2]}\", {data['GPSLongitudeRef']} { data['GPSLongitude'][0]}° {data['GPSLongitude'][1]}\' {data['GPSLongitude'][2]}\" """
        # traverse the data
        house_number = address.get('house_number', '') if ('house_number' in address) else ''
        street_name = address.get('road', '') if ('road' in address) else ''
        city = address.get('city', '') if ('city' in address) else ''
        state = address.get('ISO3166-2-lvl4', '') if ('ISO3166-2-lvl4' in address) else ''
        zipcode = address.get('postcode') if ('postcode' in address) else ''
        country = address.get('country', '') if ('country' in address) else ''
        location = f"{house_number} {street_name}\n{city}, {state} {zipcode}\n{country}\n"
        label = f"{date}\n{gps}\n{location}"
        mediaName = data['DateCreated'].replace("-", "_")
        mediaName = mediaName.replace(" ", "_")
        mediaName = mediaName.split(":")
        mediaName = f"{mediaName[0]}{mediaName[1]}_{mediaName[2]}"
        if not os.path.isdir('save'):
            os.mkdir('save')
        if (FILE_FORMAT == "VIDEO_FORMAT"):
            try : 
                # loading video dsa gfg intro video
                clip = VideoFileClip(fileName)
                text =  TextClip(str(label), font='Arial-Black', fontsize=50, stroke_color='black', stroke_width=2, color='white').\
                        set_position((100, 200)).set_duration(clip.duration).on_color(color=(0,0,0), col_opacity=0.6)
                # creating a composite video
                final_clip = CompositeVideoClip([clip, text])
                # write the result to a file in any format
                pathSave = f"save/{mediaName}.MP4"
                final_clip.write_videofile(pathSave, fps=30)
            except :
                print("Install ImageMagick on your computer")
            
        elif (FILE_FORMAT == "IMAGE_FORMAT"):
            pathSave = f"save/{mediaName}.JPG"
            # Open the image and grab its dimensions
            image = Image.open(fileName);
            w = image.width
            h = image.height
            # Use a more interesting font
            # font = ImageFont.load_default()
            font = ImageFont.truetype("Roboto-Bold.ttf", 50)

            # Instantiate draw object & be sure to set RGBA mode for transparency support
            draw = ImageDraw.Draw(image)

            # Get the dimensions of the text for dynamic placement
            textwidth, textheight = draw.textsize(str(label), font=font)
            margin = 15
            left, top, width, height = 0, 0, (2*margin) + textwidth, (2*margin) + textheight
            # Draw a rectangle and place text on it
            draw.text(xy=(margin,margin), text=str(label), fill=(255, 255, 255), font=font)
            
            image.save(pathSave)
    except Exception as e :
        print(e)
    
def dms2dd(DMS_coord, sign):
    # Convert DMS (degrees minutes seconds) to DD (decimal degrees)
    degrees = DMS_coord[0]
    minutes = DMS_coord[1]
    seconds = DMS_coord[2]
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if sign == 'S' or sign == 'W':
        dd *= -1
    return dd;


def get_addressInfo(lat, long):
    try :
        geocode = Nominatim(user_agent="application")
        location = geocode.reverse((lat, long), language='en', exactly_one=True)
        address = location.raw['address']
        return address
    except :
        print("Internet Disconnected")
        
def reformatDate(date_string):
    from datetime import datetime
    datetime = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    nowDate = datetime.strftime("%a %m, %Y at %I:%M:%S %p")
    return nowDate

def get_exif(media_file, FILE_FORMAT = ""):
    exifdata = {'GPSLatitudeRef': "", 'GPSLatitude': "", 'GPSLongitudeRef': "", 'GPSLongitude': "", 'DateCreated': "", 'ModifyDate': ""}
    #######################################
    if (FILE_FORMAT == "VIDEO_FORMAT"):
        parser = createParser(media_file)
        if parser:
            metadata = extractMetadata(parser)
            if metadata:
                for data in sorted(metadata):
                    if not data.values:
                        continue
                    key = data.description
                    value = ', '.join([item.text for item in data.values])
                    if key == "Creation date":
                        exifdata['DateCreated'] = value
                    elif key == "Last modification":
                        exifdata['ModifyDate'] = value 
                return exifdata
        else:
            print("No EXIF metadata found")
            pass 
    #######################################
    elif (FILE_FORMAT == "IMAGE_FORMAT"):
        image = Image.open(media_file)
        image.verify()
        if not image.getexif():
            print("No EXIF metadata found")
        else:
            try:
                exifdata['GPSLatitudeRef'] = image.getexif().get_ifd(0x8825)[1]
                exifdata['GPSLatitude'] = image.getexif().get_ifd(0x8825)[2]
                exifdata['GPSLongitudeRef'] = image.getexif().get_ifd(0x8825)[3]
                exifdata['GPSLongitude'] = image.getexif().get_ifd(0x8825)[4]
                DateCreated = image.getexif()[306].split(" ")
                DateCreated[0] = DateCreated[0].replace(":", "-")
                exifdata['DateCreated'] = f"{DateCreated[0]} {DateCreated[1]}"
                # file modification timestamp of a file
                m_time = os.path.getmtime(path)
                # convert timestamp into DateTime object
                exifdata['ModifyDate'] = datetime.datetime.fromtimestamp(m_time)
            except IndexError:
                pass
        return exifdata
    #######################################

    
def selectDir():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askdirectory()
    return file_path

if __name__ == '__main__':
    register_heif_opener()
    #######
    inbox = 'inbox'
    if os.path.exists(inbox):
        files_path = inbox
    else:
        files_path = selectDir()
    if not files_path:
        print('No Folder Selected', 'Please select a valid Folder')
    else :
        list_of_files= os.listdir(files_path)
        for file in list_of_files:
            IMAGE_FORMAT = (".heic", ".HEIC", ".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")
            VIDEO_FORMAT = (".mov", ".MOV", ".mp4", ".MP4") #("mov", "qt", "mp4", "m4v", "m4a", "m4p", "m4b")
            latitude = None
            longitude = None
            location = ''
            caption = ''
            
            if file.upper().endswith(IMAGE_FORMAT) :#or file.upper().endswith(VIDEO_FORMAT):
                FILE_FORMAT = "IMAGE_FORMAT" if file.upper().endswith(IMAGE_FORMAT) else "VIDEO_FORMAT"                
                path = r"{files_path}/{file}".format(files_path = files_path, file = file)
                data = get_exif(path, FILE_FORMAT)
                #########################
                if data:
                    print(file)
                    latitude  = dms2dd(data['GPSLatitude'], data['GPSLatitudeRef']) if data['GPSLatitude'] else ''
                    longitude = dms2dd(data['GPSLongitude'], data['GPSLongitudeRef']) if data['GPSLongitude'] else ''
                    address = get_addressInfo(latitude, longitude) if(latitude and longitude) else ''
                    add_caption(path, FILE_FORMAT)
                    filename = path.split("/")[-1]
                    save2csv(filename, data['DateCreated'], data['ModifyDate'], address)   
