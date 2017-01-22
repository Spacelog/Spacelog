#!/usr/bin/python

import sys
import re
from optparse import OptionParser

DEFAULT_TIMESTAMP_PARTS = 4
SECONDS_OFFSET = 0

pageNumber = 1

errors = []
       
def get_file_name_for(num):
    return str(num).zfill(3) + ".txt"

def shred_to_lines(lines, timestamp_parts=4):
    global pageNumber
    logLines = []
    tapeNumber = None
    prefixSpaces = None # how many spaces should we strip from the start?
        
    for number, line in enumerate(lines):
        line = line.decode('utf-8')
        try:
            if line.strip().startswith(u"Page"):
                pageNumber = int(line.strip().lstrip(u"Page ").strip())
                prefixSpaces = None
            elif line.strip().startswith(u"Tape "):
                tapeNumber = line.lstrip(u"Tape ").strip()
            elif line.strip().startswith(u"PAGE"):
                # Page number from transcript (ignore)
                print "Skipping line %i on page %i: %s" % (
                    number+1,
                    pageNumber,
                    line.strip(),
                )
            elif re.match('^[0-9]+$', line.strip()):
                # Almost certainly a page number from the transcript (ignore)
                print "Skipping line %i on page %i: %s" % (
                    number+1,
                    pageNumber,
                    line.strip(),
                )
            else:
                # If this is the first "real" line then figure out how
                # many spaces it has on the left, and mark to strip
                # those from all subsequent lines. Real lines start
                # with a timestamp (continuation lines and oddities
                # like ground station markers should work without
                # stripping, and if we strip based on that we'll have
                # a problem).
                if prefixSpaces is None:
                    if re.match("^[0-9]{2}:", line.lstrip()):
                        actual_line = line.lstrip()
                        prefixSpaces = len(line) - len(actual_line)
                        if line[0] == '\t':
                            errors.append(
                                "Leading tab on line %i: %s" % (
                                    number+1,
                                    line.strip(),
                                )
                            )
                if prefixSpaces is None:
                    logLines.append(
                        LogLine(pageNumber, tapeNumber, number, line)
                    )
                else:
                    # We only check if the expected prefix contains
                    # non-whitespace on this line. If whitespace
                    # continues beyond the prefix, that's probably the
                    # indentation of a continuation line, or the tab
                    # indenting an extra line, so we don't want to
                    # complain.
                    if line[:prefixSpaces].strip() != "":
                        raise Exception("Whitespace prefix changed within page")
                    if prefixSpaces != len(line) - len(line.lstrip()):
                        # More space beyond the prefix. We should check to
                        # see if it starts with something that might be
                        # a timestamp, and warn about that.
                        if re.match(
                                '^' + ':'.join(
                                    '[0-9]{2}'
                                    for n in range(0, timestamp_parts)
                                ) + ' ', line.lstrip()
                        ):
                            errors.append(
                                "Possible logline start over-indented on line %i: %s" % (
                                    number+1, line.strip()
                                )
                            )
                    logLines.append(
                        LogLine(
                            pageNumber, tapeNumber,
                            number, line[prefixSpaces:],
                        )
                    )
        except:
            print "Failed on line %i: %s" % (number+1, line)
            raise

    return logLines

def get_all_raw_lines(path, timestamp_parts=4):
    translated_lines = []
    try:
        file = open(path, "r")
        file_lines = file.readlines()
        shredded_lines = shred_to_lines(file_lines, timestamp_parts)
        translated_lines.extend(shredded_lines)
    except IOError:
        errors.append("Could not find the file: " + path)
        
    return translated_lines    

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

def get_seconds_from_mission_start(line, timestamp_parts):
    return translate_timestamp_to_seconds_from_mission_start(line.raw, timestamp_parts)

