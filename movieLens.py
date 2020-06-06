import time
import numpy as np
import csv
class makeExplanation():
	def __init__(self):
		self.USER_NUM=138494
		self.ITEM_NUM=131171
		self.FEATURE_NUM=1129
		self.batch_size=1000
		self.u_i_rat_num=20000263
		self.batch_num=int(self.u_i_rat_num/self.batch_size)+1
		self.USER_ITEM_RATING='./datasets/movieLens/user_movie_ratings.csv'
		self.ITEM_FEATURE_RELEVANCE='../datasets/movieLens-20m/genome-scores.csv'
		self.FEATURE_TAG='../datasets/movieLens-20m/genome-tags.csv'
		self.ITEM_TAG='../datasets/movieLens-20m/movies.csv'
		self.u_i_reader=csv.reader(open(self.USER_ITEM_RATING,'r'))
		self.i_f_reader=csv.reader(open(self.ITEM_FEATURE_RELEVANCE,'r'))
		self.i_f_rel=np.zeros([self.ITEM_NUM,self.FEATURE_NUM])
		self.u_f_map=np.zeros([self.USER_NUM,self.FEATURE_NUM])
		self.i_t_map=np.zeros(self.ITEM_NUM,dtype=object)
		self.f_t_map=np.zeros(self.FEATURE_NUM,dtype=object)
		self.get_item_tag_map()
		self.get_feature_tag_map()
		print("Now start to read i_r_rel...")
		self.get_i_f_rel()
		print("Now i_r_rel is read.")
		print("Now training is start.")
		header=next(self.u_i_reader)
		for i in range(1):
			u_map,u_i_rat=self.get_u_i_rat()
			self.get_u_f_map(u_map,u_i_rat)
		print("Now training is end.")

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

	def make_recommendation(self,user_id):
		out_str="So we recommend you these movies: "
		top5_features=self.get_top5_features(user_id)
		for i in top5_features:
			choiced_item=self.choose_item(i)
			out_str=out_str+self.i_t_map[choiced_item]+', '
		out_str=out_str[:-2]
		return out_str

	def get_feature(self,item_id,user_id):
		sorted_features=list(reversed(np.argsort(self.i_f_rel[item_id])))
		sorted_preferences=list(reversed(np.argsort(self.u_f_map[user_id])))
		for f in sorted_features:
			for i in range(10):
				if sorted_preferences[i]==f:
					continue
				else:
					print(self.f_t_map[f])
					return self.f_t_map[f]

	def make_explanation(self,item_name,user_id):
		item_id=-1
		for i in range(len(self.i_t_map)):
			if self.i_t_map[i]==item_name:
				item_id=i
				break
		if item_id==-1:
			return "Sorry, the name of the movie is not correctly. Please try it again."
		unrel_feat=self.get_feature(item_id,user_id)
		out_str="The movie you chosed including the feature "+unrel_feat+" that is not in your preference, do you still want to try it?"
		return out_str