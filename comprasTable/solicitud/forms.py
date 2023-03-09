from django import forms
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Solicitudes, SolicitudesDetalle, EstadosValidacion
from solicitud.models import Usuarios, SedesCompra, Areas, EstadosValidacion, OrdenesCompra, Proveedores
import django.core.validators
import django.core.exceptions
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
import datetime


class solicitudesForm(forms.ModelForm):

    class Meta:
        model = Solicitudes

        id = forms.IntegerField(label='Solicitud No', disabled=True, initial=0)
        fecha = forms.DateTimeField()
        area_id = forms.ModelChoiceField(queryset=Areas.objects.all())
        usuarios_id = forms.IntegerField(label='Usuario', disabled=True, initial=0)
        estadoReg = forms.CharField(max_length=1)

        fields = '__all__'

        widgets = {

            'id':  forms.TextInput(attrs={'readonly': 'readonly'}),
            'fecha': forms.TextInput(attrs={'readonly': 'readonly'})
        }

class solicitudesDetalleForm(forms.ModelForm):

    class Meta:
        model = SolicitudesDetalle

        id = forms.IntegerField(label='Solicitud No', disabled=True, initial=0)
        item = forms.IntegerField(label='Item', disabled=True, initial=0)
        descripcion = forms.IntegerField(label='Descripcion', disabled=True, initial=0)
        tiposCompra = forms.IntegerField(label='tiposCompra', disabled=True, initial=0)
        producto = forms.IntegerField(label='Producto', disabled=True, initial=0)
        presentacion = forms.IntegerField(label='presentacion', disabled=True, initial=0)
        cantidad = forms.IntegerField(label='Cantidad', disabled=True, initial=0)
        justificacion = forms.IntegerField(label='Justificacion', disabled=True, initial=0)
        especificacionesTecnicas = forms.CharField(label='especificacionesTecnicas', max_length=1)
        usuarioResponsableValidacion = forms.CharField(label='usuarioResponsableValidacion', max_length=1)
        estadosValidacion = forms.CharField(label='estadosValidacion', max_length=1)
        #estadosValidacion = forms.ModelChoiceField(queryset=EstadosValidacion.objects.all() , required=True)
      # solicitud_id = forms.IntegerField(label='solicitud_id', disabled=True, initial=0)
        #estadosValidacion = forms.ModelChoiceField(queryset=EstadosValidacion.objects.all(), label='name',widget=forms.Select )

        #fields = '__all__'
        fields = ['id', 'item', 'descripcion', 'tiposCompra','producto','presentacion','cantidad', 'justificacion','especificacionesTecnicas',  'usuarioResponsableValidacion','estadosValidacion' ]

        widgets = {

            'id':  forms.TextInput(attrs={'readonly': 'readonly'}),
            'item': forms.TextInput(attrs={'readonly': 'readonly'}),
            'cantidad': forms.TextInput(attrs={'readonly': 'readonly'}),
            'tiposCompra': forms.TextInput(attrs={'readonly': 'readonly'}),
            'producto': forms.TextInput(attrs={'readonly': 'readonly'}),
            'estadoReg': forms.TextInput(attrs={'readonly': 'readonly'}),
            'descripcion_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'estadosSolicitud_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'presentacion_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            #'estadosValidacion': forms.Select(attrs={'class': 'form-control'})
          #  'solicitud_id': forms.TextInput(attrs={'readonly': 'readonly'}),

        }


class ordenesCompraForm(forms.ModelForm):

    class Meta:
        model = OrdenesCompra

        id = forms.IntegerField(label='Orde de Compra No', disabled=True, initial=0)
        fechaElab = forms.DateField(initial=datetime.date.today)
        fechaRevi = forms.DateField(initial=datetime.date.today)
        fechaApro = forms.DateField(initial=datetime.date.today)
        estadoOrden =  forms.CharField(label='estadoOrdenon', max_length=1)
        elaboro_id = forms.IntegerField(label='Usuario', disabled=True, initial=0)
        revizo_id = forms.IntegerField(label='Usuario', disabled=True, initial=0)
        aprobo_id = forms.IntegerField(label='Usuario', disabled=True, initial=0)
        area_id = forms.ModelChoiceField(queryset=Areas.objects.all())
        contacto =  forms.CharField(max_length=120)
        entregarEn =  forms.CharField(max_length=120)
        telefono =   forms.CharField(max_length=120)
        proveedor_id = forms.ModelChoiceField(queryset=Proveedores.objects.all())
        opciones =  forms.CharField(max_length=10)
        valorBruto  = forms.DecimalField()
        descuento = forms.DecimalField()
        valorParcial  = forms.DecimalField()
        iva = forms.DecimalField()
        valorTotal = forms.DecimalField()
        observaciones =   forms.CharField(max_length=300)
        responsableCompra_id = forms.IntegerField(label='Usuario', disabled=True, initial=0)
        entragaMercancia_id = forms.IntegerField(label='Usuario', disabled=True, initial=0)
        recibeMercancia_id = forms.IntegerField(label='Usuario', disabled=True, initial=0)
        #estadoReg = forms.CharField(max_length=120)

        fields = '__all__'

        widgets = {

            'id': forms.TextInput(attrs={'readonly': 'readonly'}),


        }

        def clean_contacto(self):
            print ("Entre Contacto")
            data = self.cleaned_data['contacto']

            print("Esto se digito", data)

            # Check date is not in past.
            if not data:
                 raise ValidationError(_('Campo Obligatorio'))

            return data
