from django import forms

class fileform(forms.Form):
	Uploaded_File = forms.FileField()