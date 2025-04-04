from django.shortcuts import redirect

def index(request):
    if 'user_id' in request.session:
        user_id = request.session.get('user_id')
        from employer.models import User
        try:
            user = User.objects.get(id=user_id)
            if user.is_employer:
                return redirect('employer:company_list')
            else:
                return redirect('candidate:index')
        except User.DoesNotExist:
            return redirect('employer:login')
    else:
        return redirect('employer:login')
