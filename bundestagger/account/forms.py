from django import forms

class OpenIDSignupForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        # TODO: do something with these?
        self.openid = kwargs.pop("openid")
        self.reserved_usernames = kwargs.pop("reserved_usernames")
        # start added
        # end added
        super(OpenIDSignupForm, self).__init__(*args, **kwargs)
        
    def clean_username(self):
        if self.cleaned_data["username"] in self.reserved_username:
            raise forms.ValidationError(u"Dieser Nutzername ist reserviert")
        return self.cleaned_data["username"]
    
    def save(self):
        new_user = User()
        new_user.username = self.cleaned_data["username"]
        new_user.openid = self.openid
        new_user.save()
        return new_user