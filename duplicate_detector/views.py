from django.http import JsonResponse
import json

from .apps import DuplicateDetectorConfig
from .evaluator.prduplicate_evaluator import PrduplicateDetector

def test_api(request):
    return JsonResponse({'res': DuplicateDetectorConfig.encoder_encoding_dim})





def check_prduplicates(request):
    if request.method != 'POST':
        return JsonResponse({'res': 'must be post request with pr list data'})

    data = json.loads(request.body)
    PrduplicateDetector().detect_duplicate(data['pr_list'])

