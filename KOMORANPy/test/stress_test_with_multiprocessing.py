import time
from multiprocessing.pool import Pool

from ..core.komoran import Komoran

komoran = Komoran("../training/komoran_model")
komoran.set_fwd("../fwd.dic")
komoran.set_user_dic("../user.dic")

f = open("../core/stress.test", "r")
cnt = 0


def analyze(_line):
    return komoran.analyze(_line.strip())


start = time.time()  # 시작 시간 저장

pool = Pool(processes=8)
analyze_results = pool.map(analyze, f.readlines())
for analyze_result in analyze_results:
    result_tmp = []
    for word, pos in analyze_result:
        result_tmp.append(word+"/"+pos)
    print(f"{cnt}={' '.join(result_tmp)}")
    cnt += 1
pool.close()
pool.join()
end = time.time()  # 시작 시간 저장
print(f"elapsed time={(end - start)}")

f.close()
