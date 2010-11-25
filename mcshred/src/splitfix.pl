#!/usr/bin/env perl
# $Id$
# Take a badly OCRed txt file and split it into many many badly OCRed txt files
# With free log line timestamp mangling

use strict;
use warnings;
use Data::Dumper;

sub process {
    my ($file) = @_;
    my %summary;
    my %pages;
    my $pageno = 1;
    $pages{$pageno}{pageno} = $pageno;
    open( FILE, "<$file" ) || die("Unable to open $file: $!");
    while ( my $line = <FILE> ) {
        if ( $line =~ s/^// ) {
            ++$pageno;
            next if $line eq '';    # Final trailing
            $pages{$pageno}{pageno} = $pageno;
        }
        my @words = split( ' ', $line );
        my $logscore = 0;
        if ( @words > 4 ) {
            foreach my $i (qw(0 1 2 3)) {
                if ( $words[$i] =~ /^[a-zA-Z']{3,}[.,]?$/ ) {
                    $logscore -= 2;
                    next;
                }
                $words[$i] =~ s/[({\[][)}\]]/0/g;
                $words[$i] =~ s/[iJI!Ll\]\[]/1/g;
                $words[$i] =~ s/[oQO]/0/g;
                $words[$i] =~ s/[B]/8/g;
                $words[$i] =~ s/[h]/4/g;
                --$logscore if $words[$i] =~ /^[a-z]+$/;
                ++$logscore if $words[$i] =~ /^\d{2}$/;
            }
            ++$logscore if $words[4] =~ /^[A-Z]{2,}$/;
            $logscore = 0 if $logscore < 0;
        }
        if ( $logscore == 5 ) {
            $words[4] = sprintf( '%-3s', $words[4] );
            $line = "@words\n";
            ++$pages{$pageno}{goodlog};
        }
        elsif ($logscore) {
            ++$pages{$pageno}{badlog};
            $line =~ s/$/    # log:$logscore/;
        }
        ++$pages{$pageno}{lines};
        $pages{$pageno}{text} .= $line;
        ++$summary{$logscore};
    }
    close(FILE);
    print "$file";
    foreach my $key ( sort keys %summary ) {
        print "  $key: $summary{$key}";
    }
    print "\n";

    # Calculate pain
    my $total_pain = 0;
    foreach my $page ( values %pages ) {
        $page->{badtokens} = 0;
        my @badtokens = $page->{text} =~ m/([^\- .,A-Za-z0-9"'\?:;\/\n\(\)])/sg;
        $page->{badtokens} += @badtokens;
        @badtokens = $page->{text} =~ m/([[:punct:]]{2})/sg;
        $page->{badtokens} += @badtokens;
        $page->{pain} =
          int( sqrt( $page->{lines} ) * sqrt( $page->{badtokens} ) );
        $total_pain += $page->{pain};
    }

    my $labels = "<tr><th>Page</th>";
    foreach my $key (qw(group lines goodlog badlog badtokens pain)) {
        $labels .= "<th>$key</th>";
    }
    $labels .= "</tr>\n";

    my $pain = "<table>" . $labels;

    my $ngroups        = 20;
    my $pain_per_group = $total_pain / $ngroups;
    my $this_pain      = 0;
    my $group          = 1;

    # Write stuff
    foreach my $page ( sort { $a->{pageno} <=> $b->{pageno} } values %pages ) {

        my $dir = $file;
        $dir =~ s/(.[^.]+)$/\/$group/;
        mkdir( $dir, 0755 );

        $page->{group} = $group;
        my $outfile = sprintf( "$dir/%03d.txt", $page->{pageno} );
        $pain .= qq{<tr><td><a href="$outfile">$page->{pageno}</a></td>};
        foreach my $key (qw(group lines goodlog badlog badtokens pain)) {
            $pain .= "<td>" . ( $page->{$key} || 0 ) . "</td>";
        }
        $pain .= "</tr>\n";
        open( FILE, ">$outfile" ) || die("Unable to write '$outfile': $!");
        print FILE $page->{text};
        close(FILE);

        if ( ( $this_pain += $page->{pain} ) > $pain_per_group ) {
            $this_pain = 0;
            ++$group;
        }
    }

    $pain .= $labels . "</table>\n";

    my $base = $file;
    $base =~ s/(.[^.]+)$//;
    open( PAIN, ">$base-pages-pain.html" );
    print PAIN $pain;
    close(PAIN);
}

foreach my $file (@ARGV) { process($file); }
