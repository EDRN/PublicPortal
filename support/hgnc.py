# encoding: utf-8

import rdflib
from plone.i18n.normalizer import IDNormalizer

_hgncPredicateURI = rdflib.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#HgncName')
_biomarkerTypeURI = rdflib.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Biomarker')
_typeURI = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
_bmTitlePredicateURI = rdflib.URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Title')

def main():
    normalizer = IDNormalizer()
    g = rdflib.ConjunctiveGraph()
    g.parse(rdflib.URLInputSource('file:biomarkers.rdf'))
    statements = {}
    for s, p, o in g:
        if s not in statements:
            statements[s] = {}
        predicates = statements[s]
        if p not in predicates:
            predicates[p] = []
        predicates[p].append(o)
    for subject, predicates in statements.iteritems():
        if _typeURI not in predicates: continue
        kind = predicates[_typeURI][0]
        if kind != _biomarkerTypeURI: continue
        if _hgncPredicateURI not in predicates: continue
        hgncName = unicode(predicates[_hgncPredicateURI][0]).strip()
        if not hgncName: continue
        if _bmTitlePredicateURI not in predicates: continue
        title = unicode(predicates[_bmTitlePredicateURI][0]).strip()
        if not title: continue
        if title == u'Marks 7-gene signature for prostate cancer': continue
        objID = normalizer.normalize(title)
        print u'RewriteRule ^/biomarkers/{} /biomarkers/{} [R=301]'.format(objID, hgncName)


if __name__ == '__main__':
    main()