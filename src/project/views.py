from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@login_required
@ensure_csrf_cookie
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "dashboard.html", {"username": request.user.get_username()})