def translate_timestamp_to_seconds_from_mission_start(timestamp, timestamp_parts):
    values =  re.split("[ \t\:]+", timestamp);
    i = 0
    days = 0
    if timestamp_parts > 3:
        days = int(sterilize_token(values[i]))
        i += 1
    hours = int(sterilize_token(values[i]))
    i += 1
    minutes = int(sterilize_token(values[i]))
    i += 1
    seconds = int(sterilize_token(values[i]))
    
    return (seconds + (minutes * 60) + (hours * 60 * 60) + (days * 24 * 60 * 60)) - SECONDS_OFFSET

def set_timestamp_speaker_and_text(line, timestamp_parts):
    
    values =  re.split("[ \t\:]+", line.raw);
   
    line.set_seconds_from_mission_start(get_seconds_from_mission_start(line, timestamp_parts))
    
    if len(values) > timestamp_parts:
        line.set_speaker(values[timestamp_parts])
    else:
        line.set_speaker(u"_note")
        
    if len(values) > (timestamp_parts + 1):
        line.set_text(" ".join(values[timestamp_parts + 1:]))
    else:
        line.set_text(u"")

def line_is_a_new_entry(line, timestamp_parts):
    
    dateTokens = re.split('[ \t\:]+', line.raw)

    if len(dateTokens) < timestamp_parts:
        return False
    
    dateTokens = dateTokens[0:timestamp_parts]
    
    for token in dateTokens:
        try:
            int(token)
        except:
            return False

    if timestamp_parts == 3 and (
            int(dateTokens[1]) > 59 or int(dateTokens[2]) > 59):
        return False

    if timestamp_parts == 4 and (
            int(dateTokens[0]) > 20 or int(dateTokens[1]) > 23
            or int(dateTokens[2]) > 59 or int(dateTokens[3]) > 59):
        return False

    return True

def is_a_non_log_line(line):
    # non log line => extra, ie not speech
    return len(line.raw) == 0 or line.raw[0] == '\t'

def translate_lines(translated_lines, verbose=False, timestamp_parts=DEFAULT_TIMESTAMP_PARTS):
    translatedLines = []
    currentLine = None

    for number, line in enumerate(translated_lines):
        if line_is_a_new_entry(line, timestamp_parts):
            if currentLine != None:
                translatedLines.append(currentLine)
            if verbose:
                print line.raw
            set_timestamp_speaker_and_text(line, timestamp_parts)
            currentLine = line
        elif currentLine != None:
            if line.raw.strip():
                if is_a_non_log_line(line):
                    currentLine.append_non_log_line(line.raw.strip())
                else:
                    # One or more capitals (eg CC, CDR, P), followed by
                    # at least two spaces.
                    if re.match(
                            '^[A-Z]+  +',
                            line.raw.lstrip()
                    ):
                        errors.append(
                            "Line %i suspect continuation: %s" % (number+1, line.raw.strip())
                        )
                    currentLine.append_text(line.raw.lstrip())
        else:
            errors.append("Line %i has no nominal timestamp: %s" % (number+1, line.raw.strip()))
    
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
        errors.append("Invalid line found at %s" % get_timestamp_as_mission_time(line))
        return False
    
    return True    


last_tape = None
last_page = None

def get_formatted_record_for(line):
    "Returns a correctly-formatted line."
    # These really shouldn't be globals, but I'm not ready to refactor
    # this all into a big class and use instance variables.
    global last_page, last_tape
    if validate_line(line):
        lines = []
        lines.append(u"\n[%s]\n" % get_timestamp_as_mission_time(line))
#        lines.append(u"\n[%d]\n" % line.seconds_from_mission_start)
        if line.page != last_page:
            lines.append(u"_page : %d\n" % line.page)
            last_page = line.page
        if line.tape != last_tape:
            lines.append(u"_tape : %s\n" % line.tape)
            last_tape = line.tape
        if len(line.non_log_lines) > 0:
            lines.append(u"_extra : %s\n" % "\n".join(line.non_log_lines))
        lines.append(u"%s: %s" % (line.speaker, line.text,))
        return lines
    else:
        return []
    


