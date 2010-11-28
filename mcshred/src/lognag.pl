#!/usr/bin/env perl
# $Id$

# Not an entry for the obfuscated perl contest

use strict;
use warnings;
use Data::Dumper;
use Getopt::Long;

my $help;
my $inline_timestamp_format;
my $inline_timestamp_regex = '\d+:\d\d(?::\d+)?(?:\.\d\d?)?';
my $inline_timestamps;
my $invalid_inline_timestamps;
my $log_timestamp_elements = 4;
my $output_dir;
my $report_fail;
my $show_stats;
my $x_fort;

if (
    !GetOptions(
        'report|f=s'                  => \$report_fail,
        'help|h'                      => \$help,
        'fort'                        => \$x_fort,
        'inline-timestamps|T'         => \$inline_timestamps,
        'invalid-inline-timestamps|I' => \$invalid_inline_timestamps,
        'log-timestamp-elements|t=i'  => \$log_timestamp_elements,
        'stats-porn|v'                => \$show_stats,
        'output-dir|o=s'              => \$output_dir,
    )
    || $help
    || !@ARGV
  )
{
    print "Usage: lognag.pl [files]
                      --help : This help
                      --fort : Run with additional /dev/fort filter
         --inline-timestamps : Search and markup 'valid' inline timestamps
 --invalid-inline-timestamps : Search and markup 'invalid' inline timestamps
--log-timestamp-elements num : Number of timestamp elements in log lines (default 4)
              --report regex : Only report failures of type 'regex'
	    --output-dir dir : Write sanitised/updated files into dir
                --stats-porn : Show some stats on speakers
eg:
   ./lognag.pl AS13_TEC/0_CLEAN/[0-9]*.txt

lognag will sort files on the commandline by filename, excluding
directory component

It parses timestamp log lines and check for increasing timestamps.
It also tries to handle and warn about a relatively high level of
OCR damage.
If it finds a line starting Speakers: it takes the rest of the line
as a whitespace separated list of valid speakers on loglines.

";
    exit;
}

my $x_last_lognag = 0;
my $x_last_tea    = 0;
my $x_last_bacon  = 0;
my %valid_speaker;
my $last = -60 * 60;    # Allow for up to T minus 1 hour
my %badfiles;
my %speakers;
my $total_fail;
setup_valid_speakers(
    'AB CC CDR CMP CT F IWO LCC LMP MS P-1 P-2 R R-1 R-2 S S-1 S-2 SC Music G');

foreach my $file ( sort filesort @ARGV ) { process($file); }
print 'Bad files: ', join( ' ', sort keys %badfiles ), "\n" if %badfiles;
print 'Fail: ', $total_fail, "\n" if $total_fail;

if ($show_stats) {
    foreach my $speaker ( sort keys %speakers ) {
        my $perday;
        my $total;
        for ( my $day = 0 ; $day < @{ $speakers{$speaker} } ; ++$day ) {
            $speakers{$speaker}[$day] ||= 0;
            $perday .= sprintf( '%4d ', $speakers{$speaker}->[$day] );
            $total += $speakers{$speaker}[$day];
        }
        chop $perday;
        printf "%5s: %4d    ($perday)\n", $speaker, $total;
    }
}
exit;

sub filesort {

    # Ensure we process the files sorted by filename not by pathname
    my $fa = $a;
    my $fb = $b;
    $fa =~ s:.*/::;
    $fb =~ s:.*/::;
    return $fa cmp $fb;
}

