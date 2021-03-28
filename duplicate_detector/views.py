from django.http import JsonResponse
import json

from .apps import DuplicateDetectorConfig
from .evaluator.fileduplicate_evaluator import FileDuplicateDetector
from django.views.decorators.csrf import csrf_exempt



def test_api(request):
    return JsonResponse({'res': DuplicateDetectorConfig.encoder_encoding_dim})




@csrf_exempt
def check_duplicates(request):
    if request.method != 'POST':
        return JsonResponse({'res': 'must be post request with pr list data'})

    data = json.loads(request.body)
    file_clonepredictions = FileDuplicateDetector().check_similarity(data['files'])
    return JsonResponse({'data':file_clonepredictions}, safe=False)
