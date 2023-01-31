from django.shortcuts import render


def page_not_found(request, excetion):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def permission_denied(request, reason=''):
    return render(request, 'core/403.html', status=403)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')
