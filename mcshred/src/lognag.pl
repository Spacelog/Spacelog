#!/usr/bin/env perl
# $Id$

# Not an entry for the obfuscated perl contest

use strict;
use warnings;
use Data::Dumper;
use Getopt::Long;

my %opt;
my $report_fail;
my $inline_timestamps;
my $invalid_inline_timestamps;
my $output_dir;
my $show_stats;
my $x_fort;
my $log_timestamp_elements = 4;
my $help;

if (
    !GetOptions(
        'report|f=s'                 => \$report_fail,
        'help|h'                     => \$help,
        'fort'                       => \$x_fort,
        'inline-timestamps|T'        => \$inline_timestamps,
        'all-inline-timestamps|I'    => \$invalid_inline_timestamps,
        'log-timestamp-elements|t=i' => \$log_timestamp_elements,
        'stats-porn|v'               => \$show_stats,
        'output-dir|o=s'             => \$output_dir,
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

lognag will sort files on the commandline by filename, excluding directory component
";
    exit;
}

my %valid_speaker = map { $_ => 1 }
  qw( AB CC CDR CMP CT F IWO LCC LMP MS P-1 P-2 R R-1 R-2 S S-1 S-2 SC Music);
my $last = -60 * 60;    # Allow for up to T minus 1 hour
my %badfiles;
my %speakers;
my $total_fail;

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
                    my ( $hour, $min, $sec ) =
                      timefmt($now) =~ m/:(\d+):(\d+):(\d+)/;
                    if ( $hour > 20 && $hour <= 23 && $txt =~ /battery/i ) {
                        push( @fail, 'matt-write-a-song' );
                    }
                    if ( $hour > 20 && $txt =~ /charge/i ) {
                        push( @fail, 'matt-wear-comedy-hat' );
                    }
                    push( @fail, 'matt-ask-hannah-to-rework-all-rocket-images' )
                      if $txt =~ /\bmodule\b/ && $min % 5 == 0;
                    if ( $hour < 3 && $txt =~ /service/ ) {
                        push( @fail, 'matt-play-very-loud' );
                    }

                }
                if ( defined $now ) {
                    push( @fail, 'timewarp:' . timefmt($last) ) if $now < $last;
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

            my @timestamps =
              $txt =~ /(?<![Mm]inus )\d+:\d\d(?::\d+)?(?:\.\d\d?)?/g;
            foreach my $timestamp (@timestamps) {
                my $parsed_timestamp =
                  parse_inline_timestamp( $last, $timestamp );
                next if !defined $parsed_timestamp;
                my $time_link = timefmt($parsed_timestamp);
                $line =~ s/$timestamp/[time:$time_link $timestamp]/g;
                my $offset = timefmt( $parsed_timestamp - $last );
                $offset =~ s/(\s*) /$1+/ if $parsed_timestamp >= $last;
                printf( "$file: %s (%s $offset) $line",
                    timefmt($last), $time_link );
            }
        }

        push( @fail, 'badchar' )
          if my (@badchar) =
              $line =~ /[^\-\t ._,A-Za-z0-9"'\?:\[\]<!&>;\/\n\(\)\*é#]/;

        push( @fail, 'j-grows-up-so-fast' )
          if $txt =~
              /[^.\?"][ ]+J(?!ack|im|oe|ohn|ames|ay|ustice|ETT|ETS|r\.)[^A-Z]/;
        push( @fail, 'noleet-0-please' )
          if $txt =~ /([A-Za-z]0[A-Za-z\s]|[A-Za-z\s]0[A-Za-z])/;
        push( @fail, '2B-or-not-2B-13' )       if $txt =~ /\b[1l]B\b/;
        push( @fail, 'CB(11)-please' )         if $txt =~ /CB\([iI]{2}\)/;
        push( @fail, 'doh-ray-me-fa-so-la' )   if $txt =~ /\blA\b/;
        push( @fail, 'doubleplus-lonely-l' )   if $txt =~ /\b[^\w']ll\b/;
        push( @fail, 'ellipsis-needs-a-diet' ) if $txt =~ /\.\.\.\./;
        push( @fail, 'geoff-minter-alert' )    if $txt =~ /[^A-Z][a-z][A-Z]/;
        push( @fail, 'ail-the-single-ladies' ) if $txt =~ /\bail\b/i;
        push( @fail, 'hyphen-icide' )          if $txt =~ /[a-z]-$/;
        push( @fail, 'less-ls-more-1s' )       if $txt =~ /(l\d|\dl)/;
        push( @fail, 'lonely-l' )              if $txt =~ /\bl\b/;
        push( @fail, 'multiball-punctuation' ) if $txt =~ /[,:;]{2}/;
        push( @fail, 'please-flush' )          if $txt =~ /\b(po0|p0o)\b/i;
        push( @fail, 'plunger-00-needed' )     if $txt =~ /\bPOO\b/;
        push( @fail, 'stu-tts-ers' )           if $txt =~ /tts\b/;
        push( @fail, 't-is-such-a-lonely-number' ) if $txt =~ /[^']\bt\b/;
        push( @fail, 'underscore' )                if $txt =~ /_/;
        push( @fail, 'we-tlave-a-floblem' )        if $txt =~ /[^H]ouston/;

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
        my $outfile = "$output_dir/$1";
        open( OUTFILE, ">$outfile" ) || die "Unable to write $outfile: $!";
        print OUTFILE $cleandata;
        close(OUTFILE);
    }
}

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

sub timefmt {
    my $secs            = shift;
    my $timestamp       = '';
    my @timestamp_units = ( 60, 60, 24 );    # Sorted seconds, min, hour, day...
    for ( my $index = 0 ; $index < $log_timestamp_elements - 1 ; ++$index ) {
        $timestamp =
          sprintf( ":%02d", $secs % $timestamp_units[$index] ) . $timestamp;
        $secs /= $timestamp_units[$index];
    }
    return ( sprintf '%02d', $secs ) . $timestamp;
}

sub filesort {

    # Ensure we process the files sorted by filename not by pathname
    my $fa = $a;
    my $fb = $b;
    $fa =~ s:.*/::;
    $fb =~ s:.*/::;
    return $fa cmp $fb;
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

sub parse_inline_timestamp {
    my ( $logtimestamp, $timestamptxt ) = @_;

    my $valid;
    my $parsed;

    if ( $timestamptxt =~ /^(\d+):(\d+):(\d+)\.\d+$/ ) {
        $valid = $1 * 60 * 60 + $2 * 60 + $3;
    }

    # Some magic numbers which are not passed literally
    $valid = 5 * 60 + 32 if $timestamptxt eq '5:32';
    $valid = 135 * 60 * 60 + 4 * 60 + 25 if $timestamptxt eq '35:04:25';

    if ( !$valid ) {
        if ( $timestamptxt =~ /^(\d+):(\d+):(\d+)$/ ) {
            $parsed = $1 * 60 * 60 + $2 * 60 + $3;
        }
        elsif ( $timestamptxt =~ /^(\d+):(\d+)(?:\.\d+)?$/ ) {
            $parsed = $1 * 60 * 60 + $2 * 60;
        }
        else {
            warn("Unable to parse timestamp '$timestamptxt'");
        }

        my $percent_change =
          100 * abs( $logtimestamp - $parsed ) / $logtimestamp;

        $valid = $parsed if $parsed > 485900 && $parsed < 514000;
        $valid = $parsed if $percent_change < 25;
    }

    return $parsed if $invalid_inline_timestamps && !$valid;
    return $valid if $inline_timestamps;
    return;
}
