from django.shortcuts import render
from .models import *


def home(request):
    return render(request, 'main/index.html')


def weight(request):
    tg_id = request.user.profile.tg_user_id
    # print('tg_id:', tg_id)
    if tg_id:
        results = db_get_last_weights(tg_id)
        for i in results:
            print(i)
        return render(request, 'main/weight.html')
    return render(request, 'main/weight.html')


# def test_view(request):
#     results = test()
#     for i in results:
#         print(i)
#     return render(request, 'main/test.html', {'form': results})