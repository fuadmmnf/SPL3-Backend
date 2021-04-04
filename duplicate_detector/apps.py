from django.apps import AppConfig
import sys
import os
from django.conf import settings
import numpy as np
import torch
from gensim.models.word2vec import Word2Vec
from duplicate_detector.predictor.model import BatchEncoderBiGRU

sys.setrecursionlimit(10000)


class DuplicateDetectorConfig(AppConfig):
    name = 'duplicate_detector'
    CATEGORIES_COUNT = 5

    word2vec_model_path = 'word2vec/node_w2v_128'
    abs_fasttext_model_path = os.path.join(settings.MODELS, word2vec_model_path)
    word2vec = Word2Vec.load(abs_fasttext_model_path).wv
    word2vec_vocab = word2vec.vocab

    MAX_TOKENS = word2vec.syn0.shape[0]
    EMBEDDING_DIM = word2vec.syn0.shape[1]
    embeddings = np.zeros((MAX_TOKENS + 1, EMBEDDING_DIM), dtype="float32")
    embeddings[:word2vec.syn0.shape[0]] = word2vec.syn0

    HIDDEN_DIM = 100
    ENCODE_DIM = 128
    LABELS = 1
    EPOCHS = 5
    BATCH_SIZE = 16
    USE_GPU = False

    LOSS_FUNCTION = torch.nn.BCELoss()
    ASTNN_MODELS = [None]
    for i in range(1, CATEGORIES_COUNT):
        astnn_model_path = 'astnn/modelClone' + str(i)
        abs_astnn_model_path = os.path.join(settings.MODELS, astnn_model_path)
        model = BatchEncoderBiGRU(EMBEDDING_DIM, HIDDEN_DIM, MAX_TOKENS + 1, ENCODE_DIM, LABELS, BATCH_SIZE, USE_GPU,
                                  embeddings)
        model.load_state_dict(torch.load(abs_astnn_model_path))
        ASTNN_MODELS.append(model)
