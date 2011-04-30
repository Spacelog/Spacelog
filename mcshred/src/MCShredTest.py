#!/usr/bin/python
import unittest
import MCShred


class Test(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def test_sterilize_token(self):
        assert int(MCShred.sterilize_token("00")) == 0
        assert int(MCShred.sterilize_token("01")) == 1
        assert int(MCShred.sterilize_token("l0")) == 10
        assert int(MCShred.sterilize_token("BB")) == 88
        assert int(MCShred.sterilize_token("Bh")) == 84
        assert int(MCShred.sterilize_token("lo")) == 10
        assert int(MCShred.sterilize_token("OQo")) == 0
        assert int(MCShred.sterilize_token("iJI!Ll")) == 111111
        assert int(MCShred.sterilize_token("B")) == 8
        assert int(MCShred.sterilize_token("h")) == 4
        
        assert int(MCShred.sterilize_token(u"00")) == 0
        assert int(MCShred.sterilize_token(u"01")) == 1
        assert int(MCShred.sterilize_token(u"l0")) == 10
        assert int(MCShred.sterilize_token(u"BB")) == 88
        assert int(MCShred.sterilize_token(u"Bh")) == 84
        assert int(MCShred.sterilize_token(u"lo")) == 10
        assert int(MCShred.sterilize_token(u"OQo")) == 0
        assert int(MCShred.sterilize_token(u"iJI!Ll")) == 111111
        assert int(MCShred.sterilize_token(u"B")) == 8
        assert int(MCShred.sterilize_token(u"h")) == 4
    
    def test_log_line(self):
        logLine = MCShred.LogLine(5, u"5/1", u"00 01 03 59 CC This is the rest of the line")
        
        assert logLine.page == 5
        assert logLine.tape == u"5/1"
        assert logLine.raw == u"00 01 03 59 CC This is the rest of the line"
        
    def test_get_seconds_from_mission_start(self):
        logLine = MCShred.LogLine(5, u"5/1", u"01 02 03 59 CC This is the rest of the line")
        expectedTime = (59 + (3 * 60) + (2 * 60 * 60) + (1 * 24 * 60 * 60))
        
        
#        print('expected time %d' % expectedTime)
#        print('got time of %d' % MCShred.get_seconds_from_mission_start(logLine))
        assert MCShred.get_seconds_from_mission_start(logLine) == expectedTime
        
    def test_get_seconds_from_mission_start_will_work_with_full_colon_seperated_timestamps(self):
        logLine = MCShred.LogLine(5, u"5/1", u"01:02:03:59 CC This is the rest of the line")
        expectedTime = (59 + (3 * 60) + (2 * 60 * 60) + (1 * 24 * 60 * 60))
        
        
#        print('expected time %d' % expectedTime)
#        print('got time of %d' % MCShred.get_seconds_from_mission_start(logLine))
        assert MCShred.get_seconds_from_mission_start(logLine) == expectedTime
        
    def test_set_timestamp_speaker_and_text(self):
        logLine = MCShred.LogLine(5, u"5/1", u"01 02 03 59 CC This is the rest of the line")
        
        MCShred.set_timestamp_speaker_and_text(logLine)
        
        expectedTime = (59 + (3 * 60) + (2 * 60 * 60) + (1 * 24 * 60 * 60))
        
#        print(expectedTime)
#        print(logLine.seconds_from_mission_start)
        
        assert logLine.seconds_from_mission_start == expectedTime
        assert logLine.speaker == u"CC"
        assert logLine.text == "This is the rest of the line"
        
    def test_line_is_a_new_entry(self):
        logLine1 = MCShred.LogLine(5, u"5/1", u"01 02 03 59 CC This is the rest of the line")
        logLine2 = MCShred.LogLine(5, u"5/1", u"except for this thing because it's actually")
        logLine3 = MCShred.LogLine(5, u"5/1", u"a three line comment")
        
        assert MCShred.line_is_a_new_entry(logLine1) == True
        assert MCShred.line_is_a_new_entry(logLine2) == False
        assert MCShred.line_is_a_new_entry(logLine3) == False
        
    def test_shred_to_lines(self):
        logLine0 = u"Tape 3/2"
        logLine1 = u"01 02 03 59 CC This is the rest of the line"
        logLine2 = u"except for this thing because it's actually"
        logLine3 = u"a three line comment"
        
        logLines = (logLine0, logLine1, logLine2, logLine3,)
        
        shreddedLines = MCShred.shred_to_lines(logLines)
        
        assert len(shreddedLines) == 3
        assert shreddedLines[0].page == 1
        assert shreddedLines[1].page == 1
        assert shreddedLines[2].page == 1
        assert shreddedLines[0].tape == u"3/2"
        assert shreddedLines[1].tape == u"3/2"
        assert shreddedLines[2].tape == u"3/2"
        assert shreddedLines[0].raw == logLine1
        assert shreddedLines[1].raw == logLine2
        assert shreddedLines[2].raw == logLine3
        
    def test_translate_lines(self):
        logLine0 = u"Tape 3/2"
        logLine1 = u"01 02 03 59 CC This is the rest of the line"
        logLine2 = u"except for this thing because it's actually"
        logLine3 = u"a three line comment"
        
        logLines = (logLine0, logLine1, logLine2, logLine3,)
        
        shreddedLines = MCShred.shred_to_lines(logLines)
        
        translatedLines = MCShred.translate_lines(shreddedLines)
        
        print(translatedLines[0].text)
        
        assert len(translatedLines) == 1
        assert translatedLines[0].page == 1
        assert translatedLines[0].tape == u"3/2"
        assert translatedLines[0].speaker == u"CC"
        assert translatedLines[0].text == u"This is the rest of the line" + "     " + logLine2 + "     " + logLine3

    def test_get_filename_for(self):
        assert MCShred.get_file_name_for(0) == u"000.txt"
        assert MCShred.get_file_name_for(1) == u"001.txt"
        assert MCShred.get_file_name_for(12) == u"012.txt"
        assert MCShred.get_file_name_for(304) == u"304.txt"
        assert MCShred.get_file_name_for(200) == u"200.txt"
        assert MCShred.get_file_name_for(003) == u"003.txt"
        
    def test_is_a_non_log_line(self):
        logLine0 = make_log_line(u"Tape 3/2")
        logLine1 = make_log_line(u"01 02 03 59 CC This is the rest of the line")
        logLine2 = make_log_line(u"  except for this thing because it's actually")
        logLine3 = make_log_line(u"    ( other weird text Thing )")
        logLine4 = make_log_line(u"")
        assert MCShred.is_a_non_log_line(logLine0) == False
        assert MCShred.is_a_non_log_line(logLine1) == False
        assert MCShred.is_a_non_log_line(logLine2) == True
        assert MCShred.is_a_non_log_line(logLine3) == True
        assert MCShred.is_a_non_log_line(logLine4) == True
        
    def test_if_no_speaker_indicated_it_is_considered_a_note(self):
        logLine = MCShred.LogLine(5, u"5/1", u"01 02 03 59")
        
        MCShred.set_timestamp_speaker_and_text(logLine)
        
        expectedTime = (59 + (3 * 60) + (2 * 60 * 60) + (1 * 24 * 60 * 60))
        
#        print(expectedTime)
#        print(logLine.seconds_from_mission_start)
        
        assert logLine.seconds_from_mission_start == expectedTime
        assert logLine.speaker == u"_note"
        assert logLine.text == ""
        

def make_log_line(content):
    return MCShred.LogLine(0, 0, content)        
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
