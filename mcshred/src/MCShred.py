#!/usr/bin/python

import sys

#MAX_FILE_NUMBER = 20
MAX_FILE_NUMBER = 765
errors = []
valid_tec_speakers = (
    "AB",
    "CC",
    "CDR",
    "CMP", 
    "CT", 
    "F", 
    "IWO", 
    "LCC", 
    "LMP", 
    "MS", 
    "P-1", 
    "P-2", 
    "R", 
    "R-1", 
    "R-2", 
    "S", 
    "S-1", 
    "S-2", 
    "SC", 
    "Music",
)
       
def get_file_name_for(num):
    return str(num).zfill(3) + ".txt"

def shred_to_lines(lines, pageNumber):
    logLines = []
    tapeNumber = u""
        
    for line in lines:
        if line.strip().startswith(u"Page"):
            pass
        elif line.strip().startswith(u"APOLLO 13 AIR-TO-GROUND VOICE TRANSCRIPTION"):
            pass
        elif line.strip().startswith(u"Tape "):
            tapeNumber = line.lstrip(u"Tape ").strip()
        else:
            logLines.append(LogLine(pageNumber, tapeNumber, line))
    
    return logLines

def get_all_raw_lines(path, startNumber):
    missing_files = []
    all_lines = []
    
    file_number = startNumber
    
    while file_number < MAX_FILE_NUMBER:
        filename = get_file_name_for(file_number)
        try:    
            file = open(path + filename, "r")
            file_lines = file.readlines()
            shredded_lines = shred_to_lines(file_lines, file_number)
            all_lines.extend(shredded_lines)
        except:
            missing_files.append(filename)
        finally:    
            file_number = file_number + 1                 
    
    if (len(missing_files) > 0):
        print("Missing %d files:" % len(missing_files))
    
    return all_lines    

def sterilize_token(token):
    bs0 = BadNumberSub(0, ["o","Q","O"])
    bs1 = BadNumberSub(1, ["i","J", "I","!","L","l"])
    bs4 = BadNumberSub(4, ["h"])
    bs8 = BadNumberSub(8, ["B"])
    
    tempToken = token
    
    for badSub in [ bs0, bs1, bs4, bs8 ]:
        for sub in badSub.badSubList:
            tempToken = tempToken.replace(sub, str(badSub.number))
    
    return tempToken

def get_seconds_from_mission_start(line):
    values =  line.raw.split(u" ");
    days = int(sterilize_token(values[0]))
    hours = int(sterilize_token(values[1]))
    minutes = int(sterilize_token(values[2]))
    seconds = int(sterilize_token(values[3]))
    
    return (seconds + (minutes * 60) + (hours * 60 * 60) + (days * 24 * 60 * 60))

def set_timestamp_speaker_and_text(line):
    values =  line.raw.split(u" ");
   
    line.set_seconds_from_mission_start(get_seconds_from_mission_start(line))
    
    line.set_speaker(values[4])
    
    line.set_text(" ".join(values[5:]))

def line_is_a_new_entry(line):
    
    dateTokens = line.raw.split(" ")[0:4]
    
    if len(dateTokens) < 4 :
        return False
    
    for token in dateTokens:
        try:
            int(token)
        except:
            return False
    
    return True

def is_a_non_log_line(line):
    return len(line.raw) != len(line.raw.lstrip()) or len(line.raw) == 0

def translate_lines(all_lines):
    translatedLines = []
    currentLine = None
    
    for line in all_lines:
        if line_is_a_new_entry(line):
            if currentLine != None:
                translatedLines.append(currentLine)
            set_timestamp_speaker_and_text(line)
            currentLine = line
        elif currentLine != None:
            if is_a_non_log_line(line):
                currentLine.append_non_log_line(line.raw.strip())
            else:
                currentLine.append_text(line.raw)
        else:
            errors.append("Encountered An initial Line without nominal timestamp:  \n%s" % line.raw)
    
    translatedLines.append(currentLine)
    
    return translatedLines          

def validate_line(line):
    try:
        line.seconds_from_mission_start
        line.page
        line.tape
        line.speaker
        line.text
    except:
        errors.append("Invalid line found at %d" % line.seconds_from_mission_start)
        return False
    
    if line.speaker in valid_tec_speakers:
        return True
    
    errors.append("Line with invalid speaker found at %d" % line.seconds_from_mission_start)
    return False

def get_formatted_record_for(line):
    if validate_line(line):
        lines = []
        lines.append(u"\n[%d]\n" % line.seconds_from_mission_start)
        lines.append(u"_page : %d\n" % line.page)
        lines.append(u"_tape : %s\n" % line.tape)
        if len(line.non_log_lines) > 0:
            lines.append(u"_extra : %s\n" % "/n".join(line.non_log_lines))
        lines.append((u"%s: %s" % (line.speaker, line.text,)).encode('utf-8'))
        return lines
    else:
        return []
    
class LogLine:
    def __init__(self, pageNumber, tapeNumber, rawLine):
        self.raw = rawLine
        self.page = pageNumber
        self.tape = tapeNumber
        self.speaker = ""
        self.non_log_lines = []

    def get_raw_line(self):
        return self.raw
    
    def set_text(self, text):
        self.text = text
    
    def append_text(self, text):
        self.text = self.text + (" " * 5) + text
        
    def set_seconds_from_mission_start(self, seconds_from_mission_start):
        self.seconds_from_mission_start = seconds_from_mission_start
    
    def set_speaker(self, speaker):
        self.speaker = speaker
        
    def append_non_log_line(self, line):
        self.non_log_lines.append(line)

def check_lines_are_in_sequence(lines):
    currentTime = -20000000
    for line in lines:
        if line.seconds_from_mission_start < currentTime:
            errors.append("Line out of Sync error at %d seconds from mission start" %line.seconds_from_mission_start)
            print(get_formatted_record_for(line))
        currentTime = line.seconds_from_mission_start

class BadNumberSub:
    def __init__(self, number, badSubList):
        self.number = number
        self.badSubList = badSubList

def report_errors_and_exit():
    if len(errors) > 0:
        print "Shred returned errors, please check the following:"
        for error in errors:
            print error
        sys.exit(1)
    
    print "No errors found"    
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "usage MCShred.py <pathToCompletedFiles> <fileNumberToStartWith>"
        print "ex: MCShred.py /assets/transcripts/apollo13/AS13_TEC/0_CLEAN/ 8"
    
    file_path = sys.argv[1]
    file_number = int(sys.argv[2])
    allRawLines = get_all_raw_lines(file_path, file_number)
    
#    for a in allRawLines:
#        print(a)
    
    all_lines = translate_lines(allRawLines)
    
    outputFile = open(file_path + "output.txt", "w")
    
#    print all_lines[0].page
#    print all_lines[0].tape
#    print all_lines[0].speaker
#    print all_lines[0].text
    
    check_lines_are_in_sequence(all_lines)
    
    for goodLine in all_lines:
        outputFile.writelines(get_formatted_record_for(goodLine))
    
    outputFile.close()
    
    report_errors_and_exit()