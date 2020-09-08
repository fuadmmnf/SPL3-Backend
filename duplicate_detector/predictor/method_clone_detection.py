import numpy as np

# from ..apps import DuplicateDetectorConfig
from duplicate_detector.apps import DuplicateDetectorConfig
import sys
import os
import javalang
from gensim.models import FastText
# from .attention_decoder import AttentionDecoder
from keras.models import load_model
from keras.models import Sequential
from keras.models import Model
from keras.layers import LSTM, GRU, Bidirectional
from keras.layers import Dense, Input
from tensorflow.python.util import deprecation

deprecation._PRINT_DEPRECATION_WARNINGS = False


#
# word_vectors = FastText.load("model/fasttext/fasttext.model", mmap='r').wv
# # vocab_size, wordvec_emdedding_size = word_vectors.vectors.shape
# script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
# encoder_model_path = 'model/encoder/encoder.h5'
# abs_encoder_model_path = os.path.join(script_dir, encoder_model_path)
#
# encoder_model = load_model(abs_encoder_model_path)
# encoder_encoding_dim = encoder_model.layers[-1].output_shape[1]
#
# max_timestamps = max(line.count(' ') for line in open('res/method_embeddings.txt')) + 100
# print('max timestamps:', max_timestamps)
#
# nmt_model_path = 'model/nmt/nmt_encoder.h5'
# abs_nmt_model_path = os.path.join(script_dir, nmt_model_path)
#
# nmt_encoder_model = load_model(abs_nmt_model_path,  custom_objects={'AttentionDecoder': AttentionDecoder})
# nmt_encoder_model = load_model(abs_nmt_model_path)
#

