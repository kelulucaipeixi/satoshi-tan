from movieLens import makeExplanation

user_id=input("please input user id:")
a=makeExplanation()
print(a.run(user_id))