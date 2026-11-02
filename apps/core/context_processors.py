from .models import SalonInfo


def salon(request):
    return {"salon": SalonInfo.load()}
