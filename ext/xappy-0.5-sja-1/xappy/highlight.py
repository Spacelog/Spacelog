#!/usr/bin/env python
#
# Copyright (C) 2007 Lemur Consulting Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
r"""highlight.py: Highlight and summarise text.

"""
__docformat__ = "restructuredtext en"

import re
import xapian

class Highlighter(object):
    """Class for highlighting text and creating contextual summaries.

    >>> hl = Highlighter("en")
    >>> hl.makeSample('Hello world.', ['world'])
    'Hello world.'
    >>> hl.highlight('Hello world', ['world'], ('<', '>'))
    'Hello <world>'

    """

    # split string into words, spaces, punctuation and markup tags
    _split_re = re.compile(r'<\w+[^>]*>|</\w+>|[\w\']+|\s+|[^\w\'\s<>/]+')

    def __init__(self, language_code='en', stemmer=None):
        """Create a new highlighter for the specified language.

        """
        if stemmer is not None:
            self.stem = stemmer
        else:
            self.stem = xapian.Stem(language_code)

    def _split_text(self, text, strip_tags=False):
        """Split some text into words and non-words.

        - `text` is the text to process.  It may be a unicode object or a utf-8
          encoded simple string.
        - `strip_tags` is a flag - False to keep tags, True to strip all tags
          from the output.

        Returns a list of utf-8 encoded simple strings.

        """
        if isinstance(text, unicode):
            text = text.encode('utf-8')

        words = self._split_re.findall(text)
        if strip_tags:
            return [w for w in words if w[0] != '<']
        else:
            return words

    def _strip_prefix(self, term):
        """Strip the prefix off a term.

        Prefixes are any initial capital letters, with the exception that R always
        ends a prefix, even if followed by capital letters.

        >>> hl = Highlighter("en")
        >>> print hl._strip_prefix('hello')
        hello
        >>> print hl._strip_prefix('Rhello')
        hello
        >>> print hl._strip_prefix('XARHello')
        Hello
        >>> print hl._strip_prefix('XAhello')
        hello
        >>> print hl._strip_prefix('XAh')
        h
        >>> print hl._strip_prefix('XA')
        <BLANKLINE>

        """
        for p in xrange(len(term)):
            if term[p].islower():
                return term[p:]
            elif term[p] == 'R':
                return term[p+1:]
        return ''

    def _query_to_stemmed_words(self, query):
        """Convert a query to a list of stemmed words.

        - `query` is the query to parse: it may be xapian.Query object, or a
          sequence of terms.

        """
        if isinstance(query, xapian.Query):
            return [self._strip_prefix(t) for t in query]
        else:
            return [self.stem(q.lower()) for q in query]


    def makeSample(self, text, query, maxlen=600, hl=None, ellipsis='..', strict_length=False):
        """Make a contextual summary from the supplied text.

        This basically works by splitting the text into phrases, counting the query
        terms in each, and keeping those with the most.

        Any markup tags in the text will be stripped.

        `text` is the source text to summarise.
        `query` is either a Xapian query object or a list of (unstemmed) term strings.
        `maxlen` is the maximum length of the generated summary.
        `hl` is a pair of strings to insert around highlighted terms, e.g. ('<b>', '</b>')
        `ellipsis` is the separating ellipsis to use
        `strict_length` stops the sample from truncating the last interesting phrase found, at the cost of not using all its allotted characters

        """

        # coerce maxlen into an int, otherwise truncation doesn't happen
        maxlen = int(maxlen)

        words = self._split_text(text, True)
        terms = self._query_to_stemmed_words(query)
        
        # build blocks delimited by puncuation, and count matching words in each block
        # blocks[n] is a block [firstword, endword, charcount, termcount, selected]
        blocks = []
        start = end = count = blockchars = 0

        while end < len(words):
            blockchars += len(words[end])
            if words[end].isalnum():
                if self.stem(words[end].lower()) in terms:
                    count += 1
                end += 1
            elif words[end] in ',.;:?!\n':
                end += 1
                blocks.append([start, end, blockchars, count, False])
                start = end
                blockchars = 0
                count = 0
            else:
                end += 1
        if start != end:
            blocks.append([start, end, blockchars, count, False])
        if len(blocks) == 0:
            return ''

        # select high-scoring blocks first, down to zero-scoring
        chars = 0
        for count in xrange(3, -1, -1):
            for b in blocks:
                if b[3] >= count:
                    if not strict_length or chars == 0 or chars + b[2] < maxlen:
                        b[4] = True
                    chars += b[2]
                    if chars >= maxlen: break
            if chars >= maxlen: break

        # assemble summary
        words2 = []
        lastblock = -1
        for i, b in enumerate(blocks):
            if b[4]:
                if i != lastblock + 1:
                    words2.append(ellipsis)
                words2.extend(words[b[0]:b[1]])
                lastblock = i

        if not blocks[-1][4]:
            words2.append(ellipsis)

        # trim down to maxlen
        l = 0
        for i in xrange (len (words2)):
            if words2[i] != ellipsis:
                l += len (words2[i])
            if l >= maxlen:
                words2[i:] = [ellipsis]
                break

        if hl is None:
            return ''.join(words2)
        else:
            return self._hl(words2, terms, hl)

    def highlight(self, text, query, hl, strip_tags=False):
        """Add highlights (string prefix/postfix) to a string.

        `text` is the source to highlight.
        `query` is either a Xapian query object or a list of (unstemmed) term strings.
        `hl` is a pair of highlight strings, e.g. ('<i>', '</i>')
        `strip_tags` strips HTML markout iff True

        >>> hl = Highlighter()
        >>> qp = xapian.QueryParser()
        >>> q = qp.parse_query('cat dog')
        >>> tags = ('[[', ']]')
        >>> hl.highlight('The cat went Dogging; but was <i>dog tired</i>.', q, tags)
        'The [[cat]] went [[Dogging]]; but was <i>[[dog]] tired</i>.'

        """
        words = self._split_text(text, strip_tags)
        terms = self._query_to_stemmed_words(query)
        return self._hl(words, terms, hl)

    def _hl(self, words, terms, hl):
        """Add highlights to a list of words.
        
        `words` is the list of words and non-words to be highlighted..
        `terms` is the list of stemmed words to look for.

        """
        for i, w in enumerate(words):
            # HACK - more forgiving about stemmed terms 
            wl = w.lower()
            if wl in terms or self.stem (wl) in terms:
                words[i] = ''.join((hl[0], w, hl[1]))

        return ''.join(words)


