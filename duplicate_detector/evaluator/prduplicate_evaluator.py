import javalang
import numpy as np
import requests
import base64
from duplicate_detector.predictor.method_clone_detection import MethodRepresentationCalculator

class PrduplicateDetector():
    def detect_duplicate(self, pr_list):
        pr_changed_files_list = []

        for pr in pr_list:
            changed_files = requests.get(pr.url + '/files')
            pr_changed_files_list.append({
                'pr_id': pr.id,
                'changed_files': changed_files
            })

        pr_dublicate_detection_scramble = []
        for i in range(len(pr_list)):
            for j in range(i, len(pr_list)):
                pr_dublicate_detection_scramble.append([pr_list[i], pr_list[j]])

        for sample in pr_dublicate_detection_scramble:
            is_duplicate = self.__check_for_duplicate([
                changed_files for changed_files in pr_changed_files_list
                if changed_files['pr_id'] == sample[0].id or changed_files['pr_id'] == sample[1].id]
            )

    def __parse_changed_methods(self, file1_content, file2_content):
        file1_astmethods, file2_astmethods = [], []

        try:
            file1_tree, file2_tree = javalang.parse.parse(file1_content), javalang.parse.parse(file2_content)

            for t in file1_tree.types[0].body:
                if type(t) == javalang.tree.MethodDeclaration:
                    file1_astmethods.append(t)
            for t in file2_tree.types[0].body:
                if type(t) == javalang.tree.MethodDeclaration:
                    file2_astmethods.append(t)

            return list(set(file1_astmethods) ^ set(file2_astmethods)), list(
                set(file2_astmethods) ^ set(file1_astmethods))
        except Exception as e:
            print(file1_content)
            print(file2_content)

            return None

    def __check_for_duplicate(self, sample_changed_files_list):
        changed_files_intersections_contents_urls = []

        for pr1_changed_file in sample_changed_files_list[0]:
            for pr2_changed_file in sample_changed_files_list[1]:
                if pr1_changed_file.contents_url.split('?')[0].endswith('.java') and (
                        pr1_changed_file.contents_url.split('?')[0] == pr2_changed_file.contents_url.split('?')[0]):
                    changed_files_intersections_contents_urls.append(
                        [pr1_changed_file.contents_url, pr2_changed_file.contents_url])

        changed_file_diff_repr = []
        for changed_files_contents_urls in changed_files_intersections_contents_urls:
            file_contents = [base64.b64decode(requests.get(content_url)) for content_url in changed_files_contents_urls]

            disjoint_changed_astmethods_list = self.__parse_changed_methods(file_contents[0], file_contents[1])

            file1_changed_method_representations = []
            file2_changed_method_representations = []
            method_repr_calculator = MethodRepresentationCalculator()
            for file1_astmethod in disjoint_changed_astmethods_list[0]:
                file1_changed_method_representations.append(method_repr_calculator.calculateMethodRepresentation(file1_astmethod))
            for file2_astmethod in disjoint_changed_astmethods_list[1]:
                file2_changed_method_representations.append(method_repr_calculator.calculateMethodRepresentation(file2_astmethod))

            changed_file_diff_repr.append(np.absolute(method_repr_calculator.maxpooling(file1_changed_method_representations) - method_repr_calculator.maxpooling(file2_changed_method_representations)).reshape(1, 200))

        return False