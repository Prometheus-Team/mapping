import time
import multiprocessing as mp

t = time.time()
pool = mp.Pool(mp.cpu_count())

results = [pool.apply(howmany_within_range, args=(row, 4, 8)) for row in data]

pool.close()   
print(time.time() - t) 