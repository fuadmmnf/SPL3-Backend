from django.http import JsonResponse

from .apps import DuplicateDetectorConfig

def test_api(request):
    return JsonResponse({'res': DuplicateDetectorConfig.encoder_encoding_dim})