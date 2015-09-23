# encoding: utf-8

import rdflib, csv, cStringIO, codecs, sys

_pubURLs = [
    u'https://edrn.jpl.nasa.gov/dmcc/rdf-data/publications/@@rdf',
    # u'http://edrn.jpl.nasa.gov/bmdb/rdf/publications',
    # u'file:pubs-dmcc.rdf',
    # u'file:pubs-bmdb.rdf',
]

# Interesting predicates
_authorPredicateURI   = rdflib.URIRef(u'http://purl.org/dc/terms/author')
_issuePredicateURI    = rdflib.URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#issue')
_journalPredicateURI  = rdflib.URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#journal')
_pubMedIDPredicateURI = rdflib.URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#pmid')
_titlePredicateURI    = rdflib.URIRef(u'http://purl.org/dc/terms/title')
_volumePredicateURI   = rdflib.URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#volume')
_yearPredicateURI     = rdflib.URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#year')

# What we call a publication
_publicationTypeURI = rdflib.URIRef(u'http://edrn.nci.nih.gov/rdf/types.rdf#Publication')

# RDF Type
_typeURI = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')


class UnicodeCSVWriter(object):
    u'''Adapted from https://docs.python.org/2/library/csv.html'''
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def _getObj(predicateURI, predicates):
    u'''Get the object of the statement made with the given ``predicateURI``
    out of the dict of ``predicates``.  If there's none, then just return an
    empty unicode string.'''
    if predicateURI not in predicates: return u''
    value = unicode(predicates[predicateURI][0]).strip()
    return value


def main():
    u'''Print a table of publications that have no PubMedID'''
    writer = UnicodeCSVWriter(sys.stdout)
    writer.writerow([u'URI', u'Title', u'Journal', u'Volume', u'Issue', u'Year', u'Author...'])
    for url in _pubURLs:
        g = rdflib.ConjunctiveGraph()
        g.parse(rdflib.URLInputSource(url))
        statements = {}
        for s, p, o in g:
            if s not in statements:
                statements[s] = {}
            predicates = statements[s]
            if p not in predicates:
                predicates[p] = []
            predicates[p].append(o)
        missing = 0
        for subject, predicates in statements.iteritems():
            if _typeURI not in predicates: continue
            kind = predicates[_typeURI][0]
            if kind != _publicationTypeURI: continue
            if _pubMedIDPredicateURI in predicates: continue
            if _titlePredicateURI not in predicates: continue
            missing += 1
            title = _getObj(_titlePredicateURI, predicates)
            if not title: continue
            journal = _getObj(_journalPredicateURI, predicates)
            volume = _getObj(_volumePredicateURI, predicates)
            issue = _getObj(_issuePredicateURI, predicates)
            year = _getObj(_yearPredicateURI, predicates)
            authors = [unicode(i).strip() for i in predicates.get(_authorPredicateURI, [])]
            row = [unicode(subject), title, journal, volume, issue, year]
            row.extend(authors)
            writer.writerow(row)
        print >>sys.stderr, url, 'Missing', missing, 'Total', len(statements)

if __name__ == '__main__':
    main()
