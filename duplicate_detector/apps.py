from django.apps import AppConfig
import sys
import os
from django.conf import settings
from gensim.models import FastText
from keras.models import load_model
from tensorflow.python.util import deprecation
deprecation._PRINT_DEPRECATION_WARNINGS = False

sys.setrecursionlimit(5000)


class DuplicateDetectorConfig(AppConfig):
    name = 'duplicate_detector'

    fasttext_model_path = 'fasttext/fasttext.model'
    abs_fasttext_model_path = os.path.join(settings.MODELS, fasttext_model_path)
    word_vectors = FastText.load(abs_fasttext_model_path, mmap='r').wv
    # vocab_size, wordvec_emdedding_size = word_vectors.vectors.shape

    encoder_model_path = 'encoder/encoder.h5'
    abs_encoder_model_path = os.path.join(settings.MODELS, encoder_model_path)
    encoder_model = load_model(abs_encoder_model_path)
    encoder_encoding_dim = encoder_model.layers[-1].output_shape[1]

    # max_timestamps = max(line.count(' ') for line in open('res/method_embeddings.txt')) + 100
    max_timestamps = 10000
    print('max timestamps:', max_timestamps)

    nmt_model_path = 'nmt/nmt_encoder.h5'
    abs_nmt_model_path = os.path.join(settings.MODELS, nmt_model_path)
    # nmt_encoder_model = load_model(abs_nmt_model_path,  custom_objects={'AttentionDecoder': AttentionDecoder})
    nmt_encoder_model = load_model(abs_nmt_model_path)

    astnn_model_path = 'astnn/astnn.h5'
    abs_astnn_model_path = os.path.join(settings.MODELS, astnn_model_path)
    astnn_model = load_model(abs_astnn_model_path)