from movieLens import makeExplanation

user_id=input("please input user id:")
a=makeExplanation()
print(a.make_explanation("choose Star Wars: Episode IV",user_id))