from django import forms

class MatchDataForm(forms.Form):
    batting_team = forms.CharField(max_length=100)
    bowling_team = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    current_score = forms.DecimalField(max_digits=5, decimal_places=2)
    overs_done = forms.DecimalField(max_digits=3, decimal_places=1)
    wickets = forms.IntegerField(min_value=0)
    runs_in_last_5_overs = forms.DecimalField(max_digits=5, decimal_places=2)