# print(nmt_encoder_model.summary())
# quit()
class MethodRepresentationCalculator:

    def __init__(self) -> None:
        super().__init__()
        self.StatementTrees = []
        self.StTreeNodesForMaxPooling = []
        sys.setrecursionlimit(10000)

    def maxpooling(self, arr):
        stTreesVecs = np.asarray(arr)
        maxpooledEncoding = np.amax(stTreesVecs, axis=0)
        print(maxpooledEncoding[0])
        return maxpooledEncoding[0]

    def __makeNmtRepresentation(self, maxpooled_stTrees):
        nmt_encoded_stTrees = []
        methodInput = []
        for maxpooled_stTree in maxpooled_stTrees:
            methodInput.extend(maxpooled_stTree.tolist())

        spaceForPadding = (DuplicateDetectorConfig.max_timestamps * DuplicateDetectorConfig.encoder_encoding_dim) - len(methodInput)
        # print('method vector length actual: ', len(methodInput))
        methodInput.extend([0 for x in range(spaceForPadding)])

        stTreeInput = np.asarray(methodInput).reshape(DuplicateDetectorConfig.max_timestamps, DuplicateDetectorConfig.encoder_encoding_dim)
        input = np.asarray([stTreeInput])

        stTreeNmtRepr = DuplicateDetectorConfig.nmt_encoder_model.predict(input, verbose=0)
        nmt_encoded_stTrees.append(stTreeNmtRepr[0])

        return self.maxpooling(nmt_encoded_stTrees)

    def __computeEncodedTree(self, node):
        nodeVecs = {}
        child_sum = np.zeros(DuplicateDetectorConfig.encoder_encoding_dim)
        childNodesList = []

        for _, subnode in node:

            if subnode is None:
                print('none')

            subnode_str = str(subnode).replace('\"', '_').replace('\'', '_').replace(' ', '')

            childNodesList.append({subnode_str: subnode.children})
            fasttext_embedding = DuplicateDetectorConfig.word_vectors[subnode_str].reshape(1, 128)
            # print(fasttext_embedding.shape)
            # quit()
            subnode_encoding = DuplicateDetectorConfig.encoder_model.predict(fasttext_embedding, verbose=0)
            nodeVecs[subnode_str] = subnode_encoding

            for child in subnode.children:
                child_str = str(child).replace('\"', '_').replace('\'', '_').replace(' ', '')
                fasttext_embedding = DuplicateDetectorConfig.word_vectors[child_str].reshape(1, 128)
                subnode_encoding = DuplicateDetectorConfig.encoder_model.predict(fasttext_embedding, verbose=0)
                nodeVecs[child_str] = subnode_encoding

        for nodeDict in reversed(childNodesList):
            for key in nodeDict:
                for childNode in nodeDict[key]:
                    childNode_str = str(childNode).replace('\"', '_').replace('\'', '_').replace(' ', '')
                    nodeVecs[key] = nodeVecs[key] + nodeVecs[childNode_str]

        # eqn2 of paper
        # node_str = str(node).replace('\"', '_').replace('\'', '_').replace(' ', '')
        # fasttext_embedding = word_vectors[node_str]
        # node_encoding = model.predict(fasttext_embedding, verbose=0)
        # node_vec = node_encoding + child_sum

        for key in nodeVecs:
            self.StTreeNodesForMaxPooling.append(nodeVecs[key])

    def __encodeStTrees(self):
        maxpooled_stTrees = []

        print('started encoding...')

        for tree in self.StatementTrees:
            self.__computeEncodedTree(tree)

            maxpooled_stTrees.append(self.maxpooling(self.StTreeNodesForMaxPooling))

            # maxpooling and write all st tree of methods to file
            self.StTreeNodesForMaxPooling = []

        print('finished encoding...')

        return maxpooled_stTrees

    def __clean_statement(self, statement):
        for _, node in statement:
            if hasattr(node, 'member'):
                node.member = None
            if hasattr(node, 'value'):
                node.value = None

            if hasattr(node, 'documentation'):
                node.documentation = None
            if type(node) is not javalang.tree.ReferenceType:
                if hasattr(node, 'name'):
                    node.name = None

    def __handleSubStatement(self, statement):
        isStatementValid = True
        subStatement = None

        if hasattr(statement, 'body') and statement.body is not None:
            subStatement = statement.body
            statement.body = None
        elif hasattr(statement, 'block') and statement.block is not None:
            subStatement = statement.block
            statement.block = None
        elif hasattr(statement, 'statements'):
            isStatementValid = False
            subStatement = statement.statements
            statement.statements = None
        # elif hasattr(statement, 'expression'):
        # 	subStatement = statement.expression
        # 	del statement.expression

        if isStatementValid:
            self.StatementTrees.append(statement)
        # appendToCorpus(statement)

        if subStatement is not None:
            self.__pluckStatementAndAppendToStatementTree(subStatement)

    def __pluckStatementAndAppendToStatementTree(self, statementBlock):
        if type(statementBlock) is list:
            for statement in statementBlock:
                self.__handleSubStatement(statement)
        else:
            self.__handleSubStatement(statementBlock)

    def __computeMethodRepresentation(self, astmethod):
        try:

            self.__clean_statement(astmethod)
            # self.StatementTrees.append(t)
            # appendToCorpus(t)
            self.__pluckStatementAndAppendToStatementTree(astmethod)
            encoded_stTrees = self.__encodeStTrees()
            method_representation = self.__makeNmtRepresentation(encoded_stTrees)
            # print(method_representation)
            # print('\n\n\n')

            self.StatementTrees = []

            return method_representation

        except Exception as e:
            print(e)
            print('\n\n\n')
            quit()
            self.StatementTrees = []
            return

    def __parseMethodAndReturnRepresentation(self, filepath, startline, endline):
        # print(filepath)
        try:
            fileData = ''
            with open(filepath, 'r', encoding='utf-8') as file:
                fileData = file.readlines()
            fileData = "\n".join(line for line in fileData[startline - 1: endline])

            code_segment = 'class Temp {\n' + fileData + '}'
            # print(code_segment)
            # quit()
            tree = javalang.parse.parse(code_segment)  # Create your   here.
            for t in tree.types[0].body:
                if type(t) == javalang.tree.MethodDeclaration:
                    self.__clean_statement(t)
                    # self.StatementTrees.append(t)
                    # appendToCorpus(t)
                    self.__pluckStatementAndAppendToStatementTree(t)
                    # print('starting calc')
                    encoded_stTrees = self.__encodeStTrees()
                    method_representation = self.__makeNmtRepresentation(encoded_stTrees)
                    # print('finish calc')

                    # print(method_representation)
                    # print('\n\n\n')

                    self.StatementTrees = []

                    return method_representation

        except Exception as e:
            print('error file:' + filepath)
            print(e)
            print('\n\n\n')
            # quit()
            self.StatementTrees = []
            return None

    def calculateMethodRepresentation(self, astmethod):
        method_repr = self.__computeMethodRepresentation(astmethod)
        print('\n\n\n', method_repr)
        return method_repr
        # methodDiff = np.absolute(method1Repr - method2Repr).reshape(1, 200)

        # clone_probability = DuplicateDetectorConfig.astnn_model.predict(methodDiff)
        # print('prediction: ' + str(clone_probability[0][0]))
        #
        # return clone_probability[0][0]
