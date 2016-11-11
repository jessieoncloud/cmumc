@login_required
def switch(request):
    print("switch backend")
    print("username:"+request.POST['username'])

    user_profile = get_object_or_404(Profile, user=request.POST['username'])
    if user_profile.user_type == 'H':
        user_profile.user_type = 'R'
    else:
        user_profile.user_type = 'H'
    user_profile.save()

    return redirect('stream')