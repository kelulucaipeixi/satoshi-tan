import time
import numpy as np 

class makeExplanation():
	def __init__(self):
		self.USER_ITEM_DATA='./datasets/demo/user_item.txt'
		self.ITEM_FEATURE_DATA='./datasets/demo/item_feature.txt'
	def get_u_it_dict(self):
		u_i_dict={}
		u_it=open(self.USER_ITEM_DATA,'r')
		count=0
		for lines in u_it:
			if count==0: 
				count=1
				continue
			u_id=int(lines.split(',')[0])
			it_id=lines.split(',')[1].split(' ')[4:-1]
			its=[]
			for it in it_id:
				its+=[int(it)]
			if u_id not in u_i_dict:
				u_i_dict[u_id]={}
			else:
				for it in its:
					if it not in u_i_dict[u_id]:
						u_i_dict[u_id][it]=1
					else:
						u_i_dict[u_id][it]+=1
		return u_i_dict
	# sorted_u_i={}
	# for u_id in u_i_dict:
	# 	sorted_u_i[u_id]=sorted(u_i_dict[u_id].items(),key=lambda x:x[1])
	# print(sorted_u_i)

	def get_u_f_dict(self,u_it_dict,it_f_dict):
		u_f_dict={}
		for u_id in u_it_dict:
			if u_id not in u_f_dict:
				u_f_dict[u_id]={}
			for key in u_it_dict[u_id]:
				for fe in it_f_dict[key]:
					if fe not in u_f_dict[u_id]:
						u_f_dict[u_id][fe]={}
						u_f_dict[u_id][fe]['count']=1
						u_f_dict[u_id][fe]['item']=[key]
					else:
						u_f_dict[u_id][fe]['count']+=1
						u_f_dict[u_id][fe]['item']+=[key]
		return u_f_dict

	def get_u_f_score(self,u_f_dict):
		u_f_score={}
		for u_id in u_f_dict:
			u_f_score[u_id]={}
			total_va=0
			for value in u_f_dict[u_id].values():
				total_va+=value['count']
			for key in u_f_dict[u_id].keys():
				u_f_score[u_id][key]={}
				u_f_score[u_id][key]['score']=u_f_dict[u_id][key]['count']/total_va
				u_f_score[u_id][key]['item']=u_f_dict[u_id][key]['item']
		return u_f_score
	# print(u_i_score)

	def get_it_f_dict(self):
		it_f_dict={}
		it_fea=open(self.ITEM_FEATURE_DATA,'r')
		count=0
		for lines in it_fea:
			if count==0:
				count=1
				continue
			it_id=int(lines.split(',')[0])
			fe_id=lines.split(',')[1].split(' ')[4:-1]
			if it_id not in it_f_dict:
				it_f_dict[it_id]={}
			for fe in fe_id:
				it_f_dict[it_id][int(fe)]=1
		return it_f_dict

	def recommendation_to_u(self,u_id,u_f_score,it_f_dict):
		scores={}
		for it_id in it_f_dict:
			fe_score=[]
			for fe in it_f_dict[it_id]:
				if fe in u_f_score[u_id]:
					fe_score+=[[fe,u_f_score[u_id][fe]['score']]]
			sorted_fe=sorted(fe_score,key=lambda x:x[1],reverse=True)
			scores[it_id]=(sum([x[1] for x in sorted_fe]),[x[0] for x in sorted_fe[:3]])
		sorted_scores=sorted(scores.items(),key=lambda x:x[1],reverse=True)
		return sorted_scores[:3]

	def run(self,u_id):
		final_results=""	
		u_it_dict=self.get_u_it_dict()
		it_f_dict=self.get_it_f_dict()
		u_f_dict=self.get_u_f_dict(u_it_dict,it_f_dict)
		u_f_score=self.get_u_f_score(u_f_dict)
		# out=open('recommendation.txt','w')
		# out.write('user_id'+', '+'recommend_items'+'\n')
		# u_id=input("please input user id: ")
		u_id=int(u_id)
		it_rec=self.recommendation_to_u(u_id,u_f_score,it_f_dict)
		out_it_str=""
		for it in it_rec:
			out_it_str=out_it_str+str(it[0])+" "
		final_results="You are recommended with item "+out_it_str+"because:"+'\n'
		# print("You are recommended with item "+out_it_str+"because:"+'\n')
		for it in it_rec:
			out_fe_str=""
			retri_it=""
			for fe in it[1][1]:
				out_fe_str=out_fe_str+str(fe)+" "
				retri_it=retri_it+", the item "
				for i in u_f_dict[u_id][fe]['item']:
					retri_it=retri_it+str(i)+" "
				retri_it=retri_it+"you bought has the feature "+str(fe)
			final_results=final_results+"Item "+str(it[0])+" has features "+out_fe_str+retri_it+'\n'
			# print("Item "+str(it[0])+" has features "+out_fe_str+retri_it+'\n'
		return final_results
	
