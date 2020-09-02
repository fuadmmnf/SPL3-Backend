import javalang

from duplicate_detector.predictor.method_clone_detection import MethodRepresentationCalculator


class FileDuplicateDetector():
    def check_similarity(self, files):
        file_method_repr_list = []
        method_repr_calculator = MethodRepresentationCalculator()
        for file in files:
            file_method_repr_list.append({'name': file['name'], 'methods': []})
            try:
                file_tree = javalang.parse.parse(file['content'])

                for t in file_tree.types[0].body:
                    if type(t) == javalang.tree.MethodDeclaration:
                        file_method_repr_list[-1]['methods'].append({
                            'name': t.name,
                            'line_number': t.position,
                            'repr': method_repr_calculator.calculateMethodRepresentation(t)
                        })
            except Exception as e:
                print(e)
                print(file)

        print(file_method_repr_list)
