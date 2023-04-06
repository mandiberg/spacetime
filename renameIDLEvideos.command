{
exiftool -api QuickTimeUTC=1 "-FileName<CreateDate" -d "%Y%m_%d_%H%M_%S.%%e" /Users/michaelmandiberg/Documents/NYCidling/inbox/
exiftool -api QuickTimeUTC=1 -d "%m/%d/%Y, %I:%M:%S %p" -csv -MediaCreateDate -MediaModifyDate /Users/michaelmandiberg/Documents/NYCidling/inbox/ >/Users/michaelmandiberg/Documents/NYCidling/inbox/idlingvideos.csv
}
