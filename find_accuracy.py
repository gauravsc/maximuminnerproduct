import cPickle

results_1=cPickle.load(open("mip_results_1.dat",'r'))
results_2=cPickle.load(open("mip_results_10.15.dat",'r'))
sum=0
num_queries=0
for key,value in results_2.items():
	result_1_set=set(results_1[key].keys())
	result_2_set=set(results_2[key].keys())
	sum+=len(result_1_set.intersection(result_2_set))/float(len(result_1_set))
	num_queries+=1


print float(sum)/(num_queries)	
