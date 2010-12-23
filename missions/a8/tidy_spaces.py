import sys
import re

def get_lines(in_file):
    f = open(in_file,"r")
    all = f.readlines()
    f.close()
    return all

def tidy_lines(lines):
    tidied = []
    for line in lines:
        line = line.decode('utf-8')
        if re.match(r'^(\d\d \d\d \d\d \d\d)    ([A-Z]{2,})\t(\w+.*)$', line):
            m = re.match(r'^(\d\d \d\d \d\d \d\d)    ([A-Z]{2,})\t(\w+.*)$', line)
            timestamp = m.group(1)
            speaker = m.group(2)
            spaces_needed = 15 - len(speaker)
            spaces = "".join(" " for i in range(1,spaces_needed))
            text = m.group(3)
            words = text.split()
            tidy_text = " ".join(words)
            #print spaces_needed
            #print "new log"
            #column widths: timestamp=15 speaker=15 text=unbounded
            tidy_line = (u"%s    %s%s %s\n" % (timestamp, speaker, spaces, tidy_text)).encode('utf-8')
            print tidy_line
            tidied.append(tidy_line)
            
        elif re.match(r'^            \t\t(\w+.*)$', line):
            m = re.match('^            \t\t(\w+.*)$', line)
            text = m.group(1)
            words = text.split()
            tidy_text = " ".join(words)
            spaces = "".join(" " for i in range(0,30))
            tidy_line = (u"%s%s\n" % (spaces, tidy_text)).encode('utf-8')
            print tidy_line
            tidied.append(tidy_line)
        else:
            #print "unknown line"
            print line.encode('utf-8')
            tidied.append(line.encode('utf-8'))
    return tidied

def write_to_output(out_file, lines):
    f = open(out_file,"w")
    f.writelines(lines)
    f.close()

if __name__ == "__main__":
    in_file_name=sys.argv[1]
    out_file_name=sys.argv[2]
    lines = get_lines(in_file_name)
    tidied_lines = tidy_lines(lines)
    write_to_output(out_file_name, tidied_lines)
    #for line in tidied_lines:
       #print line