import javalang
from django.http import JsonResponse
import json
import requests
import base64

from .apps import DuplicateDetectorConfig
from duplicate_detector.predictor.method_clone_detection import makeFinalOutputDecision

def test_api(request):
    return JsonResponse({'res': DuplicateDetectorConfig.encoder_encoding_dim})





def check_prduplicates(request):
    if request.method != 'POST':
        return JsonResponse({'res': 'must be post request with pr list data'})

    data = json.loads(request.body)
    pr_list = data['pr_list']

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
        is_duplicate = check_for_duplicate([
            changed_files for changed_files in pr_changed_files_list
            if changed_files['pr_id'] == sample[0].id or changed_files['pr_id'] == sample[1].id]
        )


def parse_changed_methods(file1_content, file2_content):
    file1_astmethods, file2_astmethods = [], []

    try:
        file1_tree, file2_tree = javalang.parse.parse(file1_content), javalang.parse.parse(file2_content)

        for t in file1_tree.types[0].body:
            if type(t) == javalang.tree.MethodDeclaration:
                file1_astmethods.append(t)
        for t in file2_tree.types[0].body:
            if type(t) == javalang.tree.MethodDeclaration:
                file2_astmethods.append(t)

        return list(set(file1_astmethods) ^ set(file2_astmethods)), list(set(file2_astmethods) ^ set(file1_astmethods))
    except Exception as e:
        print(file1_content)
        print(file2_content)

        return None


def check_for_duplicate(sample_changed_files_list):
    changed_files_intersections_contents_urls = []

    for pr1_changed_file in sample_changed_files_list[0]:
        for pr2_changed_file in sample_changed_files_list[1]:
            if pr1_changed_file.contents_url.split('?')[0].endswith('.java') and (pr1_changed_file.contents_url.split('?')[0] == pr2_changed_file.contents_url.split('?')[0]):
                changed_files_intersections_contents_urls.append([pr1_changed_file.contents_url, pr2_changed_file.contents_url])

    for changed_files_contents_urls in changed_files_intersections_contents_urls:
        file_contents = [base64.b64decode(requests.get(content_url)) for content_url in changed_files_contents_urls]

        disjoint_changed_astmethods_list = parse_changed_methods(file_contents[0], file_contents[1])

        for file1_astmethod in disjoint_changed_astmethods_list[0]:
            for file2_astmethod in disjoint_changed_astmethods_list[1]:
                output = makeFinalOutputDecision(file1_astmethod, file2_astmethod)
                print(output)



    return False