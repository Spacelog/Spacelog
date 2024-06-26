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
    
    def test_log_line(self):
        logLine = MCShred.LogLine(5, "5/1", 1, "00 01 03 59 CC This is the rest of the line")
        
        assert logLine.page == 5
        assert logLine.tape == "5/1"
        assert logLine.line == 1
        assert logLine.raw == "00 01 03 59 CC This is the rest of the line"
        
    def test_get_seconds_from_mission_start(self):
        logLine = MCShred.LogLine(5, "5/1", 1, "01 02 03 59 CC This is the rest of the line")
        expectedTime = (59 + (3 * 60) + (2 * 60 * 60) + (1 * 24 * 60 * 60))

        assert MCShred.get_seconds_from_mission_start(logLine, timestamp_parts=4) == expectedTime

    def test_get_seconds_from_mission_start_will_work_with_full_colon_seperated_timestamps(self):
        logLine = MCShred.LogLine(5, "5/1", 1, "01:02:03:59 CC This is the rest of the line")
        expectedTime = (59 + (3 * 60) + (2 * 60 * 60) + (1 * 24 * 60 * 60))

        assert MCShred.get_seconds_from_mission_start(logLine, timestamp_parts=4) == expectedTime

    def test_get_seconds_from_mission_start_will_work_with_abbreviated_timestamps(self):
        logLine = MCShred.LogLine(5, "5/1", 1, "25:03:59 CC This is the rest of the line")
        expectedTime = (59 + (3 * 60) + (25 * 60 * 60))

        assert MCShred.get_seconds_from_mission_start(logLine, timestamp_parts=3) == expectedTime

    def test_set_timestamp_speaker_and_text(self):
        logLine = MCShred.LogLine(5, "5/1", 1, "01 02 03 59 CC This is the rest of the line")
        
        MCShred.set_timestamp_speaker_and_text(logLine, timestamp_parts=4)
        
        expectedTime = (59 + (3 * 60) + (2 * 60 * 60) + (1 * 24 * 60 * 60))
        
#        print(expectedTime)
#        print(logLine.seconds_from_mission_start)
        
        assert logLine.seconds_from_mission_start == expectedTime
        assert logLine.speaker == "CC"
        assert logLine.text == "This is the rest of the line"
        
    def test_line_is_a_new_entry(self):
        timestamp_parts = 4
        logLine1 = MCShred.LogLine(5, "5/1", 1, "01 02 03 59 CC This is the rest of the line")
        logLine2 = MCShred.LogLine(5, "5/1", 2, "except for this thing because it's actually")
        logLine3 = MCShred.LogLine(5, "5/1", 3, "a three line comment")
        
        assert MCShred.line_is_a_new_entry(logLine1, timestamp_parts) == True
        assert MCShred.line_is_a_new_entry(logLine2, timestamp_parts) == False
        assert MCShred.line_is_a_new_entry(logLine3, timestamp_parts) == False

    def test_line_is_a_new_entry_will_work_with_three_timestamp_parts(self):
        timestamp_parts = 3
        logLine1 = MCShred.LogLine(5, "5/1", 1, "26 03 59 CC This is the rest of the line")
        logLine2 = MCShred.LogLine(5, "5/1", 2, "except for this thing because it's actually")
        logLine3 = MCShred.LogLine(5, "5/1", 3, "a three line comment")

        assert MCShred.line_is_a_new_entry(logLine1, timestamp_parts) == True
        assert MCShred.line_is_a_new_entry(logLine2, timestamp_parts) == False
        assert MCShred.line_is_a_new_entry(logLine3, timestamp_parts) == False

    def test_shred_to_lines(self):
        logLine0 = "Tape 3/2"
        logLine1 = "01 02 03 59 CC This is the rest of the line"
        logLine2 = "except for this thing because it's actually"
        logLine3 = "a three line comment"
        
        logLines = (logLine0, logLine1, logLine2, logLine3,)
        
        shreddedLines = MCShred.shred_to_lines(logLines)
        
        assert len(shreddedLines) == 3
        assert shreddedLines[0].page == 1
        assert shreddedLines[1].page == 1
        assert shreddedLines[2].page == 1
        assert shreddedLines[0].tape == "3/2"
        assert shreddedLines[1].tape == "3/2"
        assert shreddedLines[2].tape == "3/2"
        assert shreddedLines[0].raw == logLine1
        assert shreddedLines[1].raw == logLine2
        assert shreddedLines[2].raw == logLine3
        
    def test_translate_lines(self):
        logLine0 = "Tape 3/2"
        logLine1 = "01 02 03 59 CC This is the rest of the line"
        logLine2 = "except for this thing because it's actually"
        logLine3 = "a three line comment"
        
        logLines = (logLine0, logLine1, logLine2, logLine3,)
        
        shreddedLines = MCShred.shred_to_lines(logLines)
        
        translatedLines = MCShred.translate_lines(shreddedLines)
        
        assert len(translatedLines) == 1
        assert translatedLines[0].page == 1
        assert translatedLines[0].tape == "3/2"
        assert translatedLines[0].speaker == "CC"
        assert translatedLines[0].text == "This is the rest of the line" + "     " + logLine2 + "     " + logLine3

    def test_get_filename_for(self):
        assert MCShred.get_file_name_for(0) == "000.txt"
        assert MCShred.get_file_name_for(1) == "001.txt"
        assert MCShred.get_file_name_for(12) == "012.txt"
        assert MCShred.get_file_name_for(304) == "304.txt"
        assert MCShred.get_file_name_for(200) == "200.txt"
        assert MCShred.get_file_name_for(0o03) == "003.txt"
        
    def test_is_a_non_log_line(self):
        logLine0 = make_log_line("Tape 3/2")
        logLine1 = make_log_line("01 02 03 59 CC This is the rest of the line")
        logLine2 = make_log_line("  except for this thing because it's actually")
        logLine3 = make_log_line("    ( other weird text Thing )")
        logLine4 = make_log_line("")
        assert MCShred.is_a_non_log_line(logLine0) == False
        assert MCShred.is_a_non_log_line(logLine1) == False
        assert MCShred.is_a_non_log_line(logLine2) == True
        assert MCShred.is_a_non_log_line(logLine3) == True
        assert MCShred.is_a_non_log_line(logLine4) == True

    def test_if_no_speaker_indicated_it_is_considered_a_note(self):
        logLine = MCShred.LogLine(5, "5/1", 1, "01 02 03 59")

        MCShred.set_timestamp_speaker_and_text(logLine, timestamp_parts=4)

        expectedTime = (59 + (3 * 60) + (2 * 60 * 60) + (1 * 24 * 60 * 60))

        assert logLine.seconds_from_mission_start == expectedTime
        assert logLine.speaker == "_note"
        assert logLine.text == ""


def make_log_line(content):
    return MCShred.LogLine(0, 0, 0, content)


if __name__ == "__main__":
    unittest.main()
