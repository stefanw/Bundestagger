from django.shortcuts import render_to_response
from django.template import RequestContext
from piston.doc import generate_doc

from bundestagger.api.handlers import ParliamentHandler, ParliamentSessionHandler, TagHandler, SpeechHandler

def documentation_view(request):
    """
    Generic documentation view. Generates documentation
    from the handlers you've defined.
    """
    docs = [ ]
    handlers = [ParliamentHandler, ParliamentSessionHandler, TagHandler, SpeechHandler]
    for handler in handlers: 
        docs.append(generate_doc(handler))
#    docs = [generate_doc(ParliamentHandler)]
    import pdb; pdb.set_trace()

    def _compare(doc1, doc2): 
       #handlers and their anonymous counterparts are put next to each other.
       name1 = doc1.name.replace("Anonymous", "")
       name2 = doc2.name.replace("Anonymous", "")
       return cmp(name1, name2)    
 
    docs.sort(_compare)
       
    return render_to_response('api/documentation.html', 
        { 'docs': docs }, RequestContext(request))