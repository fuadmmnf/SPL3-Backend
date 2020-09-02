import javalang
from threading import Thread
from itertools import combinations

from duplicate_detector.predictor.method_clone_detection import MethodRepresentationCalculator


class FileDuplicateDetector():
    file_method_repr_list = []
    method_repr_calculator = MethodRepresentationCalculator()
    def check_similarity(self, files):
        threads = []
        for file in files:
            self.__generateMethodRepresentations(file)

        file_combinations =  combinations(self.file_method_repr_list, 2)
        for file_combination in file_combinations:
            print(file_combination[0]['name'], file_combination[1]['name'])

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
