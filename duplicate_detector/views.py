from django.http import JsonResponse
import json
import requests
import base64

from .apps import DuplicateDetectorConfig


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


def check_for_duplicate(sample_changed_files_list):
    changed_files_intersections_contents_urls = []

    for pr1_changed_file in sample_changed_files_list[0]:
        for pr2_changed_file in sample_changed_files_list[1]:
            if pr1_changed_file.contents_url.split('?')[0] == pr2_changed_file.contents_url.split('?')[0]:
                changed_files_intersections_contents_urls.append([pr1_changed_file.contents_url, pr2_changed_file.contents_url])

    for changed_files_contents_urls in changed_files_intersections_contents_urls:
        file_contents = [requests.get(content_url) for content_url in changed_files_contents_urls]
