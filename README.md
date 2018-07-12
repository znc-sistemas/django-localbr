django-localbr
==============

Localization of FormFields, Widgets and etc to Brazilian Portuguese



Exemplo:

    class CadastroForm(forms.ModelForm):

        cpf = BRCPFField(always_return_formated=True, return_format=u'%s%s%s%s')

        class Meta:
            model = models.Cadastro
            fields = (
                'nome_completo',
                'cpf',
                'empresa',
                'mail',
                'celular',
            )
