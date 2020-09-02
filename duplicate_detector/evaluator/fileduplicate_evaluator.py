import javalang
from threading import Thread
from itertools import combinations

import numpy as np

from duplicate_detector.apps import DuplicateDetectorConfig
from duplicate_detector.predictor.method_clone_detection import MethodRepresentationCalculator


class FileDuplicateDetector():
    file_method_repr_list = []
    file_clonepredictions = []
    method_repr_calculator = MethodRepresentationCalculator()
    def check_similarity(self, files):
        for file in files:
            self.__generateMethodRepresentations(file)

        file_combinations =  combinations(self.file_method_repr_list, 2)
        for file_combination in file_combinations:
            self.__predictMethodClones(file_combination[0], file_combination[1])

        print(self.file_clonepredictions)
        self.file_method_repr_list = []
        self.file_clonepredictions = []
            # print(file_combination[0]['name'], file_combination[1]['name'])

    def __generateMethodRepresentations(self, file):
        self.file_method_repr_list.append({'name': file['name'], 'methods': []})
        try:
            file_tree = javalang.parse.parse(file['content'])

            for t in file_tree.types[0].body:
                if type(t) == javalang.tree.MethodDeclaration:
                    self.file_method_repr_list[-1]['methods'].append({
                        'name': t.name,
                        'line_number': t.position,
                        'repr': self.method_repr_calculator.calculateMethodRepresentation(t)
                    })
        except Exception as e:
            print(e)
            print(file)


    def __predictMethodClones(self, file1, file2):
        print(file1['name'], file2['name'], end='\n\n\n')
        for file1_method in file1['methods']:
            for file2_method in file2['methods']:

                methodDiff = np.absolute(file1_method['repr'] - file2_method['repr']).reshape(1, 200)

                clone_probability = DuplicateDetectorConfig.astnn_model.predict(methodDiff)
                # print(file1_method['name'], file2_method['name'], 'prediction: ' + str(clone_probability[0][0]))
                self.file_clonepredictions.append({
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
                    'probability': clone_probability[0][0],
                })
        # print('\n\n\n')