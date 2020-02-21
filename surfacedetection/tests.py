
Edgepair.MergeOverlapping test



a = [[1,2],[4,5]]
b = [[1,3],[2,4]]
c = [[1,3],[2,4],[5,7]]
d = [[1,3],[2,5],[4,6]]
e = [[1,3],[2,5],[4,6], [7,8]]
f = [[1,3],[2,5],[4,7], [6,8]]

ao = [[1,2],[4,5]]
bo = [[1,4]]
co = [[1,4],[5,7]]
do = [[1,6]]
eo = [[1,6],[7,8]]
fo = [[1,8]]

t = [a,b,c,d,e,f]

for i in t:
	ps = [EdgePair.Make(j) for j in i]
	for j in EdgePair.MergeOverlapping(ps):
		print(j)
	print()


SurfaceStrip.Subtract test

a = [(2,3),(4,5)]
b = [(1,6)]

c = [(2,4)]
d = [(1,3)]

e = [(2,5)]
f = [(1,3),(4,6)]

print(SurfaceStrip.Subtract(f,e))











