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
r"""indexerconnection.py: A connection to the search engine for indexing.

"""
__docformat__ = "restructuredtext en"

import _checkxapian
import cPickle
import xapian

from datastructures import *
import errors
from fieldactions import *
import fieldmappings
import memutils
from replaylog import log

class IndexerConnection(object):
    """A connection to the search engine for indexing.

    """

    def __init__(self, indexpath):
        """Create a new connection to the index.

        There may only be one indexer connection for a particular database open
        at a given time.  Therefore, if a connection to the database is already
        open, this will raise a xapian.DatabaseLockError.

        If the database doesn't already exist, it will be created.

        """
        self._index = log(xapian.WritableDatabase, indexpath, xapian.DB_CREATE_OR_OPEN)
        self._indexpath = indexpath

        # Read existing actions.
        self._field_actions = {}
        self._field_mappings = fieldmappings.FieldMappings()
        self._facet_hierarchy = {}
        self._facet_query_table = {}
        self._next_docid = 0
        self._config_modified = False
        self._load_config()

        # Set management of the memory used.
        # This can be removed once Xapian implements this itself.
        self._mem_buffered = 0
        self.set_max_mem_use()

    def set_max_mem_use(self, max_mem=None, max_mem_proportion=None):
        """Set the maximum memory to use.

        This call allows the amount of memory to use to buffer changes to be
        set.  This will affect the speed of indexing, but should not result in
        other changes to the indexing.

        Note: this is an approximate measure - the actual amount of memory used
        max exceed the specified amount.  Also, note that future versions of
        xapian are likely to implement this differently, so this setting may be
        entirely ignored.

        The absolute amount of memory to use (in bytes) may be set by setting
        max_mem.  Alternatively, the proportion of the available memory may be
        set by setting max_mem_proportion (this should be a value between 0 and
        1).

        Setting too low a value will result in excessive flushing, and very
        slow indexing.  Setting too high a value will result in excessive
        buffering, leading to swapping, and very slow indexing.

        A reasonable default for max_mem_proportion for a system which is
        dedicated to indexing is probably 0.5: if other tasks are also being
        performed on the system, the value should be lowered.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if max_mem is not None and max_mem_proportion is not None:
            raise errors.IndexerError("Only one of max_mem and "
                                       "max_mem_proportion may be specified")

        if max_mem is None and max_mem_proportion is None:
            self._max_mem = None

        if max_mem_proportion is not None:
            physmem = memutils.get_physical_memory()
            if physmem is not None:
                max_mem = int(physmem * max_mem_proportion)

        self._max_mem = max_mem

    def _store_config(self):
        """Store the configuration for the database.

        Currently, this stores the configuration in a file in the database
        directory, so changes to it are not protected by transactions.  When
        support is available in xapian for storing metadata associated with
        databases. this will be used instead of a file.

        """
        assert self._index is not None

        config_str = cPickle.dumps((
                                     self._field_actions,
                                     self._field_mappings.serialise(),
                                     self._facet_hierarchy,
                                     self._facet_query_table,
                                     self._next_docid,
                                    ), 2)
        log(self._index.set_metadata, '_xappy_config', config_str)

        self._config_modified = False

    def _load_config(self):
        """Load the configuration for the database.

        """
        assert self._index is not None

        config_str = log(self._index.get_metadata, '_xappy_config')
        if len(config_str) == 0:
            return

        try:
            (self._field_actions, mappings, self._facet_hierarchy, self._facet_query_table, self._next_docid) = cPickle.loads(config_str)
        except ValueError:
            # Backwards compatibility - configuration used to lack _facet_hierarchy and _facet_query_table
            (self._field_actions, mappings, self._next_docid) = cPickle.loads(config_str)
            self._facet_hierarchy = {}
            self._facet_query_table = {}
        self._field_mappings = fieldmappings.FieldMappings(mappings)

        self._config_modified = False

    def _allocate_id(self):
        """Allocate a new ID.

        """
        while True:
            idstr = "%x" % self._next_docid
            self._next_docid += 1
            if not self._index.term_exists('Q' + idstr):
                break
        self._config_modified = True
        return idstr

    def add_field_action(self, fieldname, fieldtype, **kwargs):
        """Add an action to be performed on a field.

        Note that this change to the configuration will not be preserved on
        disk until the next call to flush().

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if fieldname in self._field_actions:
            actions = self._field_actions[fieldname]
        else:
            actions = FieldActions(fieldname)
            self._field_actions[fieldname] = actions
        actions.add(self._field_mappings, fieldtype, **kwargs)
        self._config_modified = True

    def clear_field_actions(self, fieldname):
        """Clear all actions for the specified field.

        This does not report an error if there are already no actions for the
        specified field.

        Note that this change to the configuration will not be preserved on
        disk until the next call to flush().

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if fieldname in self._field_actions:
            del self._field_actions[fieldname]
            self._config_modified = True

    def get_fields_with_actions(self):
        """Get a list of field names which have actions defined.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        return self._field_actions.keys()

    def process(self, document):
        """Process an UnprocessedDocument with the settings in this database.

        The resulting ProcessedDocument is returned.

        Note that this processing will be automatically performed if an
        UnprocessedDocument is supplied to the add() or replace() methods of
        IndexerConnection.  This method is exposed to allow the processing to
        be performed separately, which may be desirable if you wish to manually
        modify the processed document before adding it to the database, or if
        you want to split processing of documents from adding documents to the
        database for performance reasons.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        result = ProcessedDocument(self._field_mappings)
        result.id = document.id
        context = ActionContext(self._index)

        for field in document.fields:
            try:
                actions = self._field_actions[field.name]
            except KeyError:
                # If no actions are defined, just ignore the field.
                continue
            actions.perform(result, field.value, context)

        return result

    def _get_bytes_used_by_doc_terms(self, xapdoc):
        """Get an estimate of the bytes used by the terms in a document.

        (This is a very rough estimate.)

        """
        count = 0
        for item in xapdoc.termlist():
            # The term may also be stored in the spelling correction table, so
            # double the amount used.
            count += len(item.term) * 2

            # Add a few more bytes for holding the wdf, and other bits and
            # pieces.
            count += 8

        # Empirical observations indicate that about 5 times as much memory as
        # the above calculation predicts is used for buffering in practice.
        return count * 5

    def add(self, document):
        """Add a new document to the search engine index.

        If the document has a id set, and the id already exists in
        the database, an exception will be raised.  Use the replace() method
        instead if you wish to overwrite documents.

        Returns the id of the newly added document (making up a new
        unique ID if no id was set).

        The supplied document may be an instance of UnprocessedDocument, or an
        instance of ProcessedDocument.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if not hasattr(document, '_doc'):
            # It's not a processed document.
            document = self.process(document)

        # Ensure that we have a id
        orig_id = document.id
        if orig_id is None:
            id = self._allocate_id()
            document.id = id
        else:
            id = orig_id
            if self._index.term_exists('Q' + id):
                raise errors.IndexerError("Document ID of document supplied to add() is not unique.")
            
        # Add the document.
        xapdoc = document.prepare()
        self._index.add_document(xapdoc)

        if self._max_mem is not None:
            self._mem_buffered += self._get_bytes_used_by_doc_terms(xapdoc)
            if self._mem_buffered > self._max_mem:
                self.flush()

        if id is not orig_id:
            document.id = orig_id
        return id

    def replace(self, document):
        """Replace a document in the search engine index.

        If the document does not have a id set, an exception will be
        raised.

        If the document has a id set, and the id does not already
        exist in the database, this method will have the same effect as add().

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if not hasattr(document, '_doc'):
            # It's not a processed document.
            document = self.process(document)

        # Ensure that we have a id
        id = document.id
        if id is None:
            raise errors.IndexerError("No document ID set for document supplied to replace().")

        xapdoc = document.prepare()
        self._index.replace_document('Q' + id, xapdoc)

        if self._max_mem is not None:
            self._mem_buffered += self._get_bytes_used_by_doc_terms(xapdoc)
            if self._mem_buffered > self._max_mem:
                self.flush()

    def _make_synonym_key(self, original, field):
        """Make a synonym key (ie, the term or group of terms to store in
        xapian).

        """
        if field is not None:
            prefix = self._field_mappings.get_prefix(field)
        else:
            prefix = ''
        original = original.lower()
        # Add the prefix to the start of each word.
        return ' '.join((prefix + word for word in original.split(' ')))

    def add_synonym(self, original, synonym, field=None,
                    original_field=None, synonym_field=None):
        """Add a synonym to the index.

         - `original` is the word or words which will be synonym expanded in
           searches (if multiple words are specified, each word should be
           separated by a single space).
         - `synonym` is a synonym for `original`.
         - `field` is the field which the synonym is specific to.  If no field
           is specified, the synonym will be used for searches which are not
           specific to any particular field.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if original_field is None:
            original_field = field
        if synonym_field is None:
            synonym_field = field
        key = self._make_synonym_key(original, original_field)
        # FIXME - this only works for exact fields which have no upper case
        # characters, or single words
        value = self._make_synonym_key(synonym, synonym_field)
        self._index.add_synonym(key, value)

    def remove_synonym(self, original, synonym, field=None):
        """Remove a synonym from the index.

         - `original` is the word or words which will be synonym expanded in
           searches (if multiple words are specified, each word should be
           separated by a single space).
         - `synonym` is a synonym for `original`.
         - `field` is the field which this synonym is specific to.  If no field
           is specified, the synonym will be used for searches which are not
           specific to any particular field.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        key = self._make_synonym_key(original, field)
        self._index.remove_synonym(key, synonym.lower())

    def clear_synonyms(self, original, field=None):
        """Remove all synonyms for a word (or phrase).

         - `field` is the field which this synonym is specific to.  If no field
           is specified, the synonym will be used for searches which are not
           specific to any particular field.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        key = self._make_synonym_key(original, field)
        self._index.clear_synonyms(key)

    def _assert_facet(self, facet):
        """Raise an error if facet is not a declared facet field.

        """
        for action in self._field_actions[facet]._actions:
            if action == FieldActions.FACET:
                return
        raise errors.IndexerError("Field %r is not indexed as a facet" % facet)

    def add_subfacet(self, subfacet, facet):
        """Add a subfacet-facet relationship to the facet hierarchy.
        
        Any existing relationship for that subfacet is replaced.

        Raises a KeyError if either facet or subfacet is not a field,
        and an IndexerError if either facet or subfacet is not a facet field.
        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        self._assert_facet(facet)
        self._assert_facet(subfacet)
        self._facet_hierarchy[subfacet] = facet
        self._config_modified = True

    def remove_subfacet(self, subfacet):
        """Remove any existing facet hierarchy relationship for a subfacet.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if subfacet in self._facet_hierarchy:
            del self._facet_hierarchy[subfacet]
            self._config_modified = True

    def get_subfacets(self, facet):
        """Get a list of subfacets of a facet.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        return [k for k, v in self._facet_hierarchy.iteritems() if v == facet] 

    FacetQueryType_Preferred = 1;
    FacetQueryType_Never = 2;
    def set_facet_for_query_type(self, query_type, facet, association):
        """Set the association between a query type and a facet.

        The value of `association` must be one of
        IndexerConnection.FacetQueryType_Preferred,
        IndexerConnection.FacetQueryType_Never or None. A value of None removes
        any previously set association.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if query_type is None:
            raise errors.IndexerError("Cannot set query type information for None")
        self._assert_facet(facet)
        if query_type not in self._facet_query_table:
            self._facet_query_table[query_type] = {}
        if association is None:
            if facet in self._facet_query_table[query_type]:
                del self._facet_query_table[query_type][facet]
        else:
            self._facet_query_table[query_type][facet] = association;
        if self._facet_query_table[query_type] == {}:
            del self._facet_query_table[query_type]
        self._config_modified = True

    def get_facets_for_query_type(self, query_type, association):
        """Get the set of facets associated with a query type.

        Only those facets associated with the query type in the specified
        manner are returned; `association` must be one of
        IndexerConnection.FacetQueryType_Preferred or
        IndexerConnection.FacetQueryType_Never.

        If the query type has no facets associated with it, None is returned.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if query_type not in self._facet_query_table:
            return None
        facet_dict = self._facet_query_table[query_type]
        return set([facet for facet, assoc in facet_dict.iteritems() if assoc == association])

    def set_metadata(self, key, value):
        """Set an item of metadata stored in the connection.

        The value supplied will be returned by subsequent calls to
        get_metadata() which use the same key.

        Keys with a leading underscore are reserved for internal use - you
        should not use such keys unless you really know what you are doing.

        This will store the value supplied in the database.  It will not be
        visible to readers (ie, search connections) until after the next flush.

        The key is limited to about 200 characters (the same length as a term
        is limited to).  The value can be several megabytes in size.

        To remove an item of metadata, simply call this with a `value`
        parameter containing an empty string.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if not hasattr(self._index, 'set_metadata'):
            raise errors.IndexerError("Version of xapian in use does not support metadata")
        log(self._index.set_metadata, key, value)

    def get_metadata(self, key):
        """Get an item of metadata stored in the connection.

        This returns a value stored by a previous call to set_metadata.

        If the value is not found, this will return the empty string.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if not hasattr(self._index, 'get_metadata'):
            raise errors.IndexerError("Version of xapian in use does not support metadata")
        return log(self._index.get_metadata, key)

    def delete(self, id):
        """Delete a document from the search engine index.

        If the id does not already exist in the database, this method
        will have no effect (and will not report an error).

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        self._index.delete_document('Q' + id)

    def flush(self):
        """Apply recent changes to the database.

        If an exception occurs, any changes since the last call to flush() may
        be lost.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if self._config_modified:
            self._store_config()
        self._index.flush()
        self._mem_buffered = 0

    def close(self):
        """Close the connection to the database.

        It is important to call this method before allowing the class to be
        garbage collected, because it will ensure that any un-flushed changes
        will be flushed.  It also ensures that the connection is cleaned up
        promptly.

        No other methods may be called on the connection after this has been
        called.  (It is permissible to call close() multiple times, but
        only the first call will have any effect.)

        If an exception occurs, the database will be closed, but changes since
        the last call to flush may be lost.

        """
        if self._index is None:
            return
        try:
            self.flush()
        finally:
            # There is currently no "close()" method for xapian databases, so
            # we have to rely on the garbage collector.  Since we never copy
            # the _index property out of this class, there should be no cycles,
            # so the standard python implementation should garbage collect
            # _index straight away.  A close() method is planned to be added to
            # xapian at some point - when it is, we should call it here to make
            # the code more robust.
            self._index = None
            self._indexpath = None
            self._field_actions = None
            self._config_modified = False

    def get_doccount(self):
        """Count the number of documents in the database.

        This count will include documents which have been added or removed but
        not yet flushed().

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        return self._index.get_doccount()

    def iterids(self):
        """Get an iterator which returns all the ids in the database.

        The unqiue_ids are currently returned in binary lexicographical sort
        order, but this should not be relied on.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        return PrefixedTermIter('Q', self._index.allterms())

    def get_document(self, id):
        """Get the document with the specified unique ID.

        Raises a KeyError if there is no such document.  Otherwise, it returns
        a ProcessedDocument.

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        postlist = self._index.postlist('Q' + id)
        try:
            plitem = postlist.next()
        except StopIteration:
            # Unique ID not found
            raise KeyError('Unique ID %r not found' % id)
        try:
            postlist.next()
            raise errors.IndexerError("Multiple documents " #pragma: no cover
                                       "found with same unique ID")
        except StopIteration:
            # Only one instance of the unique ID found, as it should be.
            pass

        result = ProcessedDocument(self._field_mappings)
        result.id = id
        result._doc = self._index.get_document(plitem.docid)
        return result

    def iter_synonyms(self, prefix=""):
        """Get an iterator over the synonyms.

         - `prefix`: if specified, only synonym keys with this prefix will be
           returned.

        The iterator returns 2-tuples, in which the first item is the key (ie,
        a 2-tuple holding the term or terms which will be synonym expanded,
        followed by the fieldname specified (or None if no fieldname)), and the
        second item is a tuple of strings holding the synonyms for the first
        item.

        These return values are suitable for the dict() builtin, so you can
        write things like:

         >>> conn = IndexerConnection('foo')
         >>> conn.add_synonym('foo', 'bar')
         >>> conn.add_synonym('foo bar', 'baz')
         >>> conn.add_synonym('foo bar', 'foo baz')
         >>> dict(conn.iter_synonyms())
         {('foo', None): ('bar',), ('foo bar', None): ('baz', 'foo baz')}

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        return SynonymIter(self._index, self._field_mappings, prefix)

    def iter_subfacets(self):
        """Get an iterator over the facet hierarchy.

        The iterator returns 2-tuples, in which the first item is the
        subfacet and the second item is its parent facet.

        The return values are suitable for the dict() builtin, for example:

         >>> conn = IndexerConnection('db')
         >>> conn.add_field_action('foo', FieldActions.FACET)
         >>> conn.add_field_action('bar', FieldActions.FACET)
         >>> conn.add_field_action('baz', FieldActions.FACET)
         >>> conn.add_subfacet('foo', 'bar')
         >>> conn.add_subfacet('baz', 'bar')
         >>> dict(conn.iter_subfacets())
         {'foo': 'bar', 'baz': 'bar'}

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if 'facets' in _checkxapian.missing_features:
            raise errors.IndexerError("Facets unsupported with this release of xapian")
        return self._facet_hierarchy.iteritems()

    def iter_facet_query_types(self, association):
        """Get an iterator over query types and their associated facets.

        Only facets associated with the query types in the specified manner
        are returned; `association` must be one of IndexerConnection.FacetQueryType_Preferred
        or IndexerConnection.FacetQueryType_Never.

        The iterator returns 2-tuples, in which the first item is the query
        type and the second item is the associated set of facets.

        The return values are suitable for the dict() builtin, for example:

         >>> conn = IndexerConnection('db')
         >>> conn.add_field_action('foo', FieldActions.FACET)
         >>> conn.add_field_action('bar', FieldActions.FACET)
         >>> conn.add_field_action('baz', FieldActions.FACET)
         >>> conn.set_facet_for_query_type('type1', 'foo', conn.FacetQueryType_Preferred)
         >>> conn.set_facet_for_query_type('type1', 'bar', conn.FacetQueryType_Never)
         >>> conn.set_facet_for_query_type('type1', 'baz', conn.FacetQueryType_Never)
         >>> conn.set_facet_for_query_type('type2', 'bar', conn.FacetQueryType_Preferred)
         >>> dict(conn.iter_facet_query_types(conn.FacetQueryType_Preferred))
         {'type1': set(['foo']), 'type2': set(['bar'])}
         >>> dict(conn.iter_facet_query_types(conn.FacetQueryType_Never))
         {'type1': set(['bar', 'baz'])}

        """
        if self._index is None:
            raise errors.IndexerError("IndexerConnection has been closed")
        if 'facets' in _checkxapian.missing_features:
            raise errors.IndexerError("Facets unsupported with this release of xapian")
        return FacetQueryTypeIter(self._facet_query_table, association)

