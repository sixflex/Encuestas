from django.shortcuts import redirect

def home(request):
    if request.user.is_authenticated:
        return redirect("usuarios_lista")   # a /personas/usuarios/
    return redirect("login")                 # a /accounts/login/
