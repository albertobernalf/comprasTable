from django.db import models

# Create your models here.

from django.utils.timezone import now

# Create your models here.

class SedesCompra(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    codreg_sede = models.CharField(max_length=30, default='')
    nom_sede = models.CharField(max_length=30, default='')
    codreg_ips = models.CharField(max_length=30, default='')
    direccion = models.CharField(max_length=200, default='')
    telefono = models.CharField(max_length=120, default='')
    departamento = models.CharField(max_length=120, default='')
    municipio = models.CharField(max_length=120, default='')
    zona = models.CharField(max_length=120, default='')
    sede = models.CharField(max_length=120, default='')
    estadoreg = models.CharField(max_length=1, default='A', editable=True, choices=TIPO_CHOICES, )

    class Meta:
        unique_together = ("codreg_sede", "nom_sede")

    def __str__(self):
        return self.nom_sede


class Usuarios(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    num_identificacion = models.CharField(max_length=30)
    nom_usuario = models.CharField(max_length=150)
    clave_usuario = models.CharField(max_length=20)
    carg_usuario = models.CharField(max_length=80)
    sede = models.ForeignKey('solicitud.SedesCompra', default=1, on_delete=models.PROTECT, null=True, related_name='ssedesCompra')
    estadoreg = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return self.nom_usuario

class TiposCompra(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique = True)
    descripcion = models.CharField(max_length=150)
    estadoreg = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return self.nombre

class EstadosValidacion(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique = True)
    estadoreg = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return self.nombre


class Presentacion(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique = True)
    descripcion = models.CharField(max_length=150)
    estadoreg = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return self.nombre


class DescripcionCompra(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique = True)
    descripcion = models.CharField(max_length=150)
    estadoreg = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return self.nombre

class Proveedores(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    codreg_proveedor = models.CharField(max_length=50, unique = True)
    proveedor = models.CharField(max_length=80, unique = True)
    nit = models.CharField(max_length=30, unique = True, default='')
    direccion = models.CharField(max_length=80, unique=False, default='')
    telefono = models.CharField(max_length=30,unique=False, default=0)
    correo =  models.EmailField(max_length=200)
    estadoreg = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return self.proveedor



class Areas(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    sede = models.ForeignKey('SedesCompra', default=1, on_delete=models.PROTECT, null=True, related_name='ssedesArea')
    area        = models.CharField(max_length=80, default='')
    estadoreg = models.CharField(max_length=1, default='A', editable=True, choices=TIPO_CHOICES, )

    def __str__(self):
        return self.area


class Solicitudes(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(default=now, editable=True)
    usuarios = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,related_name='uusuarios')
    area = models.ForeignKey('Areas', default=1, on_delete=models.PROTECT, null=True, related_name='aareasSolicitudes')

    estadoreg = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return str(self.fecha)

class SolicitudesDetalle(models.Model):
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )
    id = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey('Solicitudes', default=1, on_delete=models.PROTECT, null=True,related_name='ssolicitudes')

    item = models.IntegerField()
    descripcion = models.ForeignKey('DescripcionCompra', default=1, on_delete=models.PROTECT, null=True, related_name='ddescripcion')
    tiposCompra = models.ForeignKey('TiposCompra', default=1, on_delete=models.PROTECT, null=True, related_name='ttipoCompra')
    cantidad =models.IntegerField()
    presentacion = models.ForeignKey('Presentacion', default=1, on_delete=models.PROTECT, null=True,
                                     related_name='ppresentacion')
    producto = models.CharField(max_length=30, default='')
    justificacion = models.CharField(max_length=250, default=0)
    estadosSolicitud = models.ForeignKey('EstadosValidacion', default=1, on_delete=models.PROTECT, null=True, related_name='eestadosSolicitud')
    usuarioResponsableValidacion  = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,related_name='uusuariosResponsable')
    especificacionesTecnicas = models.CharField(max_length=300, default='')
    estadosValidacion = models.ForeignKey('EstadosValidacion', default=1, on_delete=models.PROTECT, null=True,related_name='eestadosValidacion')

    especificacionesAlmacen = models.CharField(max_length=300, default='')
    solicitadoAlmacen = models.IntegerField(default=0)
    entregadoAlmacen = models.IntegerField(default=0)
    usuarioResponsableAlmacen = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True, related_name='uusuariosResponsableAlmacen')
    estadosAlmacen = models.ForeignKey('EstadosValidacion', default=1, on_delete=models.PROTECT, null=True, related_name='eestadosAlmacen')
    especificacionesCompras = models.CharField(max_length=300, default='')
    usuarioResponsableCompra = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,    related_name='uusuariosResponsableCompra')
    estadosCompras = models.ForeignKey('EstadosValidacion', default=1, on_delete=models.PROTECT, null=True, related_name='eestadosCompras')
    ordenCompra    = models.ForeignKey('OrdenesCompra',  on_delete=models.PROTECT, null=True, related_name='oordenesCompra')
    solicitadoOrdenCantidad = models.DecimalField(max_digits=20, decimal_places=2,default=0)
    recibidoOrdenCantidad   = models.DecimalField(max_digits=20, decimal_places=2,default=0)
    valorUnitario           = models.DecimalField(max_digits=20, decimal_places=2,default=0)
    iva                     = models.DecimalField(max_digits=20, decimal_places=2,default=0)
    solicitadoOrdenValor    = models.DecimalField(max_digits=20, decimal_places=2,default=0)
    recibidoOrdenValor      = models.DecimalField(max_digits=20, decimal_places=2,default=0)
    estadoreg = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return self.estadoreg