class PrefixedTermIter(object):
    """Iterate through all the terms with a given prefix.

    """
    def __init__(self, prefix, termiter):
        """Initialise the prefixed term iterator.

        - `prefix` is the prefix to return terms for.
        - `termiter` is a xapian TermIterator, which should be at its start.

        """

        # The algorithm used in next() currently only works for single
        # character prefixes, so assert that the prefix is single character.
        # To deal with multicharacter prefixes, we need to check for terms
        # which have a starting prefix equal to that given, but then have a
        # following uppercase alphabetic character, indicating that the actual
        # prefix is longer than the target prefix.  We then need to skip over
        # these.  Not too hard to implement, but we don't need it yet.
        assert(len(prefix) == 1)

        self._started = False
        self._prefix = prefix
        self._prefixlen = len(prefix)
        self._termiter = termiter

    def __iter__(self):
        return self

    def next(self):
        """Get the next term with the specified prefix.

        """
        if not self._started:
            term = self._termiter.skip_to(self._prefix).term
            self._started = True
        else:
            term = self._termiter.next().term
        if len(term) < self._prefixlen or term[:self._prefixlen] != self._prefix:
            raise StopIteration
        return term[self._prefixlen:]


class SynonymIter(object):
    """Iterate through a list of synonyms.

    """
    def __init__(self, index, field_mappings, prefix):
        """Initialise the synonym iterator.

         - `index` is the index to get the synonyms from.
         - `field_mappings` is the FieldMappings object for the iterator.
         - `prefix` is the prefix to restrict the returned synonyms to.

        """
        self._index = index
        self._field_mappings = field_mappings
        self._syniter = self._index.synonym_keys(prefix)

    def __iter__(self):
        return self

    def next(self):
        """Get the next synonym.

        """
        synkey = self._syniter.next()
        pos = 0
        for char in synkey:
            if char.isupper(): pos += 1
            else: break
        if pos == 0:
            fieldname = None
            terms = synkey
        else:
            prefix = synkey[:pos]
            fieldname = self._field_mappings.get_fieldname_from_prefix(prefix)
            terms = ' '.join((term[pos:] for term in synkey.split(' ')))
        synval = tuple(self._index.synonyms(synkey))
        return ((terms, fieldname), synval)

class FacetQueryTypeIter(object):
    """Iterate through all the query types and their associated facets.

    """
    def __init__(self, facet_query_table, association):
        """Initialise the query type facet iterator.

        Only facets associated with each query type in the specified
        manner are returned (`association` must be one of
        IndexerConnection.FacetQueryType_Preferred or
        IndexerConnection.FacetQueryType_Never).

        """
        self._table_iter = facet_query_table.iteritems()
        self._association = association

    def __iter__(self):
        return self

    def next(self):
        """Get the next (query type, facet set) 2-tuple.

        """
        query_type, facet_dict = self._table_iter.next()
        facet_list = [facet for facet, association in facet_dict.iteritems() if association == self._association]
        if len(facet_list) == 0:
            return self.next()
        return (query_type, set(facet_list))

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod (sys.modules[__name__])
