import cPickle
import numpy as np
import math
results_1=cPickle.load(open("mip_results_1.dat",'r'))
results_2=cPickle.load(open("mip_results_10.1.dat",'r'))

def get_spearman_distance(orig_res, pruned_res):
    orig_sorted=[i[0] for i in (sorted(orig_res.items(), key=lambda x: x[1], reverse=True))]
    pruned_sorted=[i[0] for i in (sorted(pruned_res.items(), key=lambda x: x[1],reverse=True))]
    weights={}
    for i in range(len(orig_sorted)):
        weights[orig_sorted[i]]=len(orig_sorted)-i
    spearman_dist=0
    for i in range(len(orig_sorted)):
        doc=orig_sorted[i]
        prev_docs=orig_sorted[0:i+1]
        part_1=sum([weights[i] for i in prev_docs])
        
        if (doc in pruned_sorted):
            index_doc=pruned_sorted.index(doc)
            prev_docs=pruned_sorted[0:index_doc+1]
            part_2=sum([weights[i] for i in prev_docs if i in weights])
        else:
            part_2=sum([weights[i] for i in pruned_sorted if i in weights]) 

        spearman_dist+=weights[doc]*abs(part_1-part_2)
        return spearman_dist


k=0
spearman_dist=0
for key,value in results_2.items():
    spearman_dist+=get_spearman_distance(results_1[key],value)
    k+=1


print spearman_dist/float(k)    









