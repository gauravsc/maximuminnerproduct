import numpy
import cPickle
import json
import random
import time
import math

_perc=0.15
f_h=open('../internship/vocab.dat','r')
_global_vocab_dict=cPickle.load(f_h)
_global_mip_to_file={}

vocab_len=len(_global_vocab_dict)

f_h=open('/local/singhg/dict_mip_to_filepos.dat','r')
mip_to_filepos=cPickle.load(f_h)
f_h.close()
files=mip_to_filepos.keys()
f_h=open('/local/singhg/dict_mip_repr.dat','r')
t1=0
t2=0
class Node(object):
    def __init__(self):
        self.R=0
        self.C=None
        self.elements=None
        
    def get_vector_from_file(self,file):
        
        f_h.seek(mip_to_filepos[file][0])
        data_dict=json.loads(f_h.read(mip_to_filepos[file][1]-mip_to_filepos[file][0]))
        data=[0]*vocab_len
        for key,value in data_dict.items():
            data[int(key)]=value  
                           
        data=numpy.asarray(data)       
       
       
        return (1.0/numpy.linalg.norm(data))*data
    
    def get_dict_from_file(self,file):
        global t2
        start=time.clock()
        f_h.seek(mip_to_filepos[file][0])
        data_dict=json.loads(f_h.read(mip_to_filepos[file][1]-mip_to_filepos[file][0]))
        norm=self.norm_dict(data_dict)
        for key, value in data_dict.items():
            data_dict[key]/=norm
        t2+=time.clock()-start
        return data_dict       

    def add_dict(self,dic1,dic2):
        keys1=set(dic1.keys())
        keys2=set(dic2.keys())
        new_dic={}
        k12=keys1-keys2
        k21=keys2-keys1
        for i in keys1.intersection(keys2): 
            new_dic[i]=dic1[i]+dic2[i]
        for i in k12:
            new_dic[i]=dic1[i]
        for i in k21:
            new_dic[i]=dic2[i]        
        return new_dic     
    def sub_dict(self,dic1,dic2):
        keys1=set(dic1.keys())
        keys2=set(dic2.keys())
        new_dic={}
        k12=keys1-keys2
        k21=keys2-keys1
        for i in keys1.intersection(keys2): 
            new_dic[i]=dic1[i]-dic2[i]
        for i in k12:
            new_dic[i]=dic1[i]
        for i in k21:
            new_dic[i]=-1*dic2[i]        
        return new_dic    
        
    def norm_dict(self,dic):
        norm=math.sqrt(sum([math.pow(i,2) for i in dic.values()]))  
        return norm  
    def dot(self,dic1,dic2):
        keys1=set(dic1.keys())
        keys2=set(dic2.keys())
        inter=keys1.intersection(keys2)
        sum=0
        for i in inter:
            sum+=dic1[i]*dic2[i]
            
        return sum
                
    def calculate_center(self):
        sum_vec=None
        temp_elem=random.sample(self.elements,min(40,len(self.elements)))
        for element in temp_elem:
            dic=self.get_dict_from_file(element)
            if sum_vec ==None:
                sum_vec=dict(dic)
            else:
                sum_vec=self.add_dict(dic,sum_vec)
        for key,value in sum_vec.items():
            sum_vec[key]/= len(temp_elem)
                   
        self.C=dict(sum_vec) 
            
            
    def calculate_radius(self):
        temp_elements=random.sample(self.elements,min(40,len(self.elements)))
        for element in temp_elements:
            dic=self.get_dict_from_file(element)
            max_distance=self.norm_dict(self.sub_dict(dic,self.C))
            if(max_distance>self.R):
                self.R=max_distance
    
    def choose_centers(self):
       
        rand_elem=random.choice(self.elements)
        rand_vector=self.get_dict_from_file(rand_elem)
        max_left_dist=0
        temp_elements=random.sample(self.elements,min(40,len(self.elements)))
        for element in temp_elements:
            dic=self.get_dict_from_file(element)
            dist=self.norm_dict(self.sub_dict(dic,rand_vector))         
            if (dist>=max_left_dist):
                A=dict(dic)
                max_left_dist=dist
            
        rand_vector=dict(A)
        max_right_dist=0        
        for element in temp_elements:
            dic=self.get_dict_from_file(element)
            dist=self.norm_dict(self.sub_dict(dic,rand_vector))
            if (dist>=max_right_dist):
                B=dic
                max_right_dist=dist
         
        return (A,B)
        
    def get_distance_between_vectors(self,vector1,vector2):
        return self.norm_dict(self.sub_dict(vector1,vector2))
          
   
                   
    def  trickle(self,elements):
        self.elements=elements
        
        if (len(self.elements)<100):
            return
        #print "calculate centre"
        self.calculate_center()
        #print "calculate radius"
        self.calculate_radius()

        lc,rc=self.choose_centers()
        left=[] 
        right=[]
        start=time.clock()
        global t1
        i=0
        for element in self.elements:
            #print i
            i+=1
            dic=self.get_dict_from_file(element)
            #print dic
            ld=self.get_distance_between_vectors(dic,lc)
            rd=self.get_distance_between_vectors(dic,rc)         
            if (ld<rd):
                left.append(element)
            else:
                right.append(element)
                
                
        t1+=time.clock()-start
        print len(left), len(right)   
        #print t1,t2     
        self.elements=[]
        self.left=Node()
        self.right=Node()
        self.left.trickle(left)
        self.right.trickle(right)

topk={}

def update_topk(ptr,query):
    global topk
    global  _global_dist_count
    qvector=ptr.get_dict_from_file(query)    
    for element in ptr.elements:        
        dvector=ptr.get_dict_from_file(element)
        sim=ptr.dot(dvector,qvector)
        _global_dist_count+=1
        if (len(topk)<51):
            topk[element]=sim
        else:
             min_key=min(topk.iterkeys(), key=(lambda key: topk[key]))
             if(topk[min_key]<sim):
                 del topk[min_key]
                 topk[element]=sim                
                      
def get_bound_for_query(query,ptr):
    if(ptr.C==None):
        return 1.0
    dic=ptr.get_dict_from_file(query)
    return ptr.dot(ptr.C,dic)+ptr.R*_perc*ptr.norm_dict(dic)

def to_be_pruned(topk,bound):
    if(len(topk)<51):
        return False
    min_key=min(topk.iterkeys(), key=(lambda key: topk[key]))
    if(topk[min_key]>bound):
        return True
    else:
        return False    
        
        
def traversal_query(ptr,query):
    if(len(ptr.elements)>0):            
        update_topk(ptr,query)
        return     
    
    bound=get_bound_for_query(query,ptr)
    if(to_be_pruned(topk,bound)):
        return
        
    lbound=get_bound_for_query(query,ptr.left)
    rbound=get_bound_for_query(query,ptr.right)  
      
    if (lbound>rbound):       
        traversal_query(ptr.left,query)
        traversal_query(ptr.right,query)
    else:
        traversal_query(ptr.right,query)
        traversal_query(ptr.left,query)
            

# files=files[0:10000]               
root=Node()
root.trickle(files)
_global_topk={}
_global_dist_count=0
f_read=open('query_and_ls_results_1.dat','r')
queries=cPickle.load(f_read).keys()

queries=queries[0:100]
f_read.close()
k=0
print "queries"
for query in queries:
    print k
    k+=1
    topk={}
    traversal_query(root,query)
    print topk
    _global_topk[query]=dict(topk)


f_write=open('mip_results_1'+str(_perc)+'.dat','w')
cPickle.dump(_global_topk,f_write)
f_write.close()
print _global_dist_count            
        
                   
                
        