class OrdenesCompra(models.Model):
    VIGENTE = 'V'
    CADUCA = 'C'
    ESTADO_ORDEN = (
        (VIGENTE, 'Vigente'),
        (CADUCA, 'Caduca'),
    )
    CONTRA_ENTREGA = 'C'
    ANTICIPO = 'A'
    NOVENTADIAS = 'N'
    OPCIONES = (
        (CONTRA_ENTREGA, 'Contra entrega'),
        (ANTICIPO, 'Anticipo'),
        (NOVENTADIAS, 'Noventa dias'),
    )
    ACTIVO = 'A'
    INACTIVO = 'I'
    TIPO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    )

    id             = models.AutoField(primary_key=True)
    fechaElab      = models.DateTimeField(default=now, editable=True)
    fechaRevi      = models.DateTimeField(default=now, editable=True)
    fechaApro      = models.DateTimeField(default=now, editable=True)
    estadoOrden    = models.CharField(max_length=1, default='A', editable=True ,choices=ESTADO_ORDEN,)
    elaboro        = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,related_name='uusuariosElaboro')
    revizo         = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,related_name='uusuariosrEVIZO')
    aprobo         = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,related_name='uusuariosaPROBO')
    area           = models.ForeignKey('Areas', default=1, on_delete=models.PROTECT, null=True, related_name='aareasoRDENES')
    contacto       = models.CharField(max_length=120, default='')
    entregarEn     = models.CharField(max_length=120, default='')
    telefono       = models.CharField(max_length=30, default='')
    proveedor      = models.ForeignKey('Proveedores', default=1, on_delete=models.PROTECT, null=True,related_name='pproveedores')
    opciones       = models.CharField(max_length=1, default='A', editable=True ,choices=OPCIONES,)
    valorBruto     = models.DecimalField(max_digits=20, decimal_places=2)
    descuento      = models.DecimalField(max_digits=20, decimal_places=2)
    valorParcial   = models.DecimalField(max_digits=20, decimal_places=2)
    iva            = models.DecimalField(max_digits=20, decimal_places=2)
    valorTotal     = models.DecimalField(max_digits=20, decimal_places=2)
    observaciones  = models.CharField(max_length=300, default='')
    responsableCompra = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,related_name='uusuariosResp')
    entragaMercancia  = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,related_name='uusuariosEntrega')
    recibeMercancia   = models.ForeignKey('Usuarios', default=1, on_delete=models.PROTECT, null=True,related_name='uusuariosRecibe')
    estadoReg      = models.CharField(max_length=1, default='A', editable=True ,choices=TIPO_CHOICES,)

    def __str__(self):
        return self.observaciones