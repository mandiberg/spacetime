from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL.ExifTags import TAGS
from exiftool import ExifToolHelper
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
import sys
from datetime import datetime
from pytz import timezone
from dateutil import tz

#implicit depdency to ffmpeg, conda package
#implicit depdency to ImageMagick, brew package, and maybe also Wand, a PyPI install?
# from wand.image import Image
# to get Wand to talk to ImageMagick on MacOS you need to tell it where to find it. I used:
# $ export MAGICK_HOME=/opt/homebrew
# but wand install instructions say to use:
# $ export MAGICK_HOME=/opt/local
#implicit depdency to exiftool, command-line tool
# exiftool requires ExifToolHelper bindings, a PyPI install

def save2csv(filename, MediaCreateDate, MediaModifyDate, location):
    if not os.path.isdir('save'):
        os.mkdir('save')
    pathFile = 'save/data.csv'
    house_number = address.get('house_number', '')
    street_name = address.get('road', '')
    city = address.get('city', '')
    print("save to csv city ",city)
    state = address.get('state', '')
    zipcode = address.get('postcode')
    url = address.get('url')
    createdate_and_time = split_datetime(MediaCreateDate)
    moddate_and_time = split_datetime(MediaModifyDate)
    # MediaCreate = str(MediaCreateDate).split(" ")
    raw_data = {'filename': [filename], 'MediaCreateDate': [createdate_and_time[0]], 'MediaCreateTime': [createdate_and_time[1]], 'MediaModifyTime': [moddate_and_time[1]], \
                'House Number': [house_number], 'Street Name': [street_name], 'City': [city], 'State': [state], 'ZIP code': [zipcode], 'URL':[url]}
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
                print('trying to save video')
                # loading video dsa gfg intro video
                clip = VideoFileClip(fileName)
                print('loaded video ', clip.size)
                print(label)
                text = TextClip(label, font ="Roboto-Bold", fontsize = 70, color ="green")
                # creating a composite video
                print("made text")
                output_size = clip.size
                final_clip = CompositeVideoClip([clip, text], size=output_size).set_duration(clip.duration)
                # final_clip = final_clip
                print(final_clip)
                # write the result to a file in any format
                pathSave = f"save/{mediaName}.MP4"
                print("pathsave: ",pathSave)
                # clip.write_videofile(pathSave, codec='mp4', fps=30)
                # won't write either clip, but with the original clip it at least begins the attempt
                # fails to even try to save the final_clip
                # need to restart here: https://medium.com/codex/working-with-video-files-in-python-6530c35a6b10
                # final_clip.save_frame("save/testframe.jpeg")
                final_clip.write_videofile(pathSave, fps=30)
            except Exception as e :
                print(e)
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

def decdeg2dms(dd):
   is_positive = dd >= 0
   dd = abs(dd)
   minutes,seconds = divmod(dd*3600,60)
   degrees,minutes = divmod(minutes,60)
   degrees = degrees if is_positive else -degrees
   return (degrees,minutes,seconds)


def format_datetime(datetime):
    DateCreated = datetime.split(" ")
    DateCreated[0] = DateCreated[0].replace(":", "-")
    dashed_datetime = f"{DateCreated[0]} {DateCreated[1]}"
    return dashed_datetime

def split_datetime(thisdate_string):
    datetimeEST = timezoneDate(thisdate_string)
    date_and_time = (datetimeEST.strftime('%Y-%m-%d'), datetimeEST.strftime('%H:%M:%S'))
    return date_and_time


def get_addressInfo(lat, lon, zipcity):
    try :
        geocode = Nominatim(user_agent="application")
        location = geocode.reverse((lat, lon), language='en', exactly_one=True)
        address = location.raw['address']
        address['url'] = f"https://nominatim.openstreetmap.org/ui/reverse.html?lat={lat}&lon={lon}&zoom=18"
        print(address)
        # city = address.get('postcode') if ('postcode' in address) else ''
         #refer to the named index:
        try:
            # print("zipcity ",zipcity, int(address['postcode']))
            # print("zipcity line ",zipcity[int(address['postcode'])])
            # print("zipcity city ",zipcity[int(address['postcode'])]['city'])
            address['city'] = zipcity[int(address['postcode'])]
            print("correctcity ",address['city'])
        except:
            address['city'] = ""
            print("well that didn't work!")
        # address['city'] = zipcity['city'][int(address['postcode'])]
        # print(address.get('postcode'))
        # print(df[df["zip"] == address.get('postcode')] )
        # print(df.loc[address.get('postcode')]) 
        return address
    except :
        print("couldnt get get_addressInfo -- Internet Disconnected?")


# def convert(y,m,d,h,min,sec,ms):
#     NYC = tz.gettz('America/ New_York')
#     d = datetime.datetime(y,m,d,h,min,sec,ms,tzinfo = NYC)
#     return time.mktime(d.timetuple())
#     unixtime = time.mktime(d.timetuple())


