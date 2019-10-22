import json
dict1 = json.load(open("userpass.txt"))
print(dict1)
print(dict1["user"])
print(dict1["passwd"])
