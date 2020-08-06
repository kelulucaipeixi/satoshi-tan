import time
import numpy as np
import csv
import Levenshtein
class makeExplanation():
	def __init__(self):
		self.USER_NUM=138494
		self.ITEM_NUM=209172
		self.FEATURE_NUM=1129
		self.batch_size=1000
		self.u_i_rat_num=20000263
		self.batch_num=int(self.u_i_rat_num/self.batch_size)+1
		self.USER_ITEM_RATING='./datasets/movieLens/user_movie_ratings.csv'
		self.ITEM_FEATURE_RELEVANCE='../datasets/ml-25m/genome-scores.csv'
		self.FEATURE_TAG='../datasets/ml-25m/genome-tags.csv'
		self.ITEM_TAG='../datasets/ml-25m/movies.csv'
		self.u_i_reader=csv.reader(open(self.USER_ITEM_RATING,'r'))
		self.i_f_reader=csv.reader(open(self.ITEM_FEATURE_RELEVANCE,'r'))
		self.i_f_rel=np.zeros([self.ITEM_NUM,self.FEATURE_NUM])
		self.u_f_map=np.zeros([self.USER_NUM,self.FEATURE_NUM])
		self.i_t_map=np.zeros(self.ITEM_NUM,dtype=object)
		self.f_t_map=np.zeros(self.FEATURE_NUM,dtype=object)
		self.get_item_tag_map()
		self.get_feature_tag_map()
		print("Now start to read i_f_rel...")
		self.get_i_f_rel()
		print("Now i_f_rel is read.")
		# print("Now training is start.")
		# header=next(self.u_i_reader)
		# for i in range(1):
		# 	u_map,u_i_rat=self.get_u_i_rat()
		# 	self.get_u_f_map(u_map,u_i_rat)
		# print("Now training is end.")

	def get_item_tag_map(self):
		with open(self.ITEM_TAG) as f:
			reader=csv.reader(f)
			header=next(reader)
			for row in reader:
				self.i_t_map[int(row[0])]=row[1]
	def get_feature_tag_map(self):
		with open(self.FEATURE_TAG) as f:
			reader=csv.reader(f)
			header=next(reader)
			for row in reader:
				self.f_t_map[int(row[0])]=row[1]
		
	def get_u_i_rat(self):
		k=-1
		u_i_rat=np.zeros([self.batch_size,self.ITEM_NUM])
		u_map=[]
		pre_user=""
		for i in range(self.batch_size):
			row=next(self.u_i_reader)
			if row[0]!=pre_user:
				pre_user=row[0]
				k+=1
				u_map.append([k,int(row[0])])

			u_i_rat[k][int(row[1])]=float(row[2])
		return u_map,u_i_rat
		# print("u_i_rat:",self.u_i_rat)
	def get_i_f_rel(self):
		header=next(self.i_f_reader)
		for row in self.i_f_reader:
			self.i_f_rel[int(row[0])][int(row[1])]=float(row[2])
		# print("i_f_rel:",self.i_f_rel)
	def get_u_f_map(self,u_map,u_i_rat):
		# print(u_i_rat[:,:34])
		part=np.dot(u_i_rat,self.i_f_rel)
		# print(part[0][:34])
		for i in u_map:
			if i[1]!=0:
				self.u_f_map[i[1]]+=part[i[0]]	
		# print("u_f_map",self.u_f_map)
	def get_top5_features(self,user_id):
		res=np.argsort(self.u_f_map[int(user_id)])[-5:]
		# print("res:",res)
		if res[-1]==0:
			return False
		else:
			return res


	def show_preference(self,user_id):
		top5_f=self.get_top5_features(user_id)
		if top5_f.any():
			results=[]
			with open(self.FEATURE_TAG) as f:
				reader=csv.reader(f)
				header=next(reader)
				for row in reader:
					for tag in top5_f:
						if tag==int(row[0]):
							results.append(row[1])
							

			out_str="You have these preferences: "
			for tag in results:
				out_str=out_str+tag+', '
			out_str=out_str[:-2]
			return out_str
		else:
			return "Sorry, user id doesn't exist. Please check your user id."
	def choose_item(self,feature_id):
		max_rel=0
		choiced_item=0
		for item_id in range(len(self.i_f_rel)):
			if self.i_f_rel[item_id][feature_id]>max_rel:
				max_rel=self.i_f_rel[item_id][feature_id]
				choiced_item=item_id
		return choiced_item

	# def make_recommendation(self,user_id):
	# 	out_str="So we recommend you these movies: "
	# 	top5_features=self.get_top5_features(user_id)
	# 	for i in top5_features:
	# 		choiced_item=self.choose_item(i)
	# 		out_str=out_str+self.i_t_map[choiced_item]+', '
	# 	out_str=out_str[:-2]
	# 	return out_str

	def get_feature(self,item_id,user_id):
		sorted_features=list(reversed(np.argsort(self.i_f_rel[item_id])))
		# sorted_preferences=list(reversed(np.argsort(self.u_f_map[user_id])))
		sorted_preferences=list(np.argsort(self.u_f_map[user_id]))
		for f in sorted_features:
			for i in range(300):
				if sorted_preferences[i]!=f:
					continue
				else:
					return self.f_t_map[f],f
	def change_feature(self,user_id,feature_id):
		if feature_id==0: 
			return
		self.u_f_map[user_id][feature_id]+=10
	def best3feat(self,movie_id):
		feat_ids=list(reversed(np.argsort(self.i_f_rel[movie_id])))[:3]
		feat_names=[self.f_t_map[i] for i in feat_ids]
		return feat_names,feat_ids

	def make_explanation(self,revised_names):
		movie_ids=[]
		user_favo_feats=[]
		user_favo_feat_ids=[]
		ans="Your favorite movie "
		for i in range(len(self.i_t_map)):
			for j in revised_names:
				if self.i_t_map[i]!=0:
					self.i_t_map[i]=self.i_t_map[i].lower()
				if self.i_t_map[i]==j:
					movie_ids+=[i]
					ans=ans+j+" has features "
					best3feat,best3feat_ids=self.best3feat(i)
					user_favo_feats+=best3feat
					user_favo_feat_ids+=best3feat_ids
					for k in best3feat:
						ans=ans+k+", "
					ans=ans+"\nand your favorite movie "
		user_favo_feat_ids=list(set(user_favo_feat_ids))
		user_favo_feats=[self.f_t_map[i] for i in user_favo_feat_ids]
		ans=ans[:-27]+". \nSo I predict your favorite features are "
		for i in user_favo_feats:
			ans=ans+i+", "
		ans=ans[:-2]+"."
		ans+="\nCould you please score for all the features listed above? The more you like the feature, you should give higher score."
		return ans,user_favo_feat_ids,user_favo_feats

	def make_recommendation(self,favo_feats,not_recommend_lists):
		feat_scores=np.zeros(self.FEATURE_NUM)
		for i in favo_feats:
			feat_scores[i]=-6.25+favo_feats[i]*favo_feats[i]
		item_scores=np.dot(self.i_f_rel,feat_scores)
		best_item_ids=list(reversed(np.argsort(item_scores)))
		best4item_names=[]
		best4item_ids=[]
		for i in best_item_ids:
			name=self.i_t_map[i]
			# if name not in not_recommend_lists:
			# 	best4item_names.append(name)
			flag=0
			for j in not_recommend_lists:
				if Levenshtein.ratio(name[:6],j[:6]) <= 0.8:
					flag+=1
			if flag == len(not_recommend_lists):
				best4item_names.append(name)
				best4item_ids.append(i)
			if len(best4item_names) >= 4:
				break
		ans=""
		for i in best4item_ids:
			name=self.i_t_map[i]

			ans=ans+"I will recommend you "+name+", because:\n "
			for f in favo_feats:
				feat_name=self.f_t_map[f]
				rel=self.i_f_rel[i][f]
				#if the feature is greatly relevant to the movie and user like the feature
				if rel > 0.7 and feat_scores[f]>=3:
					rel=round(rel,2)
					ans=ans+"the correlation of this movie to feature "+feat_name+" is "+str(rel)+".\n"
		ans=ans+"Please tell me the probability you will watch these movie."
		return ans,best4item_names

				
	