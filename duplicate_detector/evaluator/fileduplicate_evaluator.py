import json

import javalang
from itertools import combinations

import numpy as np
from duplicate_detector.predictor.method_clone_detection import MethodRepresentationCalculator


class FileDuplicateDetector():
    def __init__(self):
        self.file_method_repr_list = []
        self.file_clonepredictions = []
        self.method_clone_predictor = MethodRepresentationCalculator()

    def check_similarity(self, files):
        for file in files:
            self.__generateMethodRepresentations(file)

        file_combinations = combinations(self.file_method_repr_list, 2)
        for file_combination in file_combinations:
            self.__predictMethodClones(file_combination[0], file_combination[1])

        print(self.file_clonepredictions)
        return self.file_clonepredictions
        # print(file_combination[0]['name'], file_combination[1]['name'])

    def __generateMethodTree(self, func):
        try:
            tokens = javalang.tokenizer.tokenize(func)
            parser = javalang.parser.Parser(tokens)
            method_tree = parser.parse_member_declaration()
            return {
                'name': method_tree.name,
                'line_number': method_tree.position,
                'repr': method_tree
            }
        except Exception as e:
            return None

    def __generateMethodRepresentations(self, file):
        self.file_method_repr_list.append({'name': file['name'], 'methods': []})
        try:
            file_tree = javalang.parse.parse(file['content'])

            for path, node in file_tree.filter(javalang.tree.MethodDeclaration):
                self.file_method_repr_list[-1]['methods'].append(self.__generateMethodTree(node))
        except Exception as e:
            print(e)
            print(file)

    def __predictMethodClones(self, file1, file2):
        for file1_method in file1['methods']:
            for file2_method in file2['methods']:
                # print(file1_method['name'], file2_method['name'], 'prediction: ' + str(clone_probability[0][0]))
                output = self.method_clone_predictor.predict_clone(file1_method['repr'], file2_method['repr'])

                self.file_clonepredictions.append({
                    'id': file1['name'] + '_' + file2['name'],
                    'file1': file1['name'],
                    'file2': file2['name'],
                    'file1_method': {
                        'name': file1_method['name'],
                        'line_number': file1_method['line_number'].line
                    },
                    'file2_method': {
                        'name': file2_method['name'],
                        'line_number': file2_method['line_number'].line
                    },
                    'probability': json.dumps(str(clone_probability[0][0])),
                    'type': self.__getCloneType(clone_probability[0][0]),
                })
        # print('\n\n\n')
