#!/usr/bin/env perl
# $Id$

use strict;
use warnings;

use IO::File;
use Data::Dumper;
use JSON;
use Getopt::Long;

my $help;
my @lines;
my $glossary;
my $shared_path = '.';

if (   !GetOptions( 'help|h' => \$help, 'shared_glossaries|s=s' => \$shared_path )
    || $help
    || !@ARGV )
{
    print "Usage: markup.pl [dir/file]
                      --help : This help
eg:
   tools/markup.pl missions/ma6/transcripts/TEC

markup will attenmpt to automatically markup glossary references
in a processed TEC transcript. If given a file it will read from
the file and look for a _meta in the same directory. If given a
directory it will look for a TEC and _meta files in that directory.

";
    exit;
}

foreach my $dir (@ARGV) {
    process($dir);
}
exit;

sub load_json {
    my ($file) = @_;
    my $fh = new IO::File;
    $fh->open( '<' . $file ) || die "Unable to load $file: $!";

    my $json_text;
    $fh->read( $json_text, -s $fh );
    $fh->close;

    my $json = JSON->new->allow_nonref;
    my $meta = $json->decode($json_text);
    return $meta;
}

sub load_meta {
    my ($file) = @_;
    my $meta = load_json($file);
    $glossary = $meta->{glossary};
    load_shared_glossaries(@{$meta->{shared_glossaries}}) if $meta->{shared_glossaries};
}

sub load_shared_glossaries {
    my (@glossary_names) = @_;
    foreach my $glossary_addition (@glossary_names) {
        my $json = load_json("$shared_path/$glossary_addition");
        foreach my $term (keys %$json) {
            $glossary->{$term} ||= $json->{$term};
        }
    }
}

sub load_transcript {
    my ($file) = @_;
    my $fh = new IO::File;
    $fh->open( '<' . $file ) || die "Unable to load $file: $!";
    my $entry;
    while ( my $line = <$fh> ) {
        if ( $line =~ /^\[(-?\d\d:\d\d:\d\d:\d\d)\]/ ) {
            if ( $entry->{timestamp} ) {
                push( @lines, $entry );
                $entry = undef;
            }
            $entry->{timestamp} = $1;
        }
        elsif ( $line =~ /(^_\w+)\s*:\s*(.*)/ ) {
            $entry->{$1} = $2;
        }
        elsif ( $line =~ /^([A-Z-?\d*]+): (.*)/ ) {

            # Expand multiple speaker:text entries to separate logs lines
            if ( $entry->{speaker} ) {
                my %copy = %{$entry};
                push( @lines, $entry );
                $entry = \%copy;
            }
            $entry->{speaker} = $1;
            $entry->{text}    = $2;
        }
        elsif ( $line =~ /^(\s+\S.*)/ ) {
            $entry->{text} .= "\n$1";
        }
        elsif ( $line =~ /./ ) {
            chomp $line;
            warn "Unable to parse: '$line'";
        }
    }
    push( @lines, $entry );
    $fh->close;
}

# May miss items which are followed by ']'
sub markup {
    my ( $link, @tags ) = @_;
    my $regex = '\b'
      . "(?<!\\[$link:)("
      . join( '|', map { s{(.)}{$1(?:<[^>]+>)?}g; "($_)" } @tags )
      . ')(?![<\]])(?=[. ,]|$)';
    map { $_->{text} =~ s/$regex/"[$link:".clean($1)."]"/eg; $_ } @lines;
}

# Cleanup links by removing <tags>
sub clean { my $key = shift; $key =~ s/<[^>]+>//g; $key; }

sub process {
    my ($path) = @_;

    @lines    = ();
    $glossary = undef;
    my $meta_file;
    my $transcript_file;
    if ( -d $path ) {
        $transcript_file = "$path/TEC";
        $meta_file       = "$path/_meta";
    }
    else {
        $transcript_file = $path;
        $meta_file       = $path;
        $meta_file =~ s:[^/]*$:_meta:;
    }
    load_transcript($transcript_file);
    load_meta($meta_file);
    markup( 'glossary', keys %{$glossary} ) if keys %{$glossary};
    save_transcript("$transcript_file-markedup");
}

sub save_transcript {
    my ($file) = @_;
    my $fh = new IO::File;
    $fh->open( '>' . $file ) || die "Unable to save $file: $!";
    print "Saving $file\n";
    my $timestamp = '';
    foreach my $line (@lines) {
        if ( $line->{timestamp} ne $timestamp )  # Collapse duplicate timestamps
        {
            print $fh "[$line->{timestamp}]\n";
            foreach my $key ( sort grep( /^_/, keys %{$line} ) ) {
                print $fh "$key : $line->{$key}\n";
            }
        }
        print $fh "$line->{speaker}: $line->{text}\n\n";
        $timestamp = $line->{timestamp};

    }
    $fh->close;
}
