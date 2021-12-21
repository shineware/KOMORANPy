import time

from ..core.komoran import Komoran

komoran = Komoran("../training/komoran_model")
komoran.set_fwd("../fwd.dic")
komoran.set_user_dic("../user.dic")

f = open("../core/stress.test", "r")

start = time.time()  # 시작 시간 저장
cnt = 0
for line in f.readlines():
    komoran.analyze(line.strip())
    if cnt % 10000 == 0:
        print(f"{cnt}")
    cnt += 1
end = time.time()  # 시작 시간 저장
print(f"elapsed time={(end - start)}")

f.close()