def timezoneDate(thisdate_string):
    from datetime import datetime

    #THIS NEEDS TO CONVERT FROM UTC TO EST
    #IT DOESNT AND IT WAS GIVING ME HEADACHE
    #I GIVE UP FOR NOW
    
    # format = "%Y-%m-%d %H:%M:%S %Z%z"
    format = "%Y-%m-%d %H:%M:%S"
    # NYC = tz.gettz('America/ New_York')
    # d = datetime.datetime(y,m,d,h,min,sec,ms,tzinfo = NYC)
    # print(convert(2020,5,3,3,59,0,0))

    datetimeGMT = datetime.strptime(thisdate_string, format)
    datetimeEST = datetimeGMT.astimezone(timezone('US/Eastern'))
    print(type(datetimeGMT)," datetime ",datetimeGMT.strftime(format))
    print(type(datetimeEST)," datetimeEST ",datetimeEST.strftime(format))
    return(datetimeEST)

def reformatDate(date_string):
    from datetime import datetime
    datetime = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    nowDate = datetime.strftime("%a %m, %Y at %I:%M:%S %p")
    return nowDate


def get_exif(media_file, FILE_FORMAT = ""):
    exifdata = {'GPSLatitudeRef': "", 'GPSLatitude': "", 'GPSLongitudeRef': "", 'GPSLongitude': "", 'DateCreated': "", 'ModifyDate': ""}
    #######################################
    if (FILE_FORMAT == "VIDEO_FORMAT"):
        print('a video!')
        # path_to_file = os.path.join(files_path,file)
        # print("file and path: ",media_file)
        with ExifToolHelper() as et:
            # for d in et.get_metadata("inbox/IMG_9571.MOV"):
            # these may not be the right create/modify dates for all media formats
            for d in et.get_tags([media_file], tags=["GPSLatitudeRef", "GPSLatitude", "GPSLongitudeRef", "GPSLongitude","QuickTime:CreateDate","QuickTime:ModifyDate"]):
                for k, v in d.items():
                    print(f"Dict: {k} = {v}")

                #inferring N/S and E/W from +/-
                if d['Composite:GPSLatitude'] > 0:
                    exifdata['GPSLatitudeRef'] = 'N'
                else:
                    exifdata['GPSLatitudeRef'] = 'S'
                #converting Decimals to DMS
                exifdata['GPSLatitude'] = decdeg2dms(abs(d['Composite:GPSLatitude']))
                if d['Composite:GPSLongitude'] > 0:
                    exifdata['GPSLongitudeRef'] = 'E'
                else:
                    exifdata['GPSLongitudeRef'] = 'W'
                exifdata['GPSLongitude'] = decdeg2dms(abs(d['Composite:GPSLongitude']))
                # convert timestamp into DateTime object
                exifdata['DateCreated'] = format_datetime(d['QuickTime:CreateDate'])
                exifdata['ModifyDate'] = format_datetime(d['QuickTime:ModifyDate'])
                print(exifdata)
                return exifdata
            # else:
            #     print("No EXIF metadata found")
            #     pass 
    #######################################
    elif (FILE_FORMAT == "IMAGE_FORMAT" and csvonly is False):
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
                # DateCreated = image.getexif()[306].split(" ")
                # DateCreated[0] = DateCreated[0].replace(":", "-")
                # exifdata['DateCreated'] = f"{DateCreated[0]} {DateCreated[1]}"
                exifdata['DateCreated'] = format_datetime(image.getexif()[306])
                # file modification timestamp of a file
                m_time = os.path.getmtime(path)
                # convert timestamp into DateTime object
                exifdata['ModifyDate'] = datetime.datetime.fromtimestamp(m_time)
            except IndexError:
                pass
        print (exifdata)
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
    if len(sys.argv)>1 and sys.argv[1] == 'csvonly':
        csvonly = True
    else:
        csvonly = False
    inbox = 'inbox'
    if os.path.exists(inbox):
        files_path = inbox
    else:
        files_path = selectDir()
    if not files_path:
        print('No Folder Selected', 'Please select a valid Folder')
    else :
        list_of_files= os.listdir(files_path)
        print(list_of_files)
        list_of_files.sort()
        print(list_of_files)
        zipcity = pd.read_csv('NYCZIPs.csv', index_col='zip').to_dict()
        zipcity = zipcity['city']
        for file in list_of_files:

            IMAGE_FORMAT = (".heic", ".HEIC", ".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")
            VIDEO_FORMAT = (".mov", ".MOV", ".mp4", ".MP4") #("mov", "qt", "mp4", "m4v", "m4a", "m4p", "m4b")
            latitude = None
            longitude = None
            location = ''
            caption = ''
            
            if file.upper().endswith(IMAGE_FORMAT) or file.upper().endswith(VIDEO_FORMAT):

                FILE_FORMAT = "IMAGE_FORMAT" if file.upper().endswith(IMAGE_FORMAT) else "VIDEO_FORMAT"                
                path = r"{files_path}/{file}".format(files_path = files_path, file = file)
                print(path)
                data = get_exif(path, FILE_FORMAT)
                #########################
                if data:
                    print(file)
                    latitude  = dms2dd(data['GPSLatitude'], data['GPSLatitudeRef']) if data['GPSLatitude'] else ''
                    longitude = dms2dd(data['GPSLongitude'], data['GPSLongitudeRef']) if data['GPSLongitude'] else ''
                    address = get_addressInfo(latitude, longitude, zipcity) if(latitude and longitude) else ''
                    if not csvonly: 
                        add_caption(path, FILE_FORMAT)
                    filename = path.split("/")[-1]
                    save2csv(filename, data['DateCreated'], data['ModifyDate'], address)   
