import numpy as np
a = np.array([[6,7,8],[1,2,3], [9,3,2]])

for row in a :
	print(row)

print("only row works:")
for col in a :
	print(col)

flat=a.flat
for b in flat:
	print(b)

#Reshape
print(np.arange(6).reshape(3,2))

# Stack vertically, horizontally
a=np.arange(6).reshape(3,2)
b=np.arange(6,12).reshape(3,2)
print "a={}".format(a)
print "b={}".format(b)
c=np.vstack((a,b))
print "c={}".format(c)
d=np.hstack((a,b))
print "d={}".format(d)

# split array into n arrays
print "hsplit(d.0)={}".format(np.hsplit(d,2)[0])
print "hsplit(d.1)={}".format(np.hsplit(d,2)[1])

print "vsplit(d.0)={}".format(np.vsplit(d,3)[0])
print "vsplit(d.1)={}".format(np.vsplit(d,3)[1])
print "vsplit(d.2)={}".format(np.vsplit(d,3)[2])

# Create an array, if elements are >= items of array d, the true
e = d > 4
print "e=\n{}".format(e)
d[e]=-1
print "after d[e]=-1, d:\n{}".format(d)

