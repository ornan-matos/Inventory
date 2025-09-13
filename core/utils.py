from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def admin_required(view_func):
    """
    Decorator que verifica se o usuário logado é um superusuário ou
    tem o user_type definido como 'admin'.
    """
    def check_user(user):
        return user.is_authenticated and (user.is_superuser or user.user_type == 'admin')

    decorated_view = user_passes_test(
        check_user,
        login_url='login',
        redirect_field_name=None
    )(view_func)
    return decorated_view