sub parse_inline_timestamp {
    my ( $logtimestamp, $timestamptxt ) = @_;

    my $valid;
    my $parsed;

    if ( defined $inline_timestamp_format ) {
        if ( $inline_timestamp_format eq 'HH MM SS' ) {
            if ( $timestamptxt =~ /\b(\d\d) (\d\d) (\d\d)\b$/ ) {
                $parsed = $1 * 60 * 60 + $2 * 60 + $3;
                $valid = $parsed if ( $parsed && $parsed > $logtimestamp );
            }

        }
        else {
            die
"Cannot understand inline timestamp format $inline_timestamp_format";
        }

    }

    else    # Apollo 13
    {

        if ( $timestamptxt =~ /^(\d+):(\d+):(\d+)\.\d+$/ ) {
            $valid = $1 * 60 * 60 + $2 * 60 + $3;
        }

        # Some magic numbers for Apollo13 which are modified
        $valid = 135 * 60 * 60 + 4 * 60 + 25 if $timestamptxt eq '35:04:25';

        if ( !$valid ) {
            if ( $timestamptxt =~ /^(\d+):(\d+):(\d+)$/ ) {
                $parsed = $1 * 60 * 60 + $2 * 60 + $3;
            }
            elsif ( $timestamptxt =~ /^(\d+):(\d+)(?:\.\d+)?$/ ) {
                if ( $timestamptxt eq '52:36' || $timestamptxt eq '5:32' ) {
                    $valid = $1 * 60 + $2;
                }
                else {
                    $parsed = $1 * 60 * 60 + $2 * 60;
                }
            }
            else {
                warn("Unable to parse timestamp '$timestamptxt'");
            }

            # Apollo 13
            ( $valid = $parsed )
              if $parsed && $parsed > 485900 && $parsed < 514000;

        }
    }
    if ( $parsed && !$valid ) {
        my $percent_change =
          100 * abs( $logtimestamp - $parsed ) / $logtimestamp;
        $valid = $parsed if $percent_change < 25;
    }

    return $parsed if $invalid_inline_timestamps && !$valid;
    return $valid if $inline_timestamps;
    return;
}

sub parse_log_timestamp {
    my ( $words, $fail ) = @_;

    my $timestamp = $words->[ $log_timestamp_elements - 1 ];
    if ( $log_timestamp_elements > 1 ) {
        push( @{$fail}, 'badsec' )
          if $words->[ $log_timestamp_elements - 1 ] > 60;
        $timestamp += $words->[ $log_timestamp_elements - 2 ] * 60;
    }
    if ( $log_timestamp_elements > 2 ) {
        push( @{$fail}, 'badmin' )
          if $words->[ $log_timestamp_elements - 2 ] > 60;
        $timestamp += $words->[ $log_timestamp_elements - 3 ] * 60 * 60;
    }
    if ( $log_timestamp_elements > 3 ) {
        push( @{$fail}, 'badhour' )
          if $words->[ $log_timestamp_elements - 3 ] > 24;
        $timestamp += $words->[ $log_timestamp_elements - 4 ] * 60 * 60 * 24;
    }
    return $timestamp;
}

