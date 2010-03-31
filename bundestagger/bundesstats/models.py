from django.db import models
from django.db.models import Q
import pickle
import marshal, types

import pprint
pp = pprint.PrettyPrinter(indent=4)
from bundestagger.bundestag.models import Politician, Party, Event

class Feature(models.Model):
    category = models.CharField(blank=True, max_length=100)
    description = models.CharField(blank=True, max_length=100)
    calculation = models.TextField(blank=True)
    display_rest = models.BooleanField(default=True)
    url_parameters = models.CharField(blank=True, max_length=255) 
    
    def __unicode__(self):
        return self.description
        
    def recalculate(self, top=None):
        self.featurerank_set.all().delete()
        calc = pickle.loads(self.calculations)
        top = top or calc["top"]
        code = marshal.loads(calc["key_function"])
        func = types.FunctionType(code, globals(), "key_function")
        queryset = Q()
        queryset.query = calc["query"]        
        self.calculate_feature(None, queryset, top=top, key_function=func)
    
    def calculate_feature(self, queryset, top=10, key_function=None):
        results = queryset.all()
        func_string = marshal.dumps(key_function.func_code)
        self.calculation = pickle.dumps({"query": results.query, "top":top, "key_function":func_string})
        aggregated = {}
        count = len(results)
        i= 0
        for result in results:
            if i % 1000 == 0:
                print "%d/%d" % (i, count)
#                if i>2000: break
            i+=1
            key = key_function(result)
            aggregated.setdefault(key,0)
            aggregated[key]+=1
        sorted_aggregation =  sorted(aggregated, key=lambda x: aggregated[x], reverse=True)
        firsttop = [(key,aggregated[key]) for key in sorted_aggregation[:top]]
        sorted_aggregation = sorted_aggregation[top:]
        sorted_aggregation = sum(map(lambda x: aggregated[x], sorted_aggregation))
        pp.pprint(firsttop)
        print "Rest: %d" % sorted_aggregation
        if not self.id:
            self.save()
        rank=0
        for key,val in firsttop:
            rank+=1
            if "party" in key.__class__.__name__.lower():
                FeatureRank.objects.create(feature=self, rank=rank, value=val, party=key)
            else:
                FeatureRank.objects.create(feature=self, rank=rank, value=val, politician=key)
        FeatureRank.objects.create(feature=self, value=sorted_aggregation, label="Rest")
        
        
    
class FeatureRank(models.Model):
    feature = models.ForeignKey(Feature)
    rank = models.IntegerField(blank=True, null=True)
    value = models.IntegerField()
    politician = models.ForeignKey(Politician, null=True, blank=True)
    party = models.ForeignKey(Party, null=True, blank=True)
    label = models.CharField(null=True,blank=True, max_length=100)
    
    def __unicode__(self):
        if self.label is not None:
            return self.label
        if self.party is not None:
            return unicode(self.party)
        if self.politician is not None:
            return unicode(self.politician)
        return "Feature of %s: %d" % (self.feature, self.value)