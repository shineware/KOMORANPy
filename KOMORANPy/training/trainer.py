# from ..training.corpus_builder import CorpusBuilder
from ..training.model_builder import ModelBuilder

# corpus_builder = CorpusBuilder()
# # todo : 트레이닝 데이터 위치 ( 실제로는 바이너리 파일만 제공 될 예정 )
# corpus_builder.build_path("/Users/shinjunsoo/shineware/data/komoran_training_data", ".refine.txt")
# corpus_builder.save("corpus_build")

model_builder = ModelBuilder()
model_builder.build_path("corpus_build")
model_builder.save("../model")