sub process {
    my ($file) = @_;

    my $cleandata = '';
    open( FILE, "<$file" ) || die("Unable to open $file: $!");
    while ( my $line = <FILE> ) {
        my @fail;
        my @words    = split( ' ', $line, $log_timestamp_elements + 2 );
        my $logscore = 0;
        my $fix      = 0;
        my $txt      = $line;

        if ( $line =~ /Speakers:\s+(.*)/ ) {
            setup_valid_speakers($1);
            $cleandata .= $line;
            next;
        }
        if ( $line =~ /LogTimestamp:\s+(.*)/ ) {
            setup_log_timestamp_format($1);
            $cleandata .= $line;
            next;
        }
        if ( $line =~ /InlineTimestamp:\s+(.*)/ ) {
            setup_inline_timestamp_format($1);
            $cleandata .= $line;
            next;
        }

        if ( @words > $log_timestamp_elements ) {
            for ( my $i = 0 ; $i < $log_timestamp_elements ; ++$i ) {
                if ( $words[$i] =~ /^[a-zA-Z']{3,}[.,]?$/ ) {
                    $logscore -= 2;
                    next;
                }
                $fix += $words[$i] =~ s/[({\[][)}\]]/0/g;
                $fix += $words[$i] =~ s/[iJI!Ll\]\[]/1/g;
                $fix += $words[$i] =~ s/[oQO]/0/g;
                $fix += $words[$i] =~ s/[B]/8/g;
                $fix += $words[$i] =~ s/[h]/4/g;
                --$logscore if $words[$i] =~ /^[a-z]+$/;
                if   ($i) { ++$logscore if $words[$i] =~ /^\d{2}$/; }
                else      { ++$logscore if $words[$i] =~ /^-?\d{2}$/; }
            }
            my $speaker = $words[$log_timestamp_elements];
            $speaker = 'Music' if $speaker =~ /^\(Music/;

            # log timestamp passed enough tests
            if ( $logscore && $logscore > $log_timestamp_elements - 1 ) {
                my @speakers =
                  grep( !$valid_speaker{$_}, split( '/', $speaker ) );
                push( @fail, 'imposter:' . join( ',', @speakers ) )
                  if @speakers;
                foreach my $spkr ( split( '/', $speaker ) ) {
                    ++$speakers{$spkr}[ $words[0] ];
                    $txt = $words[ $log_timestamp_elements + 1 ];
                }
            }

            # log timestamp passed tests
            if ( $logscore == $log_timestamp_elements ) {
                my $now = parse_log_timestamp( \@words, \@fail );
                if ($x_fort) {
                    my $min = $now / 60 % 60;
                    my $hour = $now / ( 60 / 60 ) % 24;
                    if ( $now > $x_last_tea + 60 * 60 ) {
                        push( @fail, 'george-make-tea' );
                        $x_last_tea = $now;
                    }
                    if ( $now > $x_last_lognag + 60 * 61 * 20 ) {
                        my $r   = rand(4);
                        my $foo = '';
                        $foo = '-useless'    if $r % 2 == 0;
                        $foo = '-that-works' if $r % 3 == 0;
                        $foo = '-readable'   if $r % 100 == 0;
                        push( @fail, "abs-add-something${foo}-to-lognag" );
                        $x_last_lognag = $now;
                    }
                    if ( $now > $x_last_bacon + 60 * 30 && $hour == 8 ) {
                        push( @fail, 'norm-eat-bacon' );
                        $x_last_bacon = $now;
                    }
                    if (   $hour > 20
                        && $hour <= 23
                        && $txt =~ /battery/i )
                    {
                        push( @fail, 'matt-writes-a-new-song' );
                    }
                    if ( $hour > 20 && $txt =~ /charge/i ) {
                        push( @fail, 'matt-wears-comedy-hat' );
                    }
                    push( @fail,
                        'matt-asks-hannah-to-rework-all-rocket-images-again' )
                      if $txt =~ /\bmodule\b/ && $min % 3 == 0;
                    if ( $hour < 3 && $txt =~ /service/ ) {
                        push( @fail, 'matt-plays-very-loud-in-piano-pants' );
                    }

                }
                if ( defined $now ) {
                    push( @fail, 'timewarp:' . timefmt($last) )
                      if $now < $last;
                    $last = $now;
                }
            }
        }

        if (   ( $logscore > 1 && $logscore < $log_timestamp_elements )
            || ( $fix && $logscore == $log_timestamp_elements ) )
        {
            push( @fail, "badlog" );
        }

        if ( $inline_timestamps || $invalid_inline_timestamps ) {

            my @timestamps = $txt =~ /$inline_timestamp_regex/g;
            foreach my $timestamp (@timestamps) {
                my $parsed_timestamp =
                  parse_inline_timestamp( $last, $timestamp );
                next if !defined $parsed_timestamp;
                my $time_link = timefmt( $parsed_timestamp, 4 );
                $line =~ s/$timestamp/[time:$time_link $timestamp]/g;
                my $offset = timefmt( $parsed_timestamp - $last );
                $offset =~ s/(\s*) /$1+/ if $parsed_timestamp >= $last;
                printf( "$file: %s (%s $offset) $line",
                    timefmt($last), $time_link );
            }
        }

        push( @fail, 'badchar' )
          if my (@badchar) =
              $line =~ /[^\-\t ._,A-Za-z0-9"'\?:\[\]<!&>;\/\n\(\)\*é°¼#]/;

        push( @fail, 'j-grows-up-so-fast' )
          if $txt =~
/[^.\?"][ ]+J(?!ack|im|oe|ohn|ames|ay|ustice|ohannesburg|ettison|ETT|ETS|r\.)[^A-Z]/;
        push( @fail, 'noleet-0-please' )
          if $txt =~ /([A-Za-z]0[A-Za-z\s]|[A-Za-z\s]0[A-Za-z])/;

        # push( @fail, '2B-or-not-2B-13' )       if $txt =~ /\b[1l]B\b/;
        push( @fail, 'CB(11)-please' )         if $txt =~ /CB\([iI]{2}\)/;
        push( @fail, 'doh-ray-me-fa-so-la' )   if $txt =~ /\blA\b/;
        push( @fail, 'doubleplus-lonely-l' )   if $txt =~ /\b[^\w']ll\b/;
        push( @fail, 'ellipsis-needs-a-diet' ) if $txt =~ /\.\.\.\./;
        push( @fail, 'geoff-minter-alert' )
          if $txt =~ /(\w*[^A-Z][a-z][A-Z]\w*)/ && $1 ne 'CapCom';
        push( @fail, 'ail-the-single-ladies' ) if $txt =~ /\bail\b/i;
        push( @fail, 'hyphen-icide' )          if $txt =~ /[a-z]-$/;
        push( @fail, 'less-ls-more-1s' )       if $txt =~ /(l\d|\dl)/;
        push( @fail, 'lonely-l' )              if $txt =~ /\bl\b/;
        push( @fail, 'multiball-punctuation' ) if $txt =~ /[,:;]{2}/;
        push( @fail, 'please-flush' )          if $txt =~ /\b(po0|p0o)\b/i;
        push( @fail, 'plunger-00-needed' )     if $txt =~ /\bPOO\b/;
        push( @fail, 'stu-tts-ers' )           if $txt =~ /tts\b/;
        push( @fail, 't-is-such-a-lonely-number' )
          if $txt =~ /[^'.]\bt\b/;
        push( @fail, 'underscore' )         if $txt =~ /_/;
        push( @fail, 'we-tlave-a-floblem' ) if $txt =~ /[^H]ouston/;
        push( @fail, 'orphaned-degree' )    if $txt =~ /\s°/;

        @fail = grep ( /^$report_fail/, @fail ) if $report_fail;
        if (@fail) {
            ++$badfiles{$file};
            print "$file: (@fail) $line";
        }
        else {
            $cleandata .= $line;
        }
        $total_fail += @fail;
    }
    close(FILE);
    if ($output_dir) {
        $file =~ m#([^/]+)$#;
        mkdir( $output_dir, 0755 );
        my $outfile = "$output_dir/$1";
        open( OUTFILE, ">$outfile" )
          || die "Unable to write $outfile: $!";
        print OUTFILE $cleandata;
        close(OUTFILE);
    }
}

sub setup_inline_timestamp_format {
    my $value = shift;
    if ( $value eq 'HH MM SS' ) {
        $inline_timestamp_format = $value;
        $inline_timestamp_regex  = '\d\d \d\d \d\d';
    }
    else {
        die "Unknown inline timestamp format: $value";
    }
}

sub setup_log_timestamp_format {
    my $value = shift;
    if    ( $value eq 'SS' )          { $log_timestamp_elements = 1 }
    elsif ( $value eq 'MM SS' )       { $log_timestamp_elements = 2 }
    elsif ( $value eq 'HH MM SS' )    { $log_timestamp_elements = 3 }
    elsif ( $value eq 'DD HH MM SS' ) { $log_timestamp_elements = 4 }
    else {
        die "Unknown log timestamp format: $value";
    }
}

sub setup_valid_speakers {
    my $value = shift;
    %valid_speaker = map { $_ => 1 } split( /\s+/, $value );
}

sub timefmt {
    my ( $secs, $timestamp_elements ) = @_;
    $timestamp_elements ||= $log_timestamp_elements;
    my $timestamp = '';
    my @timestamp_units = ( 60, 60, 24 );    # Sorted seconds, min, hour, day...
    for ( my $index = 0 ; $index < $timestamp_elements - 1 ; ++$index ) {
        $timestamp =
          sprintf( ":%02d", $secs % $timestamp_units[$index] ) . $timestamp;
        $secs /= $timestamp_units[$index];
    }
    return ( sprintf '%02d', $secs ) . $timestamp;
}
