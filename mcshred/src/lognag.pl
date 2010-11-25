#!/usr/bin/env perl
# $Id$

# Not an entry for the obfuscated perl contest

use strict;
use warnings;
use Data::Dumper;
use Getopt::Std;

my %opt;
if ( !getopts( 'ho:t:v', \%opt ) || $opt{h} || !@ARGV ) {
    print "Usage: lognag.pl [files]
      -h : This help
  -o dir : Write valid output to files in 'dir'
-t regex : Only check for failures of type 'regex'
      -v : Verbose. Make editorially biased comments regarding the files
eg:
   ./lognag.pl AS13_TEC/0_CLEAN/[0-9]*.txt

lognag will sort files on the commandline by filename, excluding directory component
";
    exit;
}

my %valid_speaker = map { $_ => 1 }
  qw( AB CC CDR CMP CT F IWO LCC LMP MS P-1 P-2 R R-1 R-2 S S-1 S-2 SC Music);
my $last = 0;
my %badfiles;
my %speakers;

sub process {
    my ($file) = @_;

    my $cleandata = '';
    open( FILE, "<$file" ) || die("Unable to open $file: $!");
    while ( my $line = <FILE> ) {
        my @fail;
        my @words    = split( ' ', $line );
        my $logscore = 0;
        my $fix      = 0;
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
                ++$logscore if $words[$i] =~ /^\d{2}$/;
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
                      join( '-', $words[0], $words[1], $words[2], $words[3] );
                    push( @fail, "timewarp:$last" ) if $now lt $last;
                    $last = $now;
                    foreach my $spkr ( split( '/', $speaker ) ) {
                        ++$speakers{$spkr}[ $words[0] ];
                    }
                }
            }
        }

        if ( ( $logscore > 1 && $logscore < 4 ) || ( $fix && $logscore == 4 ) )
        {
            push( @fail, "badlog" );
        }
        push( @fail, 'noleet0please' ) if $line =~ /(\w\s)(?![1-9]0*)0[A-Z]/;
        push( @fail, 'underscore' )    if $line =~ /_/;
        push( @fail, 'lonely-l' )      if $line =~ /\bl\b/;
        push( @fail, 'SoundOfMusicException:lA' )  if $line =~ /\blA\b/;
        push( @fail, 't-is-such-a-lonely-number' ) if $line =~ /[^']\bt\b/;
        push( @fail, 'stu-tts-ers' )               if $line =~ /tts\b/;
        push( @fail, 'pleaseflush' )               if $line =~ /\b(po0|p0o)\b/i;
        push( @fail, 'CB(11)please' )              if $line =~ /CB\([iI]{2}\)/;
        push( @fail, 'less-ls-more-1s' )           if $line =~ /(l\d|\dl)/;
        push( @fail, 'doublebonuslonely-l' )       if $line =~ /\b[^\w']ll\b/;
        push( @fail, 'multiballpunctuation' )      if $line =~ /[,:;]{2}/;
        push( @fail, 'GeoffMinterAlert' ) if $line =~ /[^A-Z][a-z][A-Z]/;
        push( @fail, '2Bornot2B13' )      if $line =~ /\b[1l]B\b/;

        push( @fail, 'badchar' )
          if my (@badchar) =
              $line =~ /[^\-\t ._,A-Za-z0-9"'\?:\[\]<!&>;\/\n\(\)\*é#]/;

        @fail = grep ( /^$opt{t}/, @fail ) if $opt{t};
        if (@fail) {
            ++$badfiles{$file};
            print "$file: (@fail) $line";
        }
        else {
            $cleandata .= $line;
        }
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
print 'Badfiles: ', join( ' ', sort keys %badfiles ), "\n" if %badfiles;

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

sub filesort {

    # Ensure we process the files sorted by filename not by pathname
    my $fa = $a;
    my $fb = $b;
    $fa =~ s:.*/::;
    $fb =~ s:.*/::;
    return $fa cmp $fb;
}

__END__;

    if (/^Tape \S+/) {
	print 'Tape ', $_;
    }
    elsif (/^.*/) {
	print 'NewP ', $_;
    }
    elsif (/^(?:[\dloPOh_iI!B\]]{2} ){4}\S+ .*/) {
	print 'LogL ', $_;
    }
    elsif (/^\S*Pag\S* \S+$/) {
	print 'Page ', $_;
    }
    elsif (/^END OF TAPE/) {
	print 'TapE ', $_;
	}
    else {
        print '**** ', $_;
    }