def check_lines_are_in_sequence(lines):
    currentTime = -20000000
    for line in lines:
        if line.seconds_from_mission_start < currentTime:
            errors.append("Line out of Sync error at %s" % get_timestamp_as_mission_time(line))
        currentTime = line.seconds_from_mission_start

def report_errors_and_exit():
    if len(errors) > 0:
        print "Shred returned errors, please check the following:"
        for error in errors:
            print error
        sys.exit(1)
    
    print "No errors found"    
    sys.exit(0)

def output_lines_to_file(lines, output_file_name_and_path):
    outputFile = open(output_file_name_and_path, "w")
    for i, line in enumerate(lines):
        try:
            outputFile.writelines(
                map(
                    lambda x: x.encode('utf8'),
                    get_formatted_record_for(line),
                )
            )
        except:
            print >>sys.stderr, "Failure in line %i (raw line %i)" % (i, line.line)
            raise
    outputFile.close()

def amalgamate_lines_by_timestamp(lines):
    amalgamated_lines = []
    last_line = lines[0]
    for line in lines[1:]:
        if last_line.seconds_from_mission_start == line.seconds_from_mission_start:
            last_line.append_second_line_content(line)
        else:
            amalgamated_lines.append(last_line)
            last_line = line
    amalgamated_lines.append(last_line)

    return amalgamated_lines

def get_timestamp_as_mission_time(line):
    sec = line.seconds_from_mission_start
    days = sec // 86400
    hours = (sec // 3600) % 24
    minutes = (sec // 60) % 60
    seconds = sec % 60
    
    return "%02d:%02d:%02d:%02d" % (days, hours, minutes, seconds)

class LogLine:
    def __init__(self, pageNumber, tapeNumber, lineNumber, rawLine):
        self.raw = rawLine
        self.page = pageNumber
        self.tape = tapeNumber
        self.line = lineNumber
        self.speaker = ""
        self.non_log_lines = []

    def get_raw_line(self):
        return self.raw
    
    def set_text(self, text):
        self.text = text
    
    def append_text(self, text):
        self.text = self.text + (" " * 5) + text
        
    def append_second_line_content(self, line):
        self.text = self.text + "\n%s: %s" % (line.speaker, line.text)
        
    def set_seconds_from_mission_start(self, seconds_from_mission_start):
        self.seconds_from_mission_start = seconds_from_mission_start
    
    def set_speaker(self, speaker):
        self.speaker = speaker
        
    def append_non_log_line(self, line):
        self.non_log_lines.append(line)

class BadNumberSub:
    def __init__(self, number, badSubList):
        self.number = number
        self.badSubList = badSubList

if __name__ == "__main__":
    usage = "usage: %prog [options] input_file output_file\n" + "eg: %prog missions/a18/TEC.txt missions/a18/transcripts/TEC"
    
    parser = OptionParser(usage=usage)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help="print out parsed lines")
    parser.add_option('-t', '--timestamp-parts', dest='timestamp_parts', type='int', default=DEFAULT_TIMESTAMP_PARTS, help="the number of values in the line timestamps (e.g. 3 for hours, minutes and second)")
    (options, args) = parser.parse_args()
    
    if len(args)!=2:
        parser.print_help()
        sys.exit(0)
    
    file_path = args[0]
    output_file = args[1]
    allRawLines = get_all_raw_lines(file_path, options.timestamp_parts)
    print "Read in %d raw lines (%d non-blank)." % (len(allRawLines), len(filter(lambda x: x.raw.strip(), allRawLines)))
    translated_lines = translate_lines(allRawLines, options.verbose, options.timestamp_parts)
    print "Translated to %d lines." % len(translated_lines)
    check_lines_are_in_sequence(translated_lines)
    
    amalgamated_lines = amalgamate_lines_by_timestamp(translated_lines)
    
    output_lines_to_file(amalgamated_lines, output_file)
        
    report_errors_and_exit()
