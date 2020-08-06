import csv

USER_MOVIE_RATING='../datasets/movieLens-20m/ratings.csv'
f=open(USER_MOVIE_RATING,'r')
reader=csv.reader(f)
head_row=next(reader)
user_total_ratings={}
user_rating_num={}
for row in reader:
	user_id=row[0]
	if user_id not in user_total_ratings:
		user_total_ratings[user_id]=float(row[2])
	else:
		user_total_ratings[user_id]+=float(row[2])
	if user_id not in user_rating_num:
		user_rating_num[user_id]=1
	else:
		user_rating_num[user_id]+=1
	
	# if user_id==user_id_before:
f.close()
user_average_ratings={}
for user_id in user_total_ratings:
	user_average_ratings[user_id]=user_total_ratings[user_id]/user_rating_num[user_id]
# print(user_average_ratings)
# print(user_total_ratings)
# print(user_rating_num)
f=open(USER_MOVIE_RATING,'r')
out=open('./datasets/movieLens/user_movie_ratings.csv','w',newline='')
reader=csv.reader(f)
writer=csv.writer(out)
header=next(reader)
writer.writerow(header[:3])
for row in reader:
	row[2]=str(float(row[2])-user_average_ratings[row[0]])
	writer.writerow(row[:3])
