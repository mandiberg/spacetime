from exiftool import ExifToolHelper
with ExifToolHelper() as et:
    # for d in et.get_metadata("inbox/IMG_9571.MOV"):
    for d in et.get_tags(["inbox/IMG_9571.MOV"], tags=["GPSLatitude", "GPSLongitude","QuickTime:CreateDate","QuickTime:ModifyDate","Duration"]):
        for k, v in d.items():
            print(f"Dict: {k} = {v}")


#Dict: QuickTime:TrackCreateDate = 2022:11:06 17:41:40
#Dict: QuickTime:TrackModifyDate = 2022:11:06 17:41:46
# Dict: Composite:GPSLatitude = 40.6754
# Dict: Composite:GPSLongitude = -73.9701
# Dict: QuickTime:Duration = 6.43833333333333
# Dict: Composite:GPSPosition = 40.6750972222222 -73.9694888888889
# Dict: Composite:GPSLatitude = 40.6750972222222
# Dict: Composite:GPSLongitude = -73.9694888888889
# Dict: Composite:SubSecDateTimeOriginal = 2022:11:06 12:40:54.326-05:00

# Dict: EXIF:GPSLatitudeRef = N
# Dict: EXIF:GPSLatitude = 40.6750972222222
# Dict: EXIF:GPSLongitudeRef = W
# Dict: EXIF:GPSLongitude = 73.9694888888889




#     from exiftool import ExifToolHelper
#     with ExifToolHelper() as et:
#         for d in et.get_tags(["rose.jpg", "skyblue.png"], tags=["GPSLatitude", "GPSLongitude","Duration"]):
#             for k, v in d.items():
#                 print(f"Dict: {k} = {v}")

#     Dict: SourceFile = rose.jpg
#     Dict: File:FileSize = 4949
#     Dict: Composite:ImageSize = 70 46
#     Dict: SourceFile = skyblue.png
#     Dict: File:FileSize = 206
#     Dict: Composite:ImageSize = 64 64

