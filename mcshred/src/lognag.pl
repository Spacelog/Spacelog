#!/usr/bin/env perl
# $Id$

# Not an entry for the obfuscated perl contest

use strict;
use warnings;
use Data::Dumper;
use Getopt::Std;

my %opt;
if ( !getopts( 'ho:t:vIT', \%opt ) || $opt{h} || !@ARGV ) {
    print "Usage: lognag.pl [files]
      -h : This help
      -T : Search and report on inline timestamps
      -I : Search and report on invalid inline timestamps
  -o dir : Write valid output to files in 'dir'
-t regex : Only check for failures of type 'regex'
      -v : Verbose. Make editorially biased comments regarding the speakers
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
        my @words    = split( ' ', $line );
        my $logscore = 0;
        my $fix      = 0;
        my $txt      = $line;

        if ( @words > 4 ) {
            foreach my $i (qw(0 1 2 3)) {
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
            my $speaker = $words[4];
            $speaker = 'Music' if $speaker =~ /^\(Music/;
            if ( $logscore > 3 ) {
                my @speakers =
                  grep( !$valid_speaker{$_}, split( '/', $speaker ) );
                push( @fail, 'imposter:' . join( ',', @speakers ) )
                  if @speakers;
            }
            if ( $logscore == 4 ) {
                push( @fail, 'badday' )  if $words[0] > 5;
                push( @fail, 'badhour' ) if $words[1] > 24;
                push( @fail, 'badmin' )  if $words[2] > 60;
                push( @fail, 'badsec' )  if $words[3] > 60;
                if ( !@fail ) {
                    my $now =
                      $words[0] * 24 * 60 * 60 +
                      $words[1] * 60 * 60 +
                      $words[2] * 60 +
                      $words[3];
                    push( @fail, "timewarp:$last" ) if $now <= $last;
                    $last = $now;
                    foreach my $spkr ( split( '/', $speaker ) ) {
                        ++$speakers{$spkr}[ $words[0] ];
                    }
                }
                $txt =~ s/(\S+\s*){5}//;
            }
        }

        if ( ( $logscore > 1 && $logscore < 4 ) || ( $fix && $logscore == 4 ) )
        {
            push( @fail, "badlog" );
        }

        if ( $opt{T} || $opt{I} ) {

            my @timestamps =
              $txt =~ /(?<![Mm]inus )\d+:\d\d(?::\d+)?(?:\.\d\d?)?/g;
            foreach my $timestamp (@timestamps) {
                my $parsed_timestamp = parse_timestamp( $last, $timestamp );
                next if !defined $parsed_timestamp;
                my $offset = timefmt( $parsed_timestamp - $last );
                $offset =~ s/(\s*) /$1+/ if $parsed_timestamp >= $last;
                printf( "$file: %s (%s $offset) $line",
                    timefmt($last), timefmt($parsed_timestamp) );
            }
        }

        push( @fail, 'badchar' )
          if my (@badchar) =
              $line =~ /[^\-\t ._,A-Za-z0-9"'\?:\[\]<!&>;\/\n\(\)\*é#]/;

        push( @fail, 'j-grows-up-so-fast' )
          if $txt =~ /[^.][ ]J(?!ack|im|oe|ohn|ames|ETT|ETS|r\.)/;
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

        @fail = grep ( /^$opt{t}/, @fail ) if $opt{t};
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
    if ( $opt{o} ) {
        $file =~ m#([^/]+)$#;
        my $outfile = "$opt{o}/$1";
        open( OUTFILE, ">$outfile" ) || die "Unable to write $outfile: $!";
        print OUTFILE $cleandata;
        close(OUTFILE);
    }
}

foreach my $file ( sort filesort @ARGV ) { process($file); }
print 'Bad files: ', join( ' ', sort keys %badfiles ), "\n" if %badfiles;
print 'Fail: ', $total_fail, "\n" if $total_fail;

if ( $opt{v} ) {
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
    my $secs = shift;
    return sprintf "    %02d:%02d", ( $secs / 60 ) % 60, $secs % 60
      if $secs < 60 * 60;
    return sprintf "%3d:%02d:%02d", $secs / ( 60 * 60 ), ( $secs / 60 ) % 60,
      $secs % 60;
}

sub filesort {

    # Ensure we process the files sorted by filename not by pathname
    my $fa = $a;
    my $fb = $b;
    $fa =~ s:.*/::;
    $fb =~ s:.*/::;
    return $fa cmp $fb;
}

sub parse_timestamp {
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

    return $parsed if $opt{I} && !$valid;
    return $valid if $opt{T};
    return;
}