__test__ = {
    'no_punc': r'''

    Test the highlighter's behaviour when there is no punctuation in the sample
    text (regression test - used to return no output):
    >>> hl = Highlighter("en")
    >>> hl.makeSample('Hello world', ['world'])
    'Hello world'

    ''',

    'stem_levels': r'''

    Test highlighting of words, and how it works with stemming:
    >>> hl = Highlighter("en")

    # "word" and "wording" stem to "word", so the following 4 calls all return
    # the same thing
    >>> hl.makeSample('Hello. word. wording. wordinging.', ['word'], hl='<>')
    'Hello. <word>. <wording>. wordinging.'
    >>> hl.highlight('Hello. word. wording. wordinging.', ['word'], '<>')
    'Hello. <word>. <wording>. wordinging.'
    >>> hl.makeSample('Hello. word. wording. wordinging.', ['wording'], hl='<>')
    'Hello. <word>. <wording>. wordinging.'
    >>> hl.highlight('Hello. word. wording. wordinging.', ['wording'], '<>')
    'Hello. <word>. <wording>. wordinging.'

    # "wordinging" stems to "wording", so only the last two words are
    # highlighted for this one.
    >>> hl.makeSample('Hello. word. wording. wordinging.', ['wordinging'], hl='<>')
    'Hello. word. <wording>. <wordinging>.'
    >>> hl.highlight('Hello. word. wording. wordinging.', ['wordinging'], '<>')
    'Hello. word. <wording>. <wordinging>.'
    ''',

    'supplied_stemmer': r'''

    Test behaviour if we pass in our own stemmer:
    >>> stem = xapian.Stem('en')
    >>> hl = Highlighter(stemmer=stem)
    >>> hl.highlight('Hello. word. wording. wordinging.', ['word'], '<>')
    'Hello. <word>. <wording>. wordinging.'

    ''',

    'unicode': r'''

    Test behaviour if we pass in unicode input:
    >>> hl = Highlighter('en')
    >>> hl.highlight(u'Hello\xf3. word. wording. wordinging.', ['word'], '<>')
    'Hello\xc3\xb3. <word>. <wording>. wordinging.'

    ''',

    'no_sample': r'''

    Test behaviour if we pass in unicode input:
    >>> hl = Highlighter('en')
    >>> hl.makeSample(u'', ['word'])
    ''

    ''',

    'short_samples': r'''

    >>> hl = Highlighter('en')
    >>> hl.makeSample("A boring start.  Hello world indeed.  A boring end.", ['hello'], 20, ('<', '>'))
    '..  <Hello> world ..'
    >>> hl.makeSample("A boring start.  Hello world indeed.  A boring end.", ['hello'], 40, ('<', '>'))
    'A boring start.  <Hello> world indeed...'
    >>> hl.makeSample("A boring start.  Hello world indeed.  A boring end.", ['boring'], 40, ('<', '>'))
    'A <boring> start...  A <boring> end.'

    ''',

    'apostrophes': r'''

    >>> hl = Highlighter('en')
    >>> hl.makeSample("A boring start.  Hello world's indeed.  A boring end.", ['world'], 40, ('<', '>'))
    "A boring start.  Hello <world's> indeed..."

    ''',

}

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod (sys.modules[__name__])
