import pickle
import os
import cPickle
import math
import json

f_h=open('../internship/vocab.dat','r')
_global_vocab_dict=pickle.load(f_h)
_global_mip_to_file={}


f_read=open('../internship/global_idf.dat','r')
_global_idf=cPickle.load(f_read)
f_read.close()        




def get_serialized_array(vector):
    return json.dumps(vector)

f_h_2=open('/local/singhg/mip_repr.dat','wb')
f_h=open('../internship/file_pos_hashmap.dat','r')
file_pos_hashmap=cPickle.load(f_h)
f_h.close()
files=file_pos_hashmap.keys()
f_h=open('../internship/dataset.dat','r')
i=0
for file in files:
    i+=1
    print i
    f_h.seek(file_pos_hashmap[file][0])
    data=f_h.read(file_pos_hashmap[file][1]-file_pos_hashmap[file][0])    
    data=data.split(" ")
    if(len(data)<2):
        print "continue"
        continue
    temp_array=[0]*len(_global_vocab_dict)
    no_of_terms=len(data)
    for word in data:
        temp_array[_global_vocab_dict[word]]=1
    prev_tell=f_h_2.tell()
    json_dump=get_serialized_array(temp_array)
    # print json_dump
    f_h_2.write(json_dump)
    _global_mip_to_file[file]=(prev_tell,f_h_2.tell())
    
f_h.close()  
f_h_1=open('/local/singhg/mip_to_filepos.dat','w')
cPickle.dump(_global_mip_to_file,f_h_1)
f_h_1.close()
f_h_2.close()
