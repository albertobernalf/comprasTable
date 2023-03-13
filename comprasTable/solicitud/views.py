from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import re
from django.http import FileResponse
import psycopg2
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
import json
from django.views.generic import ListView, CreateView, TemplateView
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.models.functions import Cast, Coalesce
import numpy  as np
from django.utils.encoding import smart_str
from datetime import datetime
from django.urls import reverse
import numpy as np
import time
import _thread

import pylab as pl
from unicodedata import normalize


## De Reporteador

import io
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from django.core import serializers
from io import StringIO
from io import BytesIO
import itertools


#from datascience import *

from django.conf import settings
import os
from datetime import datetime
from datetime import date

from email.message import EmailMessage
import smtplib
from email import encoders

import json
from .forms import solicitudesDetalleForm, solicitudesForm, ordenesCompraForm
from solicitud.models import SolicitudesDetalle, EstadosValidacion, OrdenesCompra
from django.views.generic import View
from django.views.generic import TemplateView
import openpyxl
from openpyxl.styles import Font
from decimal import Decimal

# Create your views here.

def index(request):
    print ("Entre index")
    return render(request, 'index.html')


def menuAcceso(request):
    print ("Ingreso al Menu Compras")
    context = {}

    # Sedes
    miConexion  = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432" , user="postgres", password="BD_m3d1c4l")
    cur = miConexion.cursor()
    comando = 'SELECT ltrim(codreg_sede), nom_sede FROM public.solicitud_sedesCompra'
    cur.execute(comando)
    print(comando)

    sedes = []

    for codreg_sede, nom_sede in cur.fetchall():
        sedes.append({'codreg_sede':codreg_sede, 'nom_sede' : nom_sede})
    miConexion.close()

    context['Sedes'] = sedes

    return render(request, "accesoPrincipal.html", context)


def validaAcceso(request):

    print ("Entre Validacion Acceso Compras")
    context = {}

    # Sedes
    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()
    comando = 'SELECT id, codreg_sede, nom_sede FROM public.solicitud_sedesCompra'
    cur.execute(comando)
    print(comando)

    sedes = []

    for id,codreg_sede, nom_sede in cur.fetchall():
        sedes.append({'id' : id, 'codreg_sede': codreg_sede, 'nom_sede': nom_sede})
    miConexion.close()

    context['Sedes'] = sedes
    print ("Aqui estan las sedes")
    print (context['Sedes'])

    username = request.POST["username"]
    contrasena = request.POST["password"]
    sedeSeleccionada   = request.POST["seleccion2"]
    print ("sedeSeleccionada = " , sedeSeleccionada)
    print("username = ", username)
    print ("contrasena = ", contrasena)
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada


    # Consigo Nombre de la sede

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                              password="BD_m3d1c4l")
    cur = miConexion.cursor()
    comando = "SELECT id,codreg_sede, nom_sede FROM public.solicitud_sedesCompra WHERE codreg_sede = '" + sedeSeleccionada + "'"
    #comando = 'SELECT codreg_sede, nom_sede FROM public."Administracion_imhotep_sedesreportes" where estadoReg=' + "'A'"
    cur.execute(comando)
    print(comando)

    nombreSede = []

    for id,codreg_sede, nom_sede in cur.fetchall():
        nombreSede.append({'id' : id,'codreg_sede': codreg_sede, 'nom_sede': nom_sede})

    miConexion.close()

    context['NombreSede'] = nombreSede[0]['nom_sede']

    # Validacion Usuario existente

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()
    comando = "SELECT num_identificacion, nom_usuario, clave_usuario, carg_usuario, sede_id  FROM public.solicitud_usuarios WHERE estadoReg = '" + "A' and num_identificacion = '" + username + "'"
    cur.execute(comando)
    print(comando)

    nombreUsuario = []

    for num_identificacion, nom_usuario, clave_usuario , carg_usuario,sede_id  in cur.fetchall():
        nombreUsuario.append({'num_identificacion': num_identificacion, 'nom_usuario': nom_usuario, 'clave_usuario' : clave_usuario, 'carg_usuario':carg_usuario,'sede_id':sede_id})

    print ("PASE 0")

    context['NombreUsuario'] = nombreUsuario[0]['nom_usuario']
    print ("PASE 1")

    print ("Asi quedo el nombre del usuario",  context['NombreUsuario'])
    miConexion.close()

    if nombreUsuario == []:

        context['Error'] = "Personal invalido y/o No Activo ! "
        print("Entre por personal No encontrado")

        return render(request, "accesoPrincipal.html", context)

        print("pase0")

    else:
        # Valido contraseña
        if nombreUsuario[0]['clave_usuario'] != contrasena:
            context['Error'] = "Contraseña invalida ! "
            return render(request, "accesoPrincipal.html", context)

        else:
            pass

            # Valido la Sede seleccinada

            miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                          password="BD_m3d1c4l")
            cur = miConexion.cursor()

            #comando = "SELECT num_identificacion  FROM public.solicitud_usuarios WHERE estadoReg='A' and num_identificacion = '" + username + "' and codreg_sede =  '"  + sedeSeleccionada + "'"
            comando = "SELECT num_identificacion,nom_sede  FROM public.solicitud_usuarios usu, public.solicitud_sedesCompra sedes WHERE usu.sede_id = sedes.id and usu.estadoReg='A' and usu.num_identificacion = '" + username + "' and sedes.codreg_sede =  '" + sedeSeleccionada + "'"
            print(comando)
            cur.execute(comando)

            permitido = []

            for num_identificacion, nom_sede in cur.fetchall():
                permitido.append({'num_identificacion': num_identificacion, 'nom_sede': nom_sede})

            miConexion.close()



            if permitido == []:

                context['Error'] = "Usuario no tiene autorizacion para la sede seleccionada y/o Reportes no asignados ! "
                return render(request, "accesoPrincipal.html", context)

            else:
                pass
                print("Paso Autenticacion")

    print("Asi quedo el nombre del usuario", context['NombreUsuario'])
    return render(request, "Reportes/cabeza.html", context)



def salir(request):
    print("Voy a salir Compras")

    context = {}
    # Sedes
    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()

    comando = 'SELECT codreg_sede, nom_sede FROM public.solicitud_sedesCompra'
    cur.execute(comando)
    print(comando)

    sedes = []

    for codreg_sede, nom_sede in cur.fetchall():
        sedes.append({'codreg_sede': codreg_sede, 'nom_sede': nom_sede})
    miConexion.close()

    context['Sedes'] = sedes
    print("Aqui estan las sedes")
    print(context['Sedes'])

    return render(request, "accesoPrincipal.html", context)


def Solicitudes(request , username, sedeSeleccionada, nombreUsuario, nombreSede):
    pass
    print ("Entre crear solicitudes");
    context = {}
    print("username = ", username)
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    #context['solicitudesForm'] = solicitudesForm
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede

    print("SedeSeleccionada = ", sedeSeleccionada)

    # Combo Areas

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")

    miConexion.set_client_encoding('LATIN1')
    cur = miConexion.cursor()
    cur.execute("set client_encoding='LATIN1';")
    comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    #Reemplazado
    #comando = "SELECT areas.codreg_area id ,areas.area  area FROM mae_areas areas, imhotep_sedes sedes WHERE areas.activo = 'S' and areas.sede = sedes.sede and sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    cur.execute(comando)
    print(comando)

    areas = []
    areas.append({'id': '', 'area': ''})

    for id, area in cur.fetchall():
        areas.append({'id': id, 'area': area})

    miConexion.close()

    context['Areas'] = areas

    # Fin Combo Areas

    # Combo descripcionescompra

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()
    cur = miConexion.cursor()

    comando = "SELECT t.id id, t.nombre  nombre FROM public.solicitud_descripcioncompra t where estadoReg='A'"
    cur.execute(comando)
    print(comando)

    descripcionescompra = []
    descripcionescompra.append({'id': '', 'nombre': ''})

    for id, nombre in cur.fetchall():
        descripcionescompra.append({'id': id, 'nombre': nombre})

    miConexion.close()
    print(descripcionescompra)

    context['Descripcionescompra'] = descripcionescompra

    # Fin combo descripcionescompra

    # Combo solicitud_tiposcompra

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()
    cur = miConexion.cursor()

    comando = "SELECT t.id id, t.nombre  nombre FROM public.solicitud_tiposcompra t where estadoReg='A'"
    cur.execute(comando)
    print(comando)

    tiposCompra = []
    tiposCompra.append({'id': '', 'nombre': ''})

    for id, nombre in cur.fetchall():
        tiposCompra.append({'id': id, 'nombre': nombre})

    miConexion.close()
    print(tiposCompra)

    context['TiposCompra'] = tiposCompra

    # Fin combo solicitud_presentacion

    # Combo solicitud_tiposcompra

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()

    comando = "SELECT t.id id, t.nombre  nombre FROM public.solicitud_presentacion t where estadoReg='A'"
    cur.execute(comando)
    print(comando)

    presentacion = []
    presentacion.append({'id': '', 'nombre': ''})

    for id, nombre in cur.fetchall():
        presentacion.append({'id': id, 'nombre': nombre})

    miConexion.close()
    print(presentacion)

    context['Presentacion'] = presentacion

    # Fin combo solicitud_presentacion

    # Combo productos


    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    miConexion.set_client_encoding('LATIN1')
    cur = miConexion.cursor()
    cur.execute("set client_encoding='LATIN1';")

    comando = "SELECT t.codreg_articulo codreg_articulo,  translate(btrim(t.articulo::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text)      articulo   FROM public.mae_articulos t order by t.articulo"
    cur.execute(comando)
    print(comando)

    articulos = []
    articulos.append({'id': '', 'nombre': ''})

    for codreg_articulo, articulo in cur.fetchall():
        articulos.append({'codreg_articulo': codreg_articulo, 'articulo': articulo})

    miConexion.close()
    print(articulos)

    context['Articulos'] = articulos

    # Fin combo Productos

    return render(request, "Reportes/Solicitudes.html", context)

def guardarSolicitudes(request, username,sedeSeleccionada,nombreUsuario,fecha,nombreSede,area):
    pass
    if request.method == 'POST':
        if request.is_ajax and request.method == "POST":
            print("Entre Ajax")
            username = request.POST["username"]
            nombreSede = request.POST["nombreSede"]
            nombreUsuario = request.POST["nombreUsuario"]
            fecha = request.POST["fecha"]
            area = request.POST["area"]
            estadoReg='A'


            print ("Entre solicitudes Respuesta")
            print(username)
            print (nombreSede)
            print(nombreUsuario)
            print(fecha)
            print(area)

            if (area==""):
                return HttpResponse('Favor ingresar el Area de envio . ' )

            # Consigo el id del usuario :

            miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                          password="BD_m3d1c4l")
            cur = miConexion.cursor()
            comando = "SELECT id,num_identificacion, nom_usuario FROM public.solicitud_usuarios WHERE estadoReg = '" + "A' and num_identificacion = '" + username + "'"
            cur.execute(comando)
            print(comando)

            Usuario = []

            for id, num_identificacion, nom_usuario in cur.fetchall():
                Usuario.append(
                    {'id': id, 'num_identificacion': num_identificacion, 'nom_usuario': nom_usuario})

            miConexion.close()

            usuarioId = Usuario[0]['id']
            print(usuarioId)

            miConexiont = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                          password="BD_m3d1c4l")
            curt = miConexiont.cursor()

            comando = "INSERT INTO solicitud_solicitudes (fecha , estadoReg , area_id, usuarios_id) VALUES ('" + str(
                fecha) + "', '" + str(estadoReg) + "',  '" + str(area) + "', '" + str(
                usuarioId)  + "') RETURNING id;"

            print(comando)
            resultado = curt.execute(comando)
            print("resultado =", resultado)
            n = curt.rowcount
            print("Registros commit = ", n)

            miConexiont.commit()
            solicitudId = curt.fetchone()[0]

            print("solicitudId = ", solicitudId)
            miConexiont.close()

            print("El id de solicitud es  ", solicitudId)

            # Fin grabacion Solictud de Compra


            # Grabacion Solicitud
            print ("Entre a ver detalle solicitud")
            Envio = request.POST["jsonDefSol1"]

            print ("Envio1 = ", Envio)

            JsonDicEnvio = json.loads(Envio)
            print("Diccionario Envio1 = ", JsonDicEnvio)



            # Voy a iterar
            campo = {}
            item = 1

            for x in range(0, len(JsonDicEnvio)):
                print(JsonDicEnvio[x])
                campo1 = JsonDicEnvio[x]
                campo = json.loads(campo1)
                print(campo['descripcion'])
                print(campo['tipo'])
                print(campo['producto'])
                print(campo['presentacion'])
                print(campo['cantidad'])
                print(campo['justificacion'])
                descripcion =  campo['descripcion']
                tipo = campo['tipo']
                producto = campo['producto']
                presentacion = campo['presentacion']
                cantidad = campo['cantidad']
                justificacion = campo['justificacion']
                producto = campo['producto']


                # Aqui obligo a ingresar informacion:

                # Aqui busco los id de cada cosa

                # Consigo Id username

                miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                cur = miConexion.cursor()
                comando = "SELECT id FROM public.solicitud_usuarios WHERE num_identificacion  = '" + username + "'"
                cur.execute(comando)
                print(comando)

                #usernameId = []
                usernameId = []

                for id in cur.fetchall():
                 usernameId.append({'id':id})
                   #usernameId['id'] = id

                miConexion.close()

                print ("V A L O R E S ")
                print (usernameId)
                print(usernameId[0])
                print(usernameId[0]['id'])
                #print(usernameId['id'])

                print("dato")
                for dato in usernameId:
                    print(dato)
                    print (dato['id'])
                    print(json.dumps(dato['id']))
                    usuario1 = json.dumps(dato['id'])

                print("usuario1 = ", usuario1)
                usuario1 = usuario1.replace('[','')
                usuario1 = usuario1.replace(']', '')
                print("usuario1 = ", usuario1)


                # Fin  Consigo Id username

                # Consigo Id descripcion

                miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                cur = miConexion.cursor()
                comando = "SELECT id FROM public.solicitud_descripcioncompra WHERE nombre  = '" + descripcion + "'"
                cur.execute(comando)
                print(comando)

                descripcionId = []

                for id in cur.fetchall():
                    descripcionId.append({'id': id})

                miConexion.close()

                print("dato")
                for dato in descripcionId:
                    print(dato)
                    print(dato['id'])
                    print(json.dumps(dato['id']))
                    descripcion1 = json.dumps(dato['id'])

                print("descripcionId = ", descripcionId)
                descripcion1 = descripcion1.replace('[', '')
                descripcion1 = descripcion1.replace(']', '')
                print("descripcion1 = ", descripcion1)

                # Fin  Consigo Id descripcion

                # Consigo Id tiposcomra

                miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                cur = miConexion.cursor()
                comando = "SELECT id FROM public.solicitud_tiposcompra WHERE nombre  = '" + tipo + "'"
                cur.execute(comando)
                print(comando)

                tipoId = []

                for id in cur.fetchall():
                    tipoId.append({'id': id})

                miConexion.close()

                print("dato")
                for dato in tipoId:
                    print(dato)
                    print(dato['id'])
                    print(json.dumps(dato['id']))
                    tipo1 = json.dumps(dato['id'])

                print("tipo1 = ", tipo1)
                tipo1 = tipo1.replace('[', '')
                tipo1 = tipo1.replace(']', '')
                print("tipo1 = ", tipo1)

                # Fin  Consigo Id tiposcomra

                # Consigo Id presentacion

                miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                cur = miConexion.cursor()
                comando = "SELECT id FROM public.solicitud_presentacion WHERE nombre  = '" + presentacion + "'"
                cur.execute(comando)
                print(comando)

                presentacionId = []

                for id in cur.fetchall():
                    presentacionId.append({'id': id})

                miConexion.close()

                print("dato")
                for dato in presentacionId:
                    print(dato)
                    print(dato['id'])
                    print(json.dumps(dato['id']))
                    presentacion1 = json.dumps(dato['id'])

                print("presentacion1 = ", presentacion1)
                presentacion1 = presentacion1.replace('[', '')
                presentacion1 = presentacion1.replace(']', '')

                print("presentacion1 DEFINITIVA = ", presentacion1)

                # Fin  Consigo Id presentacion

                ### Aqui fion busca Id pensientes

                miConexionu = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                curu = miConexionu.cursor()

                #comando = "INSERT INTO solicitud_solicitudesdetalle ( item ,  cantidad ,  justificacion ,  'especificacionesTecnicas' ,  'especificacionesAlmacen' ,  'especificacionesCompras' ,  estadoreg ,             descripcion_id, 'estadosAlmacen_id', 'estadosCompras_id', 'estadosSolicitud_id', 'estadosValidacion_id', solicitud_id, 'tiposCompra_id', 'usuarioResponsableValidacion_id', 'entregadoAlmacen', presentacion_id, 'solicitadoAlmacen' )         VALUES(" + str(item) + ", " + str(cantidad) + ", '" + str(justificacion) + "', '', '', '', 'A', " + descripcion1 + ", 1, 1, 1, 1, " + solicitudId + ", " + tipo1 + "," + usuario1 + ",0," + presentacion1+ ", 0)"
                comando = 'INSERT INTO solicitud_solicitudesdetalle ( item ,  cantidad ,  justificacion ,  "especificacionesTecnicas" ,  "especificacionesAlmacen" ,  "especificacionesCompras" ,  estadoreg ,             descripcion_id, "estadosAlmacen_id", "estadosCompras_id", "estadosSolicitud_id", "estadosValidacion_id", solicitud_id, "tiposCompra_id", "usuarioResponsableValidacion_id", "entregadoAlmacen", presentacion_id, "solicitadoAlmacen", producto,"usuarioResponsableAlmacen_id","usuarioResponsableCompra_id" ,iva, "recibidoOrdenCantidad","recibidoOrdenValor", "solicitadoOrdenCantidad", "solicitadoOrdenValor", "valorUnitario" )  VALUES(' + str(item) + ', ' + str(cantidad) + ',' + "'" + str(justificacion) + "'" + ",''," + "''" + ",'',"  + "'A'" + ','  + str(descripcion1) + ', 1, 1, 1, 1, ' + str(solicitudId) + ', ' + str(tipo1) + ',' + str(usuario1) + ',0,' + str(presentacion1) + ', 0,' + "'" + str(producto) + "'"  + ',1,1,0,0,0,0,0,0 '    +  '  )'
                print(comando)
                curu.execute(comando)
                miConexionu.commit()
                item=item+1
                miConexionu.close()

            # Fin Rutina Grabacion del detalle de la solicitud

    #Rutina envia correo electonico:


    #remitente = "adminbd@outlook.com"
    print("Entre correo1")
    remitente = "adminbd@clinicamedical.com.co"
    destinatario = "alberto_bernalf@yahoo.com.co"
    mensaje = "Pruebas solicitudes"
    email = EmailMessage()
    print("Entre correo2")
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = "Correo de prueba"
    email.set_content(mensaje)
    print("Entre correo3")
    #smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp = smtplib.SMTP("smtp.office365.com", port=587)
    smtp.starttls()
    print("Entre correo3.5")
    #smtp.login(remitente, "75AAbb??")
    #print("Entre correo4")
    #smtp.sendmail(remitente, destinatario, email.as_string())
    #print ("Correo Enviado")
    #smtp.quit()
    ## fin rutina correo electronico
    #print("salid de Correo Enviado")

    return HttpResponse('Solicitud creada No ' + str(solicitudId))

    #debe habes un POST



def ValidacionConsulta(request , username, sedeSeleccionada, nombreUsuario, nombreSede):
    pass
    print ("Entre a consulta solicitud a validar");
    context = {}

    print("username = ", username)
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['solicitudesForm'] = solicitudesForm
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()
    comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    #Reemplazado
    #comando = "SELECT areas.codreg_area id ,areas.area  area FROM mae_areas areas, imhotep_sedes sedes WHERE areas.activo = 'S' and areas.sede = sedes.sede and sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    cur.execute(comando)
    print(comando)

    areas = []

    for id, area in cur.fetchall():
        areas.append({'id': id, 'area': area})

    miConexion.close()

    context['Areas'] = areas

    return render(request, "Reportes/ValidacionConsulta.html", context)


## Desde Aqui codigo para Consultas Solicitud


def SolicitudesConsulta(request, username, sedeSeleccionada, nombreUsuario, nombreSede):

    context = {}
    print ("username = " , username )

    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede



    print ("Entre Consulta solicitudes")


    return render(request, 'Reportes\SolicitudesConsulta.html', context )



def load_dataSolicitudesConsulta(request, data):
    print("Entre DE VERDAD load_dataSolicitudesConsulta ")

    #data = request.GET['data']
    print ("data = ", data)
    d = json.loads(data)
    desdeFechaSolicitud = d['desdeFechaSolicitud']
    hastaFechaSolicitud = d['hastaFechaSolicitud']

    username = d['username']
    nombreSede = d['nombreSede']
    nombreUsuario = d['nombreUsuario']
    sedeSeleccionada = d['sedeSeleccionada']
    solicitudId = d['solicitudId']

    print("desdeFechaSolicitud = ", d['desdeFechaSolicitud'])
    print("hastaFechaSolicitud = ", d['hastaFechaSolicitud'])
    print("voy a context0")
    # Ahora SolicitudDetalle
    print("voy a context1")
    context = {}
    print ("pase contex2")

    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede
    context['solicitudId'] = solicitudId
    context['desdeFechaSolicitud'] = desdeFechaSolicitud
    context['hastaFechaSolicitud'] = hastaFechaSolicitud

    # Abro Conexion

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres", password="BD_m3d1c4l")
    # cur = miConexion.cursor()

    miConexion.set_client_encoding('LATIN1')
    cur = miConexion.cursor()
    cur.execute("set client_encoding='LATIN1';")
    print("voy comando")
    comando = 'SELECT sol.id id,substring(to_char(sol0.fecha,' + "'" + 'yyyy-mm-dd' + "'" + '),1,10)  fecha,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec, est.nombre estValidacion, sol."estadosValidacion_id" estadosValidacion_id , usu.nom_usuario usuSolicitud FROM public.solicitud_solicitudes sol0, public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_estadosvalidacion est      WHERE sol0.fecha >= ' + "'" + desdeFechaSolicitud + "'" + ' and sol0.fecha <= ' + "'"  + hastaFechaSolicitud + "'" + '  and sol0.id = sol.solicitud_id and des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu.id = sol0."usuarios_id" and est.id = sol."estadosValidacion_id"  ORDER BY sol0.fecha, sol.item'
    print("pase comando")
    cur.execute(comando)
    print(comando)

    solicitudDetalle = []

    for id, fecha, item, descripcion_id, descripcion, tipo, producto, nombre_producto, presentacion, cantidad, justificacion, tec, estValidacion, estadosValidacion_id, usuSolicitud in cur.fetchall():
        solicitudDetalle.append(
            {"model": "solicitud.solicitudesdetalle", "pk": id, "fields":
                {"id": id, "fecha":fecha, "item": item, "'descripcion_id": descripcion_id, "descripcion": descripcion,
                  "tiposCompra": tipo,
                "producto": producto, "nombre_producto": nombre_producto,
                "presentacion": presentacion, "cantidad": cantidad, "justificacion": justificacion,
             "especificacionesTecnicas": tec,
             "estadosValidacion": estValidacion, "estadosValidacion_id": estadosValidacion_id,
             "usuSolicitud": usuSolicitud}})

    miConexion.close()
    print("solicitudDetalle")
    print(solicitudDetalle)

    # Cierro Conexion

    context['SolicitudDetalle'] = solicitudDetalle

    ## Voy a enviar estadosSolicitudes

    # estadosvalidacionList = EstadosValidacion.objects.all()

    # json1 = serializers.serialize('json', estadosvalidacionList)
    serialized1 = json.dumps(solicitudDetalle)

    print("Envio = ", json)

    return HttpResponse(serialized1, content_type='application/json')

class PostStoreSolicitudesConsulta(TemplateView):
        form_class = solicitudesDetalleForm
        template_name = 'Reportes/SolicitudesConsultaTrae.html'

        def post(self, request):
            print("Entre a post de SolicitudesConsultas")

            context = {}

            return JsonResponse({'success': True, 'message': 'Solicitud Detalle Created Successfully!'})

        def get_context_data(self, **kwargs):
            print("ENTRE POR EL GET_CONTEXT DEL VIEW de PostStoreSolicitudesConsulta : ")
            #solicitudId = self.request.GET["solicitudId"]

            username = self.request.GET['username']

            sedeSeleccionada = self.request.GET["sedeSeleccionada"]
            nombreUsuario = self.request.GET["nombreUsuario"]
            nombreSede = self.request.GET["nombreSede"]

            #print("SolictudId =", solicitudId)
            #print("username =", username)
            #print("sedeSeleccionada =", sedeSeleccionada)
            #print("nombreUsuario =", nombreUsuario)
            #print("nombreSede =", nombreSede)

            # context = super(PostStore, self).get_context_data(**kwargs)
            context = super().get_context_data(**kwargs)

            context['Username'] = username
            context['SedeSeleccionada'] = sedeSeleccionada
            context['NombreUsuario'] = nombreUsuario
            context['NombreSede'] = nombreSede
            #context['SolicitudId'] = solicitudId
            desdeFechaSolicitud = self.request.GET['desdeFechaSolicitud']
            hastaFechaSolicitud = self.request.GET['hastaFechaSolicitud']

            print("desdeFechaSolicitud = ", desdeFechaSolicitud)
            print("hastaFechaSolicitud = ", hastaFechaSolicitud)

            context['DesdeFechaSolicitud'] = desdeFechaSolicitud
            context['HastaFechaSolicitud'] = hastaFechaSolicitud

            return context

    ## Fin Desde Aqui codigo para Consultas Solicitud


# Create your views here.
def load_dataValidacion(request, solicitudId):
    print ("Entre load_data")
    print("solicitudId = ",solicitudId)

    #print("data = ", request.GET('data'))

    solicitudesDetalleList = SolicitudesDetalle.objects.all().filter(solicitud_id=solicitudId)

    # Ahora SolicitudDetalle
    context= {}

    # Abro Conexion

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    # cur = miConexion.cursor()

    miConexion.set_client_encoding('LATIN1')
    cur = miConexion.cursor()
    cur.execute("set client_encoding='LATIN1';")

    # comando = "SELECT sol.id id, sol.fecha fecha, sol.estadoReg estadoReg,sol.usuarios_id usuarioId , usu.nom_usuario nom_usuario, area.area nom_area, sede.nom_sede  nom_sede FROM public.solicitud_solicitudes sol ,public.solicitud_areas area , public.solicitud_sedesCompra sede, public.solicitud_usuarios usu WHERE sol.id = " + solicitudId + " AND area.id = sol.area_id and area.sede_id = sede.id and sol.usuarios_id = usu.id"
    comando = 'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec,usu.nom_usuario usuResp  , est.nombre estValidacion, sol."estadosValidacion_id" estadosValidacion_id  FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_estadosvalidacion est  WHERE sol.solicitud_id = ' + solicitudId + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu.id = sol."usuarioResponsableValidacion_id" and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
    cur.execute(comando)
    print(comando)

    solicitudDetalle = []
    #solicitudDetalle.append({"model":"solicitud.solicitudesdetalle"})

    for id, item, descripcion_id, descripcion, tipo, producto, nombre_producto, presentacion, cantidad, justificacion, tec, usuResp, estValidacion, estadosValidacion_id in cur.fetchall():
        solicitudDetalle.append(
            {"model":"solicitud.solicitudesdetalle","pk":id,"fields":
            {"id": id, "item": item, "'descripcion_id": descripcion_id, "descripcion": descripcion, "tiposCompra": tipo,
             "producto": producto,"nombre_producto": nombre_producto,
             "presentacion": presentacion, "cantidad": cantidad, "justificacion": justificacion, "especificacionesTecnicas": tec,
             "usuarioResponsableValidacion": usuResp, "estadosValidacion": estValidacion, "estadosValidacion_id": estadosValidacion_id}})

    miConexion.close()
    print("solicitudDetalle")
    print(solicitudDetalle)

    # Cierro Conexion

    #{"model": "solicitud.solicitudesdetalle", "pk": 6, "fields":

    context['SolicitudDetalle'] = solicitudDetalle

    ## Voy a enviar estadosSolicitudes

    #estadosvalidacionList = EstadosValidacion.objects.all()

    #json1 = serializers.serialize('json', estadosvalidacionList)
    serialized1 = json.dumps(solicitudDetalle)

    print ("Envio = ", json)

    return HttpResponse(serialized1, content_type='application/json')


class PostStoreValidacion(TemplateView):
    form_class = solicitudesDetalleForm
    template_name = 'Reportes/ValidacionTrae.html'

    def post(self, request):
        print ("Entre a Grabar")

        context = {}

        print("OPS Entre pos POST DEL VIEW")

        username = request.POST["username"]
        nombreSede = request.POST["nombreSede"]
        nombreUsuario = request.POST["nombreUsuario"]
        sedeSeleccionada = request.POST["sedeSeleccionada"]
        solicitudId = request.POST["solicitudId"]

        context['Username'] = username
        context['SedeSeleccionada'] = sedeSeleccionada
        context['NombreUsuario'] = nombreUsuario
        context['NombreSede'] = nombreSede
        context['solicitudId'] = solicitudId

        print ("CONTEXTO solicitudId", solicitudId)

        form = self.form_class(request.POST)

        data = {'error': form.errors}
        print ("DATA MALUCA = ", data)

        if form.is_valid():
            try:
                print ("Entre forma valida")

                estadosValidacionAct = request.POST.get('estadosValidacion')
                especificacionesTecnicasAct = request.POST.get('especificacionesTecnicas')

                ## AVERIGUAMOS EL ID DEL USUARIO

                miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                cur = miConexion.cursor()

                comando = "SELECT id idActual FROM solicitud_usuarios WHERE num_identificacion = '" + str(username) + "'"
                print(comando)
                cur.execute(comando)
                idActualActual = []

                for idActual in cur.fetchall():
                    idActualActual.append({'idActual': idActual})

                print("idActual =", idActual)

                for dato in idActualActual:
                    print(dato)
                    print(dato['idActual'])
                    print(json.dumps(dato['idActual']))
                    idActual = json.dumps(dato['idActual'])

                idActual = idActual.replace('[', '')
                idActual = idActual.replace(']', '')
                print("idActual FINAL = ", idActual)

                miConexion.close()

                ## FIN AVERIGIAMOS ID DE USUARIO
                usuarioResponsableValidacion_idAct = idActual

                print ("estadosValidacionAct = ",estadosValidacionAct )
                print("especificacionesTecnicasAct = ", especificacionesTecnicasAct)
                print("usuarioResponsableValidacion_idAct = ", usuarioResponsableValidacion_idAct)
                pk = request.POST.get('pk')
                print("pk = ", pk)

                obj = get_object_or_404(SolicitudesDetalle, id=request.POST.get('pk'))
                estadosValidacionAnt = obj.estadosValidacion
                especificacionesTecnicasAnt = obj.especificacionesTecnicas
                usuarioResponsableValidacion_idAnt = obj.usuarioResponsableValidacion_id

                if (str(especificacionesTecnicasAnt) != str(especificacionesTecnicasAct) or str(estadosValidacionAnt) != str(estadosValidacionAct)):

                    obj.estadosValidacion = EstadosValidacion.objects.get(id=estadosValidacionAct)
                    obj.especificacionesTecnicas=especificacionesTecnicasAct
                    obj.usuarioResponsableValidacion_id = usuarioResponsableValidacion_idAct
                    obj.save()

                return JsonResponse({'success': True, 'message': 'Solicitud Detalle Updated Successfully!'})
            except:
                if (str(especificacionesTecnicasAnt) != str(especificacionesTecnicasAct) or str(estadosValidacionAnt) != str(estadosValidacionAct)):

                    obj.estadosValidacion = EstadosValidacion.objects.get(id=estadosValidacionAct)
                    obj.especificacionesTecnicas=especificacionesTecnicasAct
                    obj.usuarioResponsableValidacion_id = usuarioResponsableValidacion_idAct
                    obj.save()

                return JsonResponse({'success': True, 'message': 'Solicitud Detalle Created Successfully!'})
        else:
            return JsonResponse({'error': True, 'error': form.errors})
        return render(request, self.template_name,{'data':data})

    def get_context_data(self, **kwargs):
        print("ENTRE POR EL GET_CONTEXT DEL VIEW")
        solicitudId = self.request.GET["solicitudId"]
        username = self.request.GET["username"]
        sedeSeleccionada = self.request.GET["sedeSeleccionada"]
        nombreUsuario = self.request.GET["nombreUsuario"]
        nombreSede = self.request.GET["nombreSede"]

        print("SolictudId =", solicitudId)
        print("username =", username)
        print("sedeSeleccionada =", sedeSeleccionada)
        print("nombreUsuario =", nombreUsuario)
        print("nombreSede =", nombreSede)


        #context = super(PostStore, self).get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)

        context['Username'] = username
        context['SedeSeleccionada'] = sedeSeleccionada
        context['NombreUsuario'] = nombreUsuario
        context['NombreSede'] = nombreSede
        context['SolicitudId'] = solicitudId

        #DESDE AQUIP

        # Buscamos estadosValidacion

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosValidacion = []

        for id, nombre in cur.fetchall():
            estadosValidacion.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosValidacion")
        print(estadosValidacion)

        context['EstadosValidacion'] = estadosValidacion

        # Fin buscamos estdos validacion



        # Buscamos la solicitud

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()
        # Pendiente de reemplazo
        comando = "SELECT sol.id id, to_char(sol.fecha, 'YYYY-MM-DD HH:MM.SS')  fecha, sol.estadoReg estadoReg,sol.usuarios_id usuarioId , usu.nom_usuario nom_usuario, area.area nom_area, sede.nom_sede  nom_sede FROM public.solicitud_solicitudes sol ,public.solicitud_areas area , public.solicitud_sedesCompra sede, public.solicitud_usuarios usu WHERE sol.id = " + solicitudId + " AND area.id = sol.area_id and area.sede_id = sede.id and sol.usuarios_id = usu.id"
        cur.execute(comando)
        print(comando)

        solicitud = []

        for id, fecha, estadoReg, usuarioId, nom_usuario, nom_area, nom_sede in cur.fetchall():
            solicitud.append(
                {'id': id, 'fecha': fecha, 'estadoReg': estadoReg, 'usuarioId': usuarioId, 'nom_usuario': nom_usuario,
                 'nom_area': nom_area, 'nom_sede': nom_sede})

        miConexion.close()
        print("solicitud")
        print(solicitud)

        context['Solicitud'] = solicitud

        # Ahora SolicitudDetalle
        # Fin SolicitudDetalle
        if (solicitud == []):
            print("Entre por No existe")
            context['Error'] = 'Solicitud No Existe '
            miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                          password="BD_m3d1c4l")

            miConexion.set_client_encoding('LATIN1')
            cur = miConexion.cursor()
            cur.execute("set client_encoding='LATIN1';")
            comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
            cur.execute(comando)
            print(comando)
            areas = []
            areas.append({'id': '', 'area': ''})

            for id, area in cur.fetchall():
                areas.append({'id': id, 'area': area})

            miConexion.close()

            context['Areas'] = areas

            print ("No encontre data")

            #return HttpResponse(context, content_type='application/json')
            #return JsonResponse(context)
            #return render(self.request, "Reportes/ValidacionConsulta.html", {'ERROR':'Solicitud No Existe'})
            return context
        else:
            return context


        #HASTA AQUIP


def post_editValidacion(request,id,username,sedeSeleccionada,nombreUsuario,nombreSede,solicitudId):
    print ("Entre POST edit")
    print ("id = " , id)

    print ("username =" , username)
    print("sedeSeleccionada =", sedeSeleccionada)
    print("nombreUsuario =", nombreUsuario)
    print("nombreSede =", nombreSede)
    print("solicitudId =", solicitudId)

    context = {}
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede
    context['solicitudId'] = solicitudId



    if request.method == 'GET':

        #solicitudesDetalle = SolicitudesDetalle.objects.filter(id=id).first()

        # Abro Conexion

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        # cur = miConexion.cursor()

        miConexion.set_client_encoding('LATIN1')
        cur = miConexion.cursor()
        cur.execute("set client_encoding='LATIN1';")


        comando = 'SELECT sol.id id,sol.item item, sol.descripcion_id descripcion_id, des.nombre descripcion,sol."tiposCompra_id" tiposCompra_id, tip.nombre tipo , sol.producto producto, substring(art.articulo,1,150) nombre_producto ,sol.presentacion_id  presentacion_id, pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec, sol."usuarioResponsableValidacion_id" usuarioResponsableValidacion_id,  usu.nom_usuario usuResp  , est.nombre estValidacion, sol."estadosValidacion_id" estadosValidacion_id  FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_estadosvalidacion est  WHERE sol.id = ' + str(id) + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu.id = sol."usuarioResponsableValidacion_id" and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
        cur.execute(comando)
        print(comando)

        solicitudDetalle = []
        # solicitudDetalle.append({"model":"solicitud.solicitudesdetalle"})

        for id, item, descripcion_id, descripcion, tiposCompra_id, tipo, producto,nombre_producto, presentacion_id , presentacion, cantidad, justificacion, tec,usuarioResponsableValidacion_id, usuResp, estValidacion, estadosValidacion_id in cur.fetchall():
            solicitudDetalle.append(
                {
                    #"model": "solicitud.solicitudesdetalle", "pk": id, "fields": {
                     "id": id, "item": item, "descripcion_id": descripcion_id, "descripcion": descripcion,
                    "tiposCompra_id": tiposCompra_id, "tiposCompra": tipo,
                     "producto": producto,"nombre_producto": nombre_producto,
                    "presentacion_id": presentacion_id,
                     "presentacion": presentacion, "cantidad": cantidad, "justificacion": justificacion,
                     "especificacionesTecnicas": tec,
                    "usuarioResponsableValidacion_id": usuarioResponsableValidacion_id,
                     "usuarioResponsableValidacion": usuResp, "estadosValidacion": estValidacion,
                     "estadosValidacion_id": estadosValidacion_id#}
                })

        miConexion.close()
        print("solicitudDetalle")
        print(solicitudDetalle)

        # Cierro Conexion


        print ("Me devuelvo a la MODAL")

        return JsonResponse({'pk':solicitudDetalle[0]['id'],'item':solicitudDetalle[0]['item'],
                             'descripcion_id': solicitudDetalle[0]['descripcion_id'],
                             'descripcion':solicitudDetalle[0]['descripcion'],'tiposCompra_id':solicitudDetalle[0]['tiposCompra_id'], 'tiposCompra':solicitudDetalle[0]['tiposCompra'],
                             'producto':solicitudDetalle[0]['producto'],
                             'nombre_producto': solicitudDetalle[0]['nombre_producto'],
                             'presentacion_id': solicitudDetalle[0]['presentacion_id'],
                             'presentacion':solicitudDetalle[0]['presentacion'],
                             'cantidad':solicitudDetalle[0]['cantidad'],'justificacion':solicitudDetalle[0]['justificacion'],
                             'especificacionesTecnicas':solicitudDetalle[0]['especificacionesTecnicas'],
                             'usuarioResponsableValidacion_id': solicitudDetalle[0]['usuarioResponsableValidacion_id'],
                             'usuarioResponsableValidacion':solicitudDetalle[0]['usuarioResponsableValidacion'],
                             'estadosValidacion':solicitudDetalle[0]['estadosValidacion'],'estadosValidacion_id': solicitudDetalle[0]['estadosValidacion_id'] })
    else:
        return JsonResponse({'errors':'Something went wrong!'})

def post_deleteValidacion(request,id):
    print ("Entre a borrar")
    solicitudesDetalle = SolicitudesDetalle.objects.get(id=id)
    solicitudesDetalle.delete()
    return HttpResponseRedirect(reverse('index'))

# Fin Create your views here. para validacion


# Create your views here. para Almacen
def AlmacenConsulta(request , username, sedeSeleccionada, nombreUsuario, nombreSede) :
    pass
    print("Entre a consulta Solicitudes a Almacen");
    context = {}

    print("username = ", username)
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['solicitudesForm'] = solicitudesForm
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_imhotep", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()
    comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    # Reemplazado
    # comando = "SELECT areas.codreg_area id ,areas.area  area FROM mae_areas areas, imhotep_sedes sedes WHERE areas.activo = 'S' and areas.sede = sedes.sede and sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    cur.execute(comando)
    print(comando)

    areas = []

    for id, area in cur.fetchall():
        areas.append({'id': id, 'area': area})

    miConexion.close()

    context['Areas'] = areas

    return render(request, "Reportes/AlmacenConsulta.html", context)


class PostStoreAlmacen(TemplateView):
    form_class = solicitudesDetalleForm
    template_name = 'Reportes/AlmacenTrae.html'

    def post(self, request):
        print ("Entre a Grabar almacen")

        context = {}

        print("OPS Entre pos POST DEL VIEW")

        username = request.POST["username"]
        nombreSede = request.POST["nombreSede"]
        nombreUsuario = request.POST["nombreUsuario"]
        sedeSeleccionada = request.POST["sedeSeleccionada"]
        solicitudId = request.POST["solicitudId"]

        context['Username'] = username
        context['SedeSeleccionada'] = sedeSeleccionada
        context['NombreUsuario'] = nombreUsuario
        context['NombreSede'] = nombreSede
        context['solicitudId'] = solicitudId

        print ("CONTEXTO solicitudId", solicitudId)

        form = self.form_class(request.POST)

        data = {'error': form.errors}
        print ("DATA MALUCA = ", data)

        if form.is_valid():
            try:
                print ("Entre forma valida")

                estadosAlmacenAct = request.POST.get('estadosAlmacen')
                especificacionesAlmacenAct = request.POST.get('especificacionesAlmacen')

                ## AVERIGUAMOS EL ID DEL USUARIO

                miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                cur = miConexion.cursor()

                comando = "SELECT id idActual FROM solicitud_usuarios WHERE num_identificacion = '" + str(username) + "'"
                print(comando)
                cur.execute(comando)
                idActualActual = []

                for idActual in cur.fetchall():
                    idActualActual.append({'idActual': idActual})

                print("idActual =", idActual)

                for dato in idActualActual:
                    print(dato)
                    print(dato['idActual'])
                    print(json.dumps(dato['idActual']))
                    idActual = json.dumps(dato['idActual'])

                idActual = idActual.replace('[', '')
                idActual = idActual.replace(']', '')
                print("idActual FINAL = ", idActual)

                miConexion.close()

                ## FIN AVERIGIAMOS ID DE USUARIO
                usuAlmacenAct = idActual

                print ("estadosAlmacenAct = ",estadosAlmacenAct )
                print("especificacionesAlmacenAct = ", especificacionesAlmacenAct)
                print("usuAlmacenAct = ", usuAlmacenAct)
                pk = request.POST.get('pk')
                print("pk = ", pk)

                obj = get_object_or_404(SolicitudesDetalle, id=request.POST.get('pk'))
                estadosAlmacenAnt = obj.estadosAlmacen
                especificacionesAlmacenAnt = obj.especificacionesAlmacen
                usuAlmacenAnt = obj.usuarioResponsableAlmacen_id

                if (str(especificacionesAlmacenAnt) != str(especificacionesAlmacenAct) or str(estadosAlmacenAnt) != str(estadosAlmacenAct)):

                    obj.estadosAlmacen_id = EstadosValidacion.objects.get(id=estadosAlmacenAct)
                    obj.especificacionesAlmacen=especificacionesAlmacenAct
                    obj.usuarioResponsableAlmacen_id = usuAlmacenAct
                    obj.save()

                return JsonResponse({'success': True, 'message': 'Solicitud Detalle Updated Successfully!'})
            except:
                if (str(especificacionesTecnicasAnt) != str(especificacionesTecnicasAct) or str(estadosValidacionAnt) != str(estadosValidacionAct)):
                    obj.estadosAlmacen_id = EstadosValidacion.objects.get(id=estadosAlmacenAct)
                    obj.especificacionesAlmacen = especificacionesAlmacenAct
                    obj.usuarioResponsableAlmacen_id = usuAlmacenAct
                    obj.save()

                return JsonResponse({'success': True, 'message': 'Solicitud Detalle Created Successfully!'})
        else:
            return JsonResponse({'error': True, 'error': form.errors})
        return render(request, self.template_name,{'data':data})

    def get_context_data(self, **kwargs):
        print("ENTRE POR EL GET_CONTEXT DEL VIEW")
        solicitudId = self.request.GET["solicitudId"]
        username = self.request.GET["username"]
        sedeSeleccionada = self.request.GET["sedeSeleccionada"]
        nombreUsuario = self.request.GET["nombreUsuario"]
        nombreSede = self.request.GET["nombreSede"]

        print("SolictudId =", solicitudId)
        print("username =", username)
        print("sedeSeleccionada =", sedeSeleccionada)
        print("nombreUsuario =", nombreUsuario)
        print("nombreSede =", nombreSede)


        #context = super(PostStore, self).get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)

        context['Username'] = username
        context['SedeSeleccionada'] = sedeSeleccionada
        context['NombreUsuario'] = nombreUsuario
        context['NombreSede'] = nombreSede
        context['SolicitudId'] = solicitudId

        #DESDE AQUIP

        # Buscamos estadosValidacion

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosValidacion = []

        for id, nombre in cur.fetchall():
            estadosValidacion.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosValidacion")
        print(estadosValidacion)

        context['EstadosValidacion'] = estadosValidacion

        # Fin buscamos estdos validacion

        # Buscamos estadosAlmacen

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosAlmacen = []

        for id, nombre in cur.fetchall():
            estadosAlmacen.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosAlmacen")
        print(estadosAlmacen)

        context['EstadosAlmacen'] = estadosAlmacen

        # Fin buscamos estados Almacen



        # Buscamos la solicitud

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()
        # Pendiente de reemplazo
        comando = "SELECT sol.id id, to_char(sol.fecha, 'YYYY-MM-DD HH:MM.SS')  fecha, sol.estadoReg estadoReg,sol.usuarios_id usuarioId , usu.nom_usuario nom_usuario, area.area nom_area, sede.nom_sede  nom_sede FROM public.solicitud_solicitudes sol ,public.solicitud_areas area , public.solicitud_sedesCompra sede, public.solicitud_usuarios usu WHERE sol.id = " + solicitudId + " AND area.id = sol.area_id and area.sede_id = sede.id and sol.usuarios_id = usu.id"
        cur.execute(comando)
        print(comando)

        solicitud = []

        for id, fecha, estadoReg, usuarioId, nom_usuario, nom_area, nom_sede in cur.fetchall():
            solicitud.append(
                {'id': id, 'fecha': fecha, 'estadoReg': estadoReg, 'usuarioId': usuarioId, 'nom_usuario': nom_usuario,
                 'nom_area': nom_area, 'nom_sede': nom_sede})

        miConexion.close()
        print("solicitud")
        print(solicitud)

        context['Solicitud'] = solicitud

        # Ahora SolicitudDetalle
        # Fin SolicitudDetalle
        if (solicitud == []):
            print("Entre por No existe")
            context['Error'] = 'Solicitud No Existe '
            miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                          password="BD_m3d1c4l")

            miConexion.set_client_encoding('LATIN1')
            cur = miConexion.cursor()
            cur.execute("set client_encoding='LATIN1';")
            comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
            cur.execute(comando)
            print(comando)
            areas = []
            areas.append({'id': '', 'area': ''})

            for id, area in cur.fetchall():
                areas.append({'id': id, 'area': area})

            miConexion.close()

            context['Areas'] = areas

            print ("No encontre data")

            #return HttpResponse(context, content_type='application/json')
            #return JsonResponse(context)
            #return render(self.request, "Reportes/ValidacionConsulta.html", {'ERROR':'Solicitud No Existe'})
            return context
        else:
            return context


        #HASTA AQUIP class PostStoreAlmacen

def load_dataAlmacen(request, solicitudId):
    print ("Entre load_data")
    print("solicitudId = ",solicitudId)

    #print("data = ", request.GET('data'))

    solicitudesDetalleList = SolicitudesDetalle.objects.all().filter(solicitud_id=solicitudId)

    # Ahora SolicitudDetalle
    context= {}

    # Abro Conexion

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    # cur = miConexion.cursor()

    miConexion.set_client_encoding('LATIN1')
    cur = miConexion.cursor()
    cur.execute("set client_encoding='LATIN1';")

    # comando = "SELECT sol.id id, sol.fecha fecha, sol.estadoReg estadoReg,sol.usuarios_id usuarioId , usu.nom_usuario nom_usuario, area.area nom_area, sede.nom_sede  nom_sede FROM public.solicitud_solicitudes sol ,public.solicitud_areas area , public.solicitud_sedesCompra sede, public.solicitud_usuarios usu WHERE sol.id = " + solicitudId + " AND area.id = sol.area_id and area.sede_id = sede.id and sol.usuarios_id = usu.id"
    #comando = 'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec,usu.nom_usuario usuResp  , est.nombre estValidacion, sol."estadosValidacion_id" estadosValidacion_id  FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_estadosvalidacion est  WHERE sol.solicitud_id = ' + solicitudId + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu.id = sol."usuarioResponsableValidacion_id" and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
    comando =  'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec,usu.nom_usuario usuResp  , est.nombre estValidacion,est1.nombre estadosAlmacen, sol."estadosValidacion_id" estadosValidacion_id, sol."especificacionesAlmacen" especificacionesAlmacen, sol."estadosAlmacen_id" estadosAlmacen_id ,   usu1.nom_usuario usuAlmacen FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_estadosvalidacion est , public.solicitud_estadosvalidacion est1  WHERE sol.solicitud_id = ' + solicitudId + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id" and est.id = sol."estadosValidacion_id" ORDER BY sol.item'

    cur.execute(comando)
    print(comando)

    solicitudDetalle = []
    #solicitudDetalle.append({"model":"solicitud.solicitudesdetalle"})

    for id, item, descripcion_id, descripcion, tipo, producto, nombre_producto, presentacion, cantidad, justificacion, tec, usuResp, estValidacion, estadosAlmacen, estadosValidacion_id, especificacionesAlmacen, estadosAlmacen_id , usuAlmacen  in cur.fetchall():
        solicitudDetalle.append(
            {"model":"solicitud.solicitudesdetalle","pk":id,"fields":
            {"id": id, "item": item, "'descripcion_id": descripcion_id, "descripcion": descripcion, "tiposCompra": tipo,
             "producto": producto,"nombre_producto": nombre_producto,
             "presentacion": presentacion, "cantidad": cantidad, "justificacion": justificacion, "especificacionesTecnicas": tec,
             "usuarioResponsableValidacion": usuResp, "estadosValidacion": estValidacion,
             "estadosAlmacen": estadosAlmacen,
             "estadosValidacion_id": estadosValidacion_id,
             "especificacionesAlmacen":especificacionesAlmacen  , "estadosAlmacen_id":estadosAlmacen_id, "usuAlmacen":usuAlmacen
             }})

    miConexion.close()
    print("solicitudDetalle")
    print(solicitudDetalle)

    # Cierro Conexion

    #{"model": "solicitud.solicitudesdetalle", "pk": 6, "fields":

    context['SolicitudDetalle'] = solicitudDetalle

    serialized1 = json.dumps(solicitudDetalle)

    print ("Envio = ", json)

    return HttpResponse(serialized1, content_type='application/json')


def post_editAlmacen(request,id,username,sedeSeleccionada,nombreUsuario,nombreSede,solicitudId):
    print ("Entre POST edit")
    print ("id = " , id)

    print ("username =" , username)
    print("sedeSeleccionada =", sedeSeleccionada)
    print("nombreUsuario =", nombreUsuario)
    print("nombreSede =", nombreSede)
    print("solicitudId =", solicitudId)

    context = {}
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede
    context['solicitudId'] = solicitudId



    if request.method == 'GET':

        #solicitudesDetalle = SolicitudesDetalle.objects.filter(id=id).first()

        # Abro Conexion

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        # cur = miConexion.cursor()

        miConexion.set_client_encoding('LATIN1')
        cur = miConexion.cursor()
        cur.execute("set client_encoding='LATIN1';")

        comando = 'SELECT sol.id id ,sol.item item, sol.descripcion_id descripcion_id, des.nombre descripcion,sol."tiposCompra_id" tiposCompra_id, tip.nombre tipo , sol.producto producto, substring(art.articulo,1,150) nombre_producto ,sol.presentacion_id  presentacion_id, pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec, sol."usuarioResponsableValidacion_id" usuarioResponsableValidacion_id,  usu.nom_usuario usuResp  , est.nombre estValidacion,est1.nombre estadosAlmacen  , sol."estadosValidacion_id" estadosValidacion_id ,  sol."especificacionesAlmacen" especificacionesAlmacen, sol."estadosAlmacen_id" estadosAlmacen_id ,   usu1.nom_usuario usuAlmacen    FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_estadosvalidacion est, public.solicitud_estadosvalidacion est1   WHERE sol.id = ' + str(id) + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id"  and est.id = sol."estadosValidacion_id" ORDER BY sol.item'

        cur.execute(comando)
        print(comando)

        solicitudDetalle = []
        # solicitudDetalle.append({"model":"solicitud.solicitudesdetalle"})

        for id, item, descripcion_id, descripcion, tiposCompra_id, tipo, producto,nombre_producto, presentacion_id , presentacion, cantidad, justificacion, tec,usuarioResponsableValidacion_id, usuResp, estValidacion,estadosAlmacen, estadosValidacion_id, especificacionesAlmacen, estadosAlmacen_id , usuAlmacen    in cur.fetchall():

            solicitudDetalle.append(
                {
                    #"model": "solicitud.solicitudesdetalle", "pk": id, "fields": {
                     "id": id, "item": item, "descripcion_id": descripcion_id, "descripcion": descripcion,
                    "tiposCompra_id": tiposCompra_id, "tiposCompra": tipo,
                     "producto": producto,"nombre_producto": nombre_producto,
                    "presentacion_id": presentacion_id,
                     "presentacion": presentacion, "cantidad": cantidad, "justificacion": justificacion,
                     "especificacionesTecnicas": tec,
                    "usuarioResponsableValidacion_id": usuarioResponsableValidacion_id,
                     "usuarioResponsableValidacion": usuResp, "estadosValidacion": estValidacion,
                     "estadosAlmacen": estadosAlmacen,
                     "estadosValidacion_id": estadosValidacion_id,
                    "especificacionesAlmacen":especificacionesAlmacen, "estadosAlmacen_id":estadosAlmacen_id,
                    "usuAlmacen":usuAlmacen
                           })

        miConexion.close()
        print("solicitudDetalle")
        print(solicitudDetalle)

        # Cierro Conexion


        print ("Me devuelvo a la MODAL")

        return JsonResponse({'pk':solicitudDetalle[0]['id'],'item':solicitudDetalle[0]['item'],
                             'descripcion_id': solicitudDetalle[0]['descripcion_id'],
                             'descripcion':solicitudDetalle[0]['descripcion'],'tiposCompra_id':solicitudDetalle[0]['tiposCompra_id'], 'tiposCompra':solicitudDetalle[0]['tiposCompra'],
                             'producto':solicitudDetalle[0]['producto'],
                             'nombre_producto': solicitudDetalle[0]['nombre_producto'],
                             'presentacion_id': solicitudDetalle[0]['presentacion_id'],
                             'presentacion':solicitudDetalle[0]['presentacion'],
                             'cantidad':solicitudDetalle[0]['cantidad'],'justificacion':solicitudDetalle[0]['justificacion'],
                             'especificacionesTecnicas':solicitudDetalle[0]['especificacionesTecnicas'],
                             'usuarioResponsableValidacion_id': solicitudDetalle[0]['usuarioResponsableValidacion_id'],
                             'usuarioResponsableValidacion':solicitudDetalle[0]['usuarioResponsableValidacion'],
                             'estadosValidacion':solicitudDetalle[0]['estadosValidacion'],
                             'estadosAlmacen': solicitudDetalle[0]['estadosAlmacen'],
                             'estadosValidacion_id': solicitudDetalle[0]['estadosValidacion_id'],
                             'especificacionesAlmacen':solicitudDetalle[0]['especificacionesAlmacen'],
                             'estadosAlmacen_id': solicitudDetalle[0]['estadosAlmacen_id'],
                             'usuAlmacen': solicitudDetalle[0]['usuAlmacen']
                             })
    else:
        return JsonResponse({'errors':'Something went wrong!'})

def post_deleteAlmacen(request,id):
    print ("Entre a borrar")
    solicitudesDetalle = SolicitudesDetalle.objects.get(id=id)
    solicitudesDetalle.delete()
    return HttpResponseRedirect(reverse('index'))



# Fin Create your views here. para Almacen


# Create your views here. para Compras

def ComprasConsulta(request , username, sedeSeleccionada, nombreUsuario, nombreSede) :
    pass
    print("Entre a consulta Solicitudes a Compras");
    context = {}

    print("username = ", username)
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['solicitudesForm'] = solicitudesForm
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_imhotep", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()
    comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    # Reemplazado
    # comando = "SELECT areas.codreg_area id ,areas.area  area FROM mae_areas areas, imhotep_sedes sedes WHERE areas.activo = 'S' and areas.sede = sedes.sede and sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    cur.execute(comando)
    print(comando)

    areas = []

    for id, area in cur.fetchall():
        areas.append({'id': id, 'area': area})

    miConexion.close()

    context['Areas'] = areas

    return render(request, "Reportes/ComprasConsulta.html", context)



class PostStoreCompras(TemplateView):
    form_class = solicitudesDetalleForm
    template_name = 'Reportes/ComprasTrae.html'

    def post(self, request):
        print ("Entre a Grabar compras")

        context = {}

        print("OPS Entre pos POST DEL VIEW")

        username = request.POST["username"]
        nombreSede = request.POST["nombreSede"]
        nombreUsuario = request.POST["nombreUsuario"]
        sedeSeleccionada = request.POST["sedeSeleccionada"]
        solicitudId = request.POST["solicitudId"]

        context['Username'] = username
        context['SedeSeleccionada'] = sedeSeleccionada
        context['NombreUsuario'] = nombreUsuario
        context['NombreSede'] = nombreSede
        context['solicitudId'] = solicitudId

        print ("CONTEXTO solicitudId", solicitudId)

        form = self.form_class(request.POST)

        data = {'error': form.errors}
        print ("DATA MALUCA = ", data)

        if form.is_valid():
            try:
                print ("Entre forma valida")

                estadosComprasAct = request.POST.get('estadosCompras')
                especificacionesComprasAct = request.POST.get('especificacionesCompras')

                ## AVERIGUAMOS EL ID DEL USUARIO

                miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                cur = miConexion.cursor()

                comando = "SELECT id idActual FROM solicitud_usuarios WHERE num_identificacion = '" + str(username) + "'"
                print(comando)
                cur.execute(comando)
                idActualActual = []

                for idActual in cur.fetchall():
                    idActualActual.append({'idActual': idActual})

                print("idActual =", idActual)

                for dato in idActualActual:
                    print(dato)
                    print(dato['idActual'])
                    print(json.dumps(dato['idActual']))
                    idActual = json.dumps(dato['idActual'])

                idActual = idActual.replace('[', '')
                idActual = idActual.replace(']', '')
                print("idActual FINAL = ", idActual)

                miConexion.close()

                ## FIN AVERIGIAMOS ID DE USUARIO
                usuComprasAct = idActual

                print ("estadosComprasAct = ",estadosComprasAct )
                print("especificacionesComprasAct = ", especificacionesComprasAct)
                print("usuComprasAct = ", usuComprasAct)
                pk = request.POST.get('pk')
                print("pk = ", pk)

                obj = get_object_or_404(SolicitudesDetalle, id=request.POST.get('pk'))
                estadosComprasAnt = obj.estadosCompras
                especificacionesComprasAnt = obj.especificacionesCompras
                usuComprasAnt = obj.usuarioResponsableCompras

                if (str(especificacionesComprasAnt) != str(especificacionesComprasAct) or str(estadosComprasAnt) != str(estadosComprasAct)):

                    obj.estadosCompras_id = EstadosValidacion.objects.get(id=estadosComprasAct)
                    obj.especificacionesCompras=especificacionesComprasAct
                    obj.usuarioResponsableCompra_id = usuComprasAct
                    obj.save()

                return JsonResponse({'success': True, 'message': 'Solicitud Detalle Updated Successfully!'})
            except:
                if (str(especificacionesComprasAnt) != str(especificacionesComprasAct) or str(estadosComprasAnt) != str(estadosComprasAct)):
                    obj.estadosCompras_id = EstadosValidacion.objects.get(id=estadosComprasAct)
                    obj.especificacionesCompras = especificacionesComprasAct
                    obj.usuarioResponsableCompra_id = usuComprasAct
                    obj.save()

                return JsonResponse({'success': True, 'message': 'Solicitud Detalle Created Successfully!'})
        else:
            return JsonResponse({'error': True, 'error': form.errors})
        return render(request, self.template_name,{'data':data})

    def get_context_data(self, **kwargs):
        print("ENTRE POR EL GET_CONTEXT DEL VIEW")
        solicitudId = self.request.GET["solicitudId"]
        username = self.request.GET["username"]
        sedeSeleccionada = self.request.GET["sedeSeleccionada"]
        nombreUsuario = self.request.GET["nombreUsuario"]
        nombreSede = self.request.GET["nombreSede"]

        print("SolictudId =", solicitudId)
        print("username =", username)
        print("sedeSeleccionada =", sedeSeleccionada)
        print("nombreUsuario =", nombreUsuario)
        print("nombreSede =", nombreSede)


        #context = super(PostStore, self).get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)

        context['Username'] = username
        context['SedeSeleccionada'] = sedeSeleccionada
        context['NombreUsuario'] = nombreUsuario
        context['NombreSede'] = nombreSede
        context['SolicitudId'] = solicitudId

        #DESDE AQUIP

        # Buscamos estadosValidacion

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosValidacion = []

        for id, nombre in cur.fetchall():
            estadosValidacion.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosValidacion")
        print(estadosValidacion)

        context['EstadosValidacion'] = estadosValidacion

        # Fin buscamos estdos validacion

        # Buscamos estadosAlmacen

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosAlmacen = []

        for id, nombre in cur.fetchall():
            estadosAlmacen.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosAlmacen")
        print(estadosAlmacen)

        context['EstadosAlmacen'] = estadosAlmacen

        # Fin buscamos estados Almacen

        # Buscamos estadosCompras

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosCompras = []

        for id, nombre in cur.fetchall():
            estadosCompras.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosCompras")
        print(estadosCompras)

        context['EstadosCompras'] = estadosCompras

        # Fin buscamos estados Almacen

        # Buscamos la solicitud

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()
        # Pendiente de reemplazo
        comando = "SELECT sol.id id, to_char(sol.fecha, 'YYYY-MM-DD HH:MM.SS')  fecha, sol.estadoReg estadoReg,sol.usuarios_id usuarioId , usu.nom_usuario nom_usuario, area.area nom_area, sede.nom_sede  nom_sede FROM public.solicitud_solicitudes sol ,public.solicitud_areas area , public.solicitud_sedesCompra sede, public.solicitud_usuarios usu WHERE sol.id = " + solicitudId + " AND area.id = sol.area_id and area.sede_id = sede.id and sol.usuarios_id = usu.id"
        cur.execute(comando)
        print(comando)

        solicitud = []

        for id, fecha, estadoReg, usuarioId, nom_usuario, nom_area, nom_sede in cur.fetchall():
            solicitud.append(
                {'id': id, 'fecha': fecha, 'estadoReg': estadoReg, 'usuarioId': usuarioId, 'nom_usuario': nom_usuario,
                 'nom_area': nom_area, 'nom_sede': nom_sede})

        miConexion.close()
        print("solicitud")
        print(solicitud)

        context['Solicitud'] = solicitud

        # Ahora SolicitudDetalle
        # Fin SolicitudDetalle
        if (solicitud == []):
            print("Entre por No existe")
            context['Error'] = 'Solicitud No Existe '
            miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                          password="BD_m3d1c4l")

            miConexion.set_client_encoding('LATIN1')
            cur = miConexion.cursor()
            cur.execute("set client_encoding='LATIN1';")
            comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
            cur.execute(comando)
            print(comando)
            areas = []
            areas.append({'id': '', 'area': ''})

            for id, area in cur.fetchall():
                areas.append({'id': id, 'area': area})

            miConexion.close()

            context['Areas'] = areas

            print ("No encontre data")

            #return HttpResponse(context, content_type='application/json')
            #return JsonResponse(context)
            #return render(self.request, "Reportes/ValidacionConsulta.html", {'ERROR':'Solicitud No Existe'})
            return context
        else:
            return context


        #HASTA AQUIP class PostStoreCompras

def load_dataCompras(request, solicitudId):
    print ("Entre load_data Compras")
    print("solicitudId = ",solicitudId)

    #print("data = ", request.GET('data'))

    solicitudesDetalleList = SolicitudesDetalle.objects.all().filter(solicitud_id=solicitudId)

    # Ahora SolicitudDetalle
    context= {}

    # Abro Conexion

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    # cur = miConexion.cursor()

    miConexion.set_client_encoding('LATIN1')
    cur = miConexion.cursor()
    cur.execute("set client_encoding='LATIN1';")


    #comando =  'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec,usu.nom_usuario usuResp  , est.nombre estValidacion,est1.nombre estadosAlmacen, sol."estadosValidacion_id" estadosValidacion_id, sol."especificacionesAlmacen" especificacionesAlmacen, sol."estadosAlmacen_id" estadosAlmacen_id ,   usu1.nom_usuario usuAlmacen FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_estadosvalidacion est , public.solicitud_estadosvalidacion est1  WHERE sol.solicitud_id = ' + solicitudId + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id" and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
    comando = 'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec,usu.nom_usuario usuResp  , est.nombre estValidacion,est1.nombre estadosAlmacen, sol."estadosValidacion_id" estadosValidacion_id, sol."especificacionesAlmacen" especificacionesAlmacen, sol."estadosAlmacen_id" estadosAlmacen_id ,   usu1.nom_usuario usuAlmacen , sol."especificacionesCompras" especificacionesCompras, sol."estadosCompras_id" estadosCompras_id, est2.nombre estadosCompras, usu2.nom_usuario usuCompras  FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_usuarios usu2,  public.solicitud_estadosvalidacion est , public.solicitud_estadosvalidacion est1 , public.solicitud_estadosvalidacion est2  WHERE sol.solicitud_id = ' + solicitudId + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and  usu2.id = sol."usuarioResponsableCompra_id"   and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id" and est2.id = "estadosCompras_id"  and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
    cur.execute(comando)
    print(comando)

    solicitudDetalle = []
    #solicitudDetalle.append({"model":"solicitud.solicitudesdetalle"})


    for id, item, descripcion_id, descripcion, tipo, producto, nombre_producto, presentacion, cantidad, justificacion, tec, usuResp, estValidacion, estadosAlmacen, estadosValidacion_id, especificacionesAlmacen, estadosAlmacen_id , usuAlmacen  ,especificacionesCompras,estadosCompras_id, estadosCompras,usuCompras in cur.fetchall():
        solicitudDetalle.append(
            {"model":"solicitud.solicitudesdetalle","pk":id,"fields":
            {"id": id, "item": item, "'descripcion_id": descripcion_id, "descripcion": descripcion, "tiposCompra": tipo,
             "producto": producto,"nombre_producto": nombre_producto,
             "presentacion": presentacion, "cantidad": cantidad, "justificacion": justificacion, "especificacionesTecnicas": tec,
             "usuarioResponsableValidacion": usuResp, "estadosValidacion": estValidacion,
             "estadosAlmacen": estadosAlmacen,
             "estadosValidacion_id": estadosValidacion_id,
             "especificacionesAlmacen":especificacionesAlmacen  , "estadosAlmacen_id":estadosAlmacen_id, "usuAlmacen":usuAlmacen,
             "especificacionesCompras":especificacionesCompras, "estadosCompras_id":estadosCompras_id,
             "estadosCompras":estadosCompras, "usuCompras":usuCompras

             }})

    miConexion.close()
    print("solicitudDetalle")
    print(solicitudDetalle)

    # Cierro Conexion

    #{"model": "solicitud.solicitudesdetalle", "pk": 6, "fields":

    context['SolicitudDetalle'] = solicitudDetalle

    serialized1 = json.dumps(solicitudDetalle)

    print ("Envio = ", json)

    return HttpResponse(serialized1, content_type='application/json')


def post_editCompras(request,id,username,sedeSeleccionada,nombreUsuario,nombreSede,solicitudId):
    print ("Entre POST edit compras")
    print ("id = " , id)

    print ("username =" , username)
    print("sedeSeleccionada =", sedeSeleccionada)
    print("nombreUsuario =", nombreUsuario)
    print("nombreSede =", nombreSede)
    print("solicitudId =", solicitudId)

    context = {}
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede
    context['solicitudId'] = solicitudId



    if request.method == 'GET':

        #solicitudesDetalle = SolicitudesDetalle.objects.filter(id=id).first()

        # Abro Conexion

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        # cur = miConexion.cursor()

        miConexion.set_client_encoding('LATIN1')
        cur = miConexion.cursor()
        cur.execute("set client_encoding='LATIN1';")

        comando = 'SELECT sol.id id ,sol.item item, sol.descripcion_id descripcion_id, des.nombre descripcion,sol."tiposCompra_id" tiposCompra_id, tip.nombre tipo , sol.producto producto, substring(art.articulo,1,150) nombre_producto ,sol.presentacion_id  presentacion_id, pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec, sol."usuarioResponsableValidacion_id" usuarioResponsableValidacion_id,  usu.nom_usuario usuResp  , est.nombre estValidacion,est1.nombre estadosAlmacen  , sol."estadosValidacion_id" estadosValidacion_id ,  sol."especificacionesAlmacen" especificacionesAlmacen, sol."estadosAlmacen_id" estadosAlmacen_id ,   usu1.nom_usuario usuAlmacen , sol."especificacionesCompras" especificacionesCompras, sol."estadosCompras_id" estadosCompras_id, est2.nombre estadosCompras, usu2.nom_usuario usuCompras     FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 ,  public.solicitud_usuarios usu2 , public.solicitud_estadosvalidacion est, public.solicitud_estadosvalidacion est1, public.solicitud_estadosvalidacion est2 WHERE sol.id = ' + str(id) + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu2.id = sol."usuarioResponsableCompra_id"  and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id"  and est2.id = sol."estadosCompras_id" and est.id = sol."estadosValidacion_id" ORDER BY sol.item'

        cur.execute(comando)
        print(comando)

        solicitudDetalle = []
        # solicitudDetalle.append({"model":"solicitud.solicitudesdetalle"})

        for id, item, descripcion_id, descripcion, tiposCompra_id, tipo, producto,nombre_producto, presentacion_id , presentacion, cantidad, justificacion, tec,usuarioResponsableValidacion_id, usuResp, estValidacion,estadosAlmacen, estadosValidacion_id, especificacionesAlmacen, estadosAlmacen_id , usuAlmacen   ,especificacionesCompras,estadosCompras_id, estadosCompras,usuCompras   in cur.fetchall():

            solicitudDetalle.append(
                {
                    #"model": "solicitud.solicitudesdetalle", "pk": id, "fields": {
                     "id": id, "item": item, "descripcion_id": descripcion_id, "descripcion": descripcion,
                    "tiposCompra_id": tiposCompra_id, "tiposCompra": tipo,
                     "producto": producto,"nombre_producto": nombre_producto,
                    "presentacion_id": presentacion_id,
                     "presentacion": presentacion, "cantidad": cantidad, "justificacion": justificacion,
                     "especificacionesTecnicas": tec,
                    "usuarioResponsableValidacion_id": usuarioResponsableValidacion_id,
                     "usuarioResponsableValidacion": usuResp, "estadosValidacion": estValidacion,
                     "estadosAlmacen": estadosAlmacen,
                     "estadosValidacion_id": estadosValidacion_id,
                    "especificacionesAlmacen":especificacionesAlmacen, "estadosAlmacen_id":estadosAlmacen_id,
                    "usuAlmacen":usuAlmacen,
                    "especificacionesCompras": especificacionesCompras, "estadosCompras_id": estadosCompras_id,
                    "estadosCompras": estadosCompras, "usuCompras": usuCompras

                })

        miConexion.close()
        print("solicitudDetalle")
        print(solicitudDetalle)

        # Cierro Conexion


        print ("Me devuelvo a la MODAL")

        return JsonResponse({'pk':solicitudDetalle[0]['id'],'item':solicitudDetalle[0]['item'],
                             'descripcion_id': solicitudDetalle[0]['descripcion_id'],
                             'descripcion':solicitudDetalle[0]['descripcion'],'tiposCompra_id':solicitudDetalle[0]['tiposCompra_id'], 'tiposCompra':solicitudDetalle[0]['tiposCompra'],
                             'producto':solicitudDetalle[0]['producto'],
                             'nombre_producto': solicitudDetalle[0]['nombre_producto'],
                             'presentacion_id': solicitudDetalle[0]['presentacion_id'],
                             'presentacion':solicitudDetalle[0]['presentacion'],
                             'cantidad':solicitudDetalle[0]['cantidad'],'justificacion':solicitudDetalle[0]['justificacion'],
                             'especificacionesTecnicas':solicitudDetalle[0]['especificacionesTecnicas'],
                             'usuarioResponsableValidacion_id': solicitudDetalle[0]['usuarioResponsableValidacion_id'],
                             'usuarioResponsableValidacion':solicitudDetalle[0]['usuarioResponsableValidacion'],
                             'estadosValidacion':solicitudDetalle[0]['estadosValidacion'],
                             'estadosAlmacen': solicitudDetalle[0]['estadosAlmacen'],
                             'estadosValidacion_id': solicitudDetalle[0]['estadosValidacion_id'],
                             'especificacionesAlmacen':solicitudDetalle[0]['especificacionesAlmacen'],
                             'estadosAlmacen_id': solicitudDetalle[0]['estadosAlmacen_id'],
                             'usuAlmacen': solicitudDetalle[0]['usuAlmacen'],
                             'especificacionesCompras': solicitudDetalle[0]['especificacionesCompras'],
                             'estadosCompras_id': solicitudDetalle[0]['estadosCompras_id'],
                             'estadosCompras': solicitudDetalle[0]['estadosCompras'],
                             'usuCompras': solicitudDetalle[0]['usuCompras'],

                             })
    else:
        return JsonResponse({'errors':'Something went wrong!'})

def post_deleteCompras(request,id):
    print ("Entre a borrar")
    solicitudesDetalle = SolicitudesDetalle.objects.get(id=id)
    solicitudesDetalle.delete()
    return HttpResponseRedirect(reverse('index'))


# Fin Create your views here. para Compras

# Create your views here. para Ordenes de Compras

def OrdenesCompraConsulta1(request , username, sedeSeleccionada, nombreUsuario, nombreSede):
    pass
    print ("Entre a consulta Ordenes de Compra1 solicitud");
    context = {}

    print("username = ", username)
    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['solicitudesForm'] = solicitudesForm
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    cur = miConexion.cursor()
    comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    #Reemplazado
    #comando = "SELECT areas.codreg_area id ,areas.area  area FROM mae_areas areas, imhotep_sedes sedes WHERE areas.activo = 'S' and areas.sede = sedes.sede and sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
    cur.execute(comando)
    print(comando)

    areas = []

    for id, area in cur.fetchall():
        areas.append({'id': id, 'area': area})

    miConexion.close()

    context['Areas'] = areas

    return render(request, "Reportes/OrdenesCompraConsulta.html", context)


class PostStoreOrdenesCompra(TemplateView):
    form_class = ordenesCompraForm
    template_name = 'Reportes/OrdenesCompraTrae2.html'

    def post(self, request):
        print ("Entre a Grabar Ordenes de compras")

        context = {}

        print("OPS Entre pos POST DEL VIEW de Ordenes de Compra")

        username = request.POST["username"]
        nombreSede = request.POST["nombreSede"]
        nombreUsuario = request.POST["nombreUsuario"]
        sedeSeleccionada = request.POST["sedeSeleccionada"]
        solicitudId = request.POST["solicitudId"]

        # Contamos
        valeQuerySet = SolicitudesDetalle.objects.filter(solicitud_id=solicitudId, estadosCompras_id=3)

        print("vale =", valeQuerySet.count())

        totalRegistros = valeQuerySet.count()

        print("totalRegistros =", totalRegistros)

        context['Username'] = username
        context['SedeSeleccionada'] = sedeSeleccionada
        context['NombreUsuario'] = nombreUsuario
        context['NombreSede'] = nombreSede
        context['SolicitudId'] = solicitudId

        print ("CONTEXTO solicitudId", solicitudId)

        form = self.form_class(request.POST)

        data = {'error': form.errors}
        print ("DATA MALUCA = ", data)

        if form.is_valid():
            try:
                print ("Entre forma valida Orden de Compra")
                print("form =", form.cleaned_data)

                ordenesCompra = OrdenesCompra(
                    fechaElab=form.cleaned_data['fechaElab'],
                    fechaRevi=form.cleaned_data['fechaRevi'],
                    fechaApro=form.cleaned_data['fechaApro'],
                    estadoOrden=form.cleaned_data['estadoOrden'],
                    elaboro=form.cleaned_data['elaboro'],
                    revizo=form.cleaned_data['revizo'],
                    aprobo=form.cleaned_data['aprobo'],
                    area=form.cleaned_data['area'],
                    contacto=form.cleaned_data['contacto'],
                    entregarEn=form.cleaned_data['entregarEn'],
                    telefono=form.cleaned_data['telefono'],
                    proveedor=form.cleaned_data['proveedor'],
                    opciones=form.cleaned_data['opciones'],
                    valorBruto=form.cleaned_data['valorBruto'],
                    descuento=form.cleaned_data['descuento'],
                    valorParcial=form.cleaned_data['valorParcial'],
                    iva=form.cleaned_data['iva'],
                    valorTotal=form.cleaned_data['valorTotal'],
                    observaciones=form.cleaned_data['observaciones'],
                    responsableCompra=form.cleaned_data['responsableCompra'],
                    entragaMercancia=   form.cleaned_data['entragaMercancia'],
                    recibeMercancia=form.cleaned_data['recibeMercancia'],
                    estadoReg=form.cleaned_data['estadoReg']
                )

                ordenesCompra.save()

                print (ordenesCompra.id)

                idCompra = ordenesCompra.id


                context['NoOrdenCompra'] = idCompra
                context['SolicitudId'] = 0
                context['success'] = True
                context['message'] = 'Orden de Compra No ' + str(idCompra) +  ' Created Successfully!'

                ## Comienzo a preparar la impresion EXCEL  de la Orden de Compra

                my_wb = openpyxl.Workbook(encoding='ascii')

                my_sheet = my_wb.active
                fuente1 = Font(name='Century', bold=True, size=11, color='0a0a0a')
                fuente2 = Font(name='Century', bold=False, size=11, color='0a0a0a')

                b1 = my_sheet['B1']
                b1.value = "NIT 830.507.718-8"
                e1 = my_sheet['E1']
                e1.value = "FORMATO"
                e1.font = fuente1
                e3 = my_sheet['E3']
                e3.value = "APOYO FINANCIERO COMPRAS"
                e3.font = fuente1
                e5 = my_sheet['E5']
                e5.value = "ORDEN DE COMPRA : "+ str(idCompra)
                e5.font = fuente1
                print("pase1")
                j1 = my_sheet['J1']
                j1.value = "Código: FOR-AFI-ORDEN DE COMPRA"
                j2 = my_sheet['J2']
                j2.value = "Versión 4"
                j3 = my_sheet['J3']
                j3.value = "Fecha de Elaboración :"
                l3 = my_sheet['L3']
                l3.value = str(form.cleaned_data['fechaElab'])
                l3 = my_sheet['L3']
                l3.value = str(form.cleaned_data['fechaElab'])
                j4 = my_sheet['J4']
                j4.value = "Fecha de Revision"
                l4 = my_sheet['L4']
                l4.value = str(form.cleaned_data['fechaRevi'])
                j5 = my_sheet['J5']
                j5.value = "Fecha de Aprobacion"
                l5 = my_sheet['L5']
                l5.value = str(form.cleaned_data['fechaApro'])
                j6 = my_sheet['J6']
                j6.value = "Pagina"
                j6.font = fuente1
                l6 = my_sheet['L6']
                l6.value = "ESTADO"
                l6.font = fuente1
                print("pase2")
                b7 = my_sheet['B7']
                b7.value = "ELABORO"
                b7.font = fuente1
                c7 = my_sheet['C7']
                c7.value = str(form.cleaned_data['elaboro'])
                c7.font = fuente2

                f7 = my_sheet['F7']
                f7.value = "REVIZO"
                f7.font = fuente1
                g7 = my_sheet['G7']
                g7.value = str(form.cleaned_data['revizo'])
                g7.font = fuente2

                j7 = my_sheet['J7']
                j7.value = "APROBO"
                j7.font = fuente1

                k7 = my_sheet['K7']
                k7.value = str(form.cleaned_data['aprobo'])
                k7.font = fuente2

                print("pase21")
                e9 = my_sheet['E9']
                e9.value = "DATOS ORDEN DE COMPRA"
                e9.font = fuente1
                b11 = my_sheet['B11']
                b11.value = "FECHA"
                b11.font = fuente2
                d11 = my_sheet['D11']
                d11.value = str(form.cleaned_data['fechaElab'])
                print("pase22")
                g11 = my_sheet['G11']
                g11.value = "AREA"
                g11.font = fuente2
                print("pase23")
                h11 = my_sheet['H11']
                h11.value = str(form.cleaned_data['area'])

                k11 = my_sheet['K11']
                k11.value = "# Cotizacion:"
                k11.font = fuente1
                l11 = my_sheet['L11']
                l11.value = "Pedido No:"
                l11.font = fuente1
                b12 = my_sheet['B12']
                b12.value = "CONTACTO"
                b12.font = fuente2
                print("pase24")
                d12 = my_sheet['D12']
                d12.value = str(form.cleaned_data['contacto'])
                g12 = my_sheet['G12']
                g12.value = "ENTREGAR EN"
                g12.font = fuente2
                h12 = my_sheet['H12']
                h12.value = str(form.cleaned_data['entregarEn'])
                b13 = my_sheet['B13']
                b13.value = "TELEFONO"
                b13.font = fuente2
                d13 = my_sheet['D13']
                d13.value = str(form.cleaned_data['telefono'])
                b14 = my_sheet['B14']
                b14.value = "          Horario de Recepcion :"
                b14.font = fuente1
                e14 = my_sheet['E14']
                e14.value = "martes y jueves: 7:30 am a 12 pm y de 2:00 pm a 4:00 pm "
                e14.font = fuente1
                e15 = my_sheet['E15']
                e15.value = "DATOS DEL PROVEEDOR"
                e15.font = fuente1

                ## Extraemos los datos del Proveedor

                miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                              password="BD_m3d1c4l")
                miConexion.set_client_encoding('LATIN1')
                cur = miConexion.cursor()

                comando = "SELECT prov.proveedor nombre, prov.nit nit, prov.telefono telefono, translate(btrim(prov.direccion::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text)  direccion, prov.correo correo FROM public.solicitud_proveedores prov WHERE prov.proveedor = '" + str(form.cleaned_data['proveedor']) + "'"
                print(comando)
                print("pase26")
                cur.execute("set client_encoding='LATIN1';")
                cur.execute(comando)
                print(comando)

                prov = []

                for nombre , nit, telefono, direccion, correo in cur.fetchall():
                    prov.append({'nombre': nombre, 'nit' : nit, 'telefono' : telefono, 'direccion' : direccion, 'correo' : correo })

                miConexion.close()
                print("prov")
                print(prov)

                for x in prov:
                    print("X = " ,x)
                    jsonProv= x

                nombreProveedor = jsonProv['nombre']
                nitProveedor = jsonProv['nit']
                telefonoProveedor = jsonProv['telefono']
                direccionProveedor = jsonProv['direccion']
                correoProveedor = jsonProv['correo']

                print ("nombre Proveedor = ",nombreProveedor )
                print ("Nit Proveedor = ", nitProveedor)
                print("telefonoProveedor = ", telefonoProveedor)
                print("direccionProveedor = ", direccionProveedor)
                print("correoProveedor = ", correoProveedor)

                ### FIN DATOS DEL PROVEEDOR

                print("Pase 50")
                b16 = my_sheet['B16']
                b16.value = "RAZON SOCIAL"
                b16.font = fuente2
                d16 = my_sheet['D16']
                d16.value = str(nombreProveedor)
                h16 = my_sheet['H16']
                h16.value =  "NIT"
                h16.font = fuente1
                print("Pase 51")
                i16 = my_sheet['I16']
                i16.value = str(nitProveedor)
                print("Pase 52")
                k16 = my_sheet['K16']
                k16.value = "TELEFONO:"
                k16.font = fuente1
                print("Pase 53")
                l16 = my_sheet['L16']
                l16.value = str(telefonoProveedor)
                b17 = my_sheet['B17']
                b17.value = "DIRECCION:"
                b17.font = fuente1
                d17 = my_sheet['D17']
                d17.value = str(direccionProveedor)
                print("Pase 54")
                h17 = my_sheet['H17']
                h17.value = "E-MAIL:"
                h17.font = fuente1
                i17 = my_sheet['I17']
                i17.value = str(correoProveedor)
                print("Pase 55")
                b18 = my_sheet['B18']
                b18.value = "ATENCION:"
                b18.font = fuente2
                e20 = my_sheet['E20']
                e20.value = "DETALLE DE LA COMPRA"
                e20.font = fuente1
                k20 = my_sheet['K20']
                k20.value = "VALOR BRUTO"
                k20.font = fuente1
                b21 = my_sheet['B21']
                b21.value = "ITEM"
                b21.font = fuente1
                c21 = my_sheet['C21']
                c21.value = "DESCRIPCION REF"
                c21.font = fuente1
                f21 = my_sheet['F21']
                f21.value = "PRESENT."
                f21.font = fuente1
                g21 = my_sheet['G21']
                g21.value = "IVA"
                g21.font = fuente1
                h21 = my_sheet['H21']
                h21.value = "CANTIDAD"
                h21.font = fuente1
                h22 = my_sheet['H22']
                h22.value = "SOLICITADA"
                h22.font = fuente1
                i22 = my_sheet['I22']
                i22.value = "RECIBIDA"
                i22.font = fuente1
                j21 = my_sheet['J21']
                j21.value = "VALOR UNITARIO"
                j21.font = fuente1
                k21 = my_sheet['K21']
                k21.value = "VALOR TOTAL"
                k21.font = fuente1
                k22 = my_sheet['K22']
                k22.value = "SOLICITADA"
                k22.font = fuente1
                l22 = my_sheet['L22']
                l22.value = "RECIBIDA"
                l22.font = fuente1


                print("Armo pah archivo")

                archivo = 'C:/EntornosPython/comprasTable/comprasTable/Archivos/OC_' + str(idCompra) + '.xlsx'
                print ("Archivo =" , archivo)

                ## DESDE AQUI RUTINA ACTUALIZA ITEM EN SOLICITUD DETALLE
                # Imprimo en un for los valores de los items

                for campo in range(1, totalRegistros + 1):
                    print("item = " ,campo)
                    var1 = "item_" + str(campo)
                    var2 = "iva_" + str(campo)
                    var3 = "solcan_" + str(campo)
                    var4 = "reccan_" + str(campo)
                    var5 = "unitario_" + str(campo)
                    var6 = "solval_" + str(campo)
                    var7 = "recval_" + str(campo)
                    print ("var2 IVA_ = ", var2)
                    data1 = request.POST[var1]
                    data2 = request.POST[var2]
                    data3 = request.POST[var3]
                    data4 = request.POST[var4]
                    data5 = request.POST[var5]
                    data6 = request.POST[var6]
                    data7 = request.POST[var7]
                    print ("Registro Completo = ", data1 + ' ' + data2 + ' ' +data3 + ' ' + data4 + ' ' + data5 + ' ' + data6 + ' ' +data7)

                    ## Rutina Actualiza uno a una los items de la solicitud

                    miConexiont = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432",    user="postgres", password="BD_m3d1c4l")
                    print ("Me conecte")
                    curt = miConexiont.cursor()
                    print("Abri cursor")
                    comando = 'UPDATE solicitud_solicitudesDetalle set iva = ' + str(data2) + ', "recibidoOrdenCantidad" = ' + str(data4) + ', "recibidoOrdenValor" =' + str(data7) + ',"solicitadoOrdenCantidad" = ' + str(data3) + ',"solicitadoOrdenValor" = ' + str(data6) + ',"valorUnitario" = ' + str(data5) + ', "ordenCompra_id" = ' + str(idCompra) + ' WHERE solicitud_id = ' + solicitudId + ' AND item = ' + str(data1)

                    print(comando)
                    print("voy a ejecutar comando")
                    resultado = curt.execute(comando)
                    print("resultado =", resultado)
                    n = curt.rowcount
                    print("Registros commit = ", n)

                    miConexiont.commit()

                    ## Aqui la impresion Excel del detalle de la Orden de Compra

                    b23 = my_sheet['B23']
                    b23.value = str(data1)
                    c23 = my_sheet['C23']
                    c23.value = "AqUi descripcion"
                    f23 = my_sheet['F23']
                    f23.value = "AqUi presentacion"
                    g23 = my_sheet['G23']
                    g23.value = str(data2)
                    h23 = my_sheet['H23']
                    h23.value = str(data3)
                    i23 = my_sheet['I23']
                    i23.value = str(data4)
                    j23 = my_sheet['J23']
                    j23.value = str(data5)
                    k23 = my_sheet['K23']
                    k23.value = str(data6)
                    l23 = my_sheet['L23']
                    l23.value = str(data7)

                    ## Fin detalle Excel

                #seguimos con la ultima parte del archivo excel

                print ("Pase 56")
                b27 = my_sheet['B27']
                b27.value = "FORMA DE PAGO"
                b27.font = fuente1
                b28 = my_sheet['B28']
                b28.value = "OPCION 1"
                b28.font = fuente1
                c28 = my_sheet['C28']
                c28.value = "CONTRA ENTREGA"
                c28.font = fuente2
                b29 = my_sheet['B29']
                b29.value = "OPCION 2"
                b29.font = fuente1
                c29 = my_sheet['C29']
                c29.value = "ANTICIPO"
                c29.font = fuente2
                e29 = my_sheet['E29']
                e29.value = "50 %"
                e29.font = fuente2
                f29 = my_sheet['F29']
                f29.value = str(form.cleaned_data['opciones'])
                f29.font = fuente2
                c30 = my_sheet['C30']
                c30.value = "CONTRA ENTREGA"
                c30.font = fuente2
                e30 = my_sheet['E30']
                e30.value = "50 %"
                e30.font = fuente2
                b31 = my_sheet['B31']
                b31.value = "OPCION 3"
                b31.font = fuente1
                c31 = my_sheet['C31']
                c31.value = "NOVENTA (90) DIAS"
                c31.font = fuente2
                b32 = my_sheet['B32']
                b32.value = "OPCION 4"
                b32.font = fuente1
                h27 = my_sheet['H27']
                h27.value = "VALOR BRUTO"
                h27.font = fuente1
                print("Pase 57")
                l27 = my_sheet['L27']
                l27.value = str(form.cleaned_data['valorBruto'])
                h28 = my_sheet['H28']
                h28.value = "DESCUENTO %"
                h28.font = fuente1
                l28 = my_sheet['L28']
                l28.value = str(form.cleaned_data['descuento'])
                h29 = my_sheet['H29']
                h29.value = "VALOR PARCIAL"
                h29.font = fuente1
                l29 = my_sheet['L29']
                l29.value = str(form.cleaned_data['valorParcial'])
                h30 = my_sheet['H30']
                h30.value = "IVA"
                h30.font = fuente1
                l30 = my_sheet['L30']
                l30.value = str(form.cleaned_data['iva'])
                print("Pase 58")
                h31 = my_sheet['H31']
                h31.value = "VALOR TOTAL"
                h31.font = fuente1
                l31 = my_sheet['L31']
                l31.value = form.cleaned_data['valorTotal']

                h32 = my_sheet['H32']
                h32.value = "OBSERVACIONES"
                h32.font = fuente1
                l32 = my_sheet['L32']
                l32.value = str(form.cleaned_data['observaciones'])

                b36 = my_sheet['B36']
                b36.value = "RESPONSABLE ORDEN DE COMPRA:"
                b36.font = fuente1
                print("Pase 59")
                b38 = my_sheet['B38']
                b38.value = str(form.cleaned_data['responsableCompra'])

                g36 = my_sheet['G36']
                g36.value = "QUIEN ENTREGA MERCANCIA:"
                g36.font = fuente1
                print("Pase 60")
                g38 = my_sheet['G38']
                g38.value = str(form.cleaned_data['entragaMercancia'])
                k36 = my_sheet['K36']
                k36.value = "QUIEN RECIBE MERCANCIA:"
                k36.font = fuente1
                k38 = my_sheet['K38']
                k38.value = str(form.cleaned_data['recibeMercancia'])
                print("Pase 61")
                b43 = my_sheet['B43']
                b43.value = "FIRMA Y SELLO"
                b43.font = fuente2
                g43 = my_sheet['G43']
                g43.value = "FIRMA Y SELLO"
                g43.font = fuente2
                k43 = my_sheet['K43']
                k43.value = "FIRMA Y SELLO"
                k43.font = fuente2
                b44 = my_sheet['B44']
                b44.value = "NOTA ACLARATORIA. "
                b44.font = fuente1
                e44 = my_sheet['E44']
                e44.value = "TODA CANTIDAD RECIBIDA, MAYOR A LA SOLICITADA EN LA ORDEN DE COMPRA NO SERÁ PAGADA POR LA CLÍNICA MEDICAL S.A.S"
                e44.font = fuente2
                print("Pase Final")

                response = HttpResponse(content_type="application/ms-excel")
                contenido = "attachment; filename = {0}".format(archivo)
                response["Content-Disposition"] = contenido
                my_wb.save(archivo)
                #my_wb.save(response)
                #return response

                ## fin excel

                return render(request, self.template_name, context)



            except:

                return render(request, self.template_name,{'success': True, 'message': 'Orden de Compra Error Created Successfully!'})

        else:
            context['error'] = form.errors
            return render(request, self.template_name, context)
            #return JsonResponse({'error': True, 'error': form.errors})

        return render(request, self.template_name,{'data':data})

    def get_context_data(self, **kwargs):
        print("GET_CONTEXT DEL VIEW DE ORDENES DE COMPRA")
        solicitudId = self.request.GET["solicitudId"]
        username = self.request.GET["username"]
        sedeSeleccionada = self.request.GET["sedeSeleccionada"]
        nombreUsuario = self.request.GET["nombreUsuario"]
        nombreSede = self.request.GET["nombreSede"]

        print("SolictudId =", solicitudId)
        print("username =", username)
        print("sedeSeleccionada =", sedeSeleccionada)
        print("nombreUsuario =", nombreUsuario)
        print("nombreSede =", nombreSede)



        #context = super(PostStore, self).get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)

        context['Username'] = username
        context['SedeSeleccionada'] = sedeSeleccionada
        context['NombreUsuario'] = nombreUsuario
        context['NombreSede'] = nombreSede
        context['SolicitudId'] = solicitudId
        context['ordenesCompraForm'] = ordenesCompraForm

        #DESDE AQUIP

        # Buscamos estadosValidacion

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosValidacion = []

        for id, nombre in cur.fetchall():
            estadosValidacion.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosValidacion")
        print(estadosValidacion)

        context['EstadosValidacion'] = estadosValidacion

        # Fin buscamos estdos validacion

        # Buscamos estadosAlmacen

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosAlmacen = []

        for id, nombre in cur.fetchall():
            estadosAlmacen.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosAlmacen")
        print(estadosAlmacen)

        context['EstadosAlmacen'] = estadosAlmacen

        # Fin buscamos estados Almacen

        # Buscamos estadosCompras

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()

        comando = 'SELECT id,nombre FROM public.solicitud_estadosValidacion est'
        cur.execute(comando)
        print(comando)

        estadosCompras = []

        for id, nombre in cur.fetchall():
            estadosCompras.append({'id': id, 'nombre': nombre})

        miConexion.close()
        print("estadosCompras")
        print(estadosCompras)

        context['EstadosCompras'] = estadosCompras

        # Fin buscamos estados Almacen

        # Buscamos la solicitud

        miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                      password="BD_m3d1c4l")
        cur = miConexion.cursor()
        # Pendiente de reemplazo
        comando = "SELECT sol.id id, to_char(sol.fecha, 'YYYY-MM-DD HH:MM.SS')  fecha, sol.estadoReg estadoReg,sol.usuarios_id usuarioId , usu.nom_usuario nom_usuario, area.area nom_area, sede.nom_sede  nom_sede FROM public.solicitud_solicitudes sol ,public.solicitud_areas area , public.solicitud_sedesCompra sede, public.solicitud_usuarios usu WHERE sol.id = " + solicitudId + " AND area.id = sol.area_id and area.sede_id = sede.id and sol.usuarios_id = usu.id"
        cur.execute(comando)
        print(comando)

        solicitud = []

        for id, fecha, estadoReg, usuarioId, nom_usuario, nom_area, nom_sede in cur.fetchall():
            solicitud.append(
                {'id': id, 'fecha': fecha, 'estadoReg': estadoReg, 'usuarioId': usuarioId, 'nom_usuario': nom_usuario,
                 'nom_area': nom_area, 'nom_sede': nom_sede})

        miConexion.close()
        print("solicitud")
        print(solicitud)

        context['Solicitud'] = solicitud

        # Ahora SolicitudDetalle
        # Fin SolicitudDetalle
        if (solicitud == []):
            print("Entre por No existe")
            context['Error'] = 'Solicitud No Existe '
            miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                          password="BD_m3d1c4l")

            miConexion.set_client_encoding('LATIN1')
            cur = miConexion.cursor()
            cur.execute("set client_encoding='LATIN1';")
            comando = "SELECT areas.id id ,areas.area  area FROM public.solicitud_areas areas, public.solicitud_sedesCompra sedes WHERE areas.estadoreg = 'A' and areas.sede_id = sedes.id and  sedes.codreg_sede = '" + sedeSeleccionada + "' order by areas.area"
            cur.execute(comando)
            print(comando)
            areas = []
            areas.append({'id': '', 'area': ''})

            for id, area in cur.fetchall():
                areas.append({'id': id, 'area': area})

            miConexion.close()

            context['Areas'] = areas

            print ("No encontre data")

            #return HttpResponse(context, content_type='application/json')
            #return JsonResponse(context)
            #return render(self.request, "Reportes/ValidacionConsulta.html", {'ERROR':'Solicitud No Existe'})
            return context
        else:
            # POr aqui si existe
            ## Desde aquip codigo para la vista de ordenescompratrae2

            # Abro Conexion

            miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                          password="BD_m3d1c4l")
            # cur = miConexion.cursor()

            miConexion.set_client_encoding('LATIN1')
            cur = miConexion.cursor()
            cur.execute("set client_encoding='LATIN1';")

            # comando =  'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec,usu.nom_usuario usuResp  , est.nombre estValidacion,est1.nombre estadosAlmacen, sol."estadosValidacion_id" estadosValidacion_id, sol."especificacionesAlmacen" especificacionesAlmacen, sol."estadosAlmacen_id" estadosAlmacen_id ,   usu1.nom_usuario usuAlmacen FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_estadosvalidacion est , public.solicitud_estadosvalidacion est1  WHERE sol.solicitud_id = ' + solicitudId + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id" and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
            comando = 'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion, sol.iva iva ,sol."recibidoOrdenCantidad" recibidoOrdenCantidad,sol."recibidoOrdenValor" recibidoOrdenValor,sol."solicitadoOrdenCantidad" solicitadoOrdenCantidad,sol."solicitadoOrdenValor" solicitadoOrdenValor,sol."valorUnitario" valorUnitario FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_usuarios usu2,  public.solicitud_estadosvalidacion est , public.solicitud_estadosvalidacion est1 , public.solicitud_estadosvalidacion est2  WHERE sol.solicitud_id = ' + solicitudId + ' AND sol."estadosCompras_id" = 3  AND  (sol."ordenCompra_id"= 0 OR  sol."ordenCompra_id" is null)  AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and  usu2.id = sol."usuarioResponsableCompra_id"   and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id" and est2.id = "estadosCompras_id"  and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
            cur.execute(comando)
            print(comando)

            solicitudDetalle = []
            # solicitudDetalle.append({"model":"solicitud.solicitudesdetalle"})

            for id, item, descripcion_id, descripcion, tipo, producto, nombre_producto, presentacion, iva, recibidoOrdenCantidad, recibidoOrdenValor, solicitadoOrdenCantidad, solicitadoOrdenValor, valorUnitario in cur.fetchall():
                solicitudDetalle.append(
                     {"id": id, "item": item, "descripcion": descripcion, "tiposCompra": tipo,
                         "producto": producto, "nombre_producto": nombre_producto,
                         "presentacion": presentacion, "iva": iva, "recibidoOrdenCantidad": recibidoOrdenCantidad,
                         "recibidoOrdenValor": recibidoOrdenValor, "solicitadoOrdenCantidad": solicitadoOrdenCantidad,
                         "solicitadoOrdenValor":solicitadoOrdenValor, "valorUnitario": valorUnitario
                         })

            miConexion.close()
            print("solicitudDetalle")
            print(solicitudDetalle)

            # Cierro Conexion

            context['SolicitudDetalle'] = solicitudDetalle

            ## Fin

            return context


        #HASTA AQUIP class PostStoreCompras

def load_dataOrdenesCompra(request, solicitudId):
    print ("Entre load_data Ordenes de Compras")
    print("solicitudId = ",solicitudId)

    #print("data = ", request.GET('data'))

    solicitudesDetalleList = SolicitudesDetalle.objects.all().filter(solicitud_id=solicitudId)

    # Ahora SolicitudDetalle
    context= {}

    # Abro Conexion

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres",
                                  password="BD_m3d1c4l")
    # cur = miConexion.cursor()

    miConexion.set_client_encoding('LATIN1')
    cur = miConexion.cursor()
    cur.execute("set client_encoding='LATIN1';")


    #comando =  'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion,sol.cantidad, sol.justificacion  , sol."especificacionesTecnicas" tec,usu.nom_usuario usuResp  , est.nombre estValidacion,est1.nombre estadosAlmacen, sol."estadosValidacion_id" estadosValidacion_id, sol."especificacionesAlmacen" especificacionesAlmacen, sol."estadosAlmacen_id" estadosAlmacen_id ,   usu1.nom_usuario usuAlmacen FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_estadosvalidacion est , public.solicitud_estadosvalidacion est1  WHERE sol.solicitud_id = ' + solicitudId + ' AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id" and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
    comando = 'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion, sol.iva iva ,sol."recibidoOrdenCantidad" recibidoOrdenCantidad,sol."recibidoOrdenValor" recibidoOrdenValor,sol."solicitadoOrdenCantidad" solicitadoOrdenCantidad,sol."solicitadoOrdenValor" solicitadoOrdenValor,sol."valorUnitario" valorUnitario FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_usuarios usu2,  public.solicitud_estadosvalidacion est , public.solicitud_estadosvalidacion est1 , public.solicitud_estadosvalidacion est2  WHERE sol.solicitud_id = ' + solicitudId + ' AND sol."estadosAlmacen_id" = 3  AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and  usu2.id = sol."usuarioResponsableCompra_id"   and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id" and est2.id = "estadosCompras_id"  and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
    cur.execute(comando)
    print(comando)

    solicitudDetalle = []
    #solicitudDetalle.append({"model":"solicitud.solicitudesdetalle"})


    for id, item, descripcion_id, descripcion, tipo, producto, nombre_producto, presentacion, iva ,recibidoOrdenCantidad,recibidoOrdenValor,solicitadoOrdenCantidad,solicitadoOrdenValor,valorUnitario  in cur.fetchall():
        solicitudDetalle.append(
            {"model":"solicitud.solicitudesdetalle","pk":id,"fields":
            {"id": id, "item": item,  "descripcion": descripcion, "tiposCompra": tipo,
             "producto": producto,"nombre_producto": nombre_producto,
             "presentacion": presentacion, "iva":0, "recibidoOrdenCantidad":0,
             "recibidoOrdenValor" : 0,"solicitadoOrdenCantidad" : 0,
             "solicitadoOrdenValor" : 0, "valorUnitario" : 0
             }})

    miConexion.close()
    print("solicitudDetalle")
    print(solicitudDetalle)

    # Cierro Conexion

    #{"model": "solicitud.solicitudesdetalle", "pk": 6, "fields":

    context['SolicitudDetalle'] = solicitudDetalle

    serialized1 = json.dumps(solicitudDetalle)

    print ("Envio = ", json)

    return HttpResponse(serialized1, content_type='application/json')

def descargaArchivo(request, archivo):

    print ("Entro A Descargar Archivo")

    nombreReporte = 'C:\EntornosPython\comprasTable\comprasTable\Archivos_OC_116'
    nombreReporteFinal = nombreReporte + ".xlsx"

    response = HttpResponse(content_type="application/ms-excel")
    #response.write(u'\ufeff'.encode('utf8'))
    contenido = "attachment; filename = {0}".format(nombreReporteFinal)
    #contenido = "attachment; filename = " + nombreReporteFinal
    response["Content-Disposition"] = contenido

    return response

## Desde Aqui Consulta Ordenes de Compras

def OrdenesCompraConsulta(request, username, sedeSeleccionada, nombreUsuario, nombreSede):

    context = {}
    print ("username = " , username )

    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede



    print ("Entre Consulta OrdenesCompra")


    return render(request, 'Reportes\OrdenesCompraConsulta1.html', context )



def load_dataOrdenesCompraConsulta(request, data):
    print("Entre DE VERDAD load_dataOrdenesCompraConsulta ")

    #data = request.GET['data']
    print ("data = ", data)
    d = json.loads(data)
    desdeFechaSolicitud = d['desdeFechaSolicitud']
    hastaFechaSolicitud = d['hastaFechaSolicitud']

    username = d['username']
    nombreSede = d['nombreSede']
    nombreUsuario = d['nombreUsuario']
    sedeSeleccionada = d['sedeSeleccionada']
    solicitudId = d['solicitudId']

    print("desdeFechaSolicitud = ", d['desdeFechaSolicitud'])
    print("hastaFechaSolicitud = ", d['hastaFechaSolicitud'])
    print("voy a context0")
    # Ahora SolicitudDetalle
    print("voy a context1")
    context = {}
    print ("pase contex2")

    context['Username'] = username
    context['SedeSeleccionada'] = sedeSeleccionada
    context['NombreUsuario'] = nombreUsuario
    context['NombreSede'] = nombreSede
    context['solicitudId'] = solicitudId
    context['desdeFechaSolicitud'] = desdeFechaSolicitud
    context['hastaFechaSolicitud'] = hastaFechaSolicitud

    # Abro Conexion

    miConexion = psycopg2.connect(host="192.168.0.237", database="bd_solicitudes", port="5432", user="postgres", password="BD_m3d1c4l")
    # cur = miConexion.cursor()

    miConexion.set_client_encoding('LATIN1')
    cur = miConexion.cursor()
    cur.execute("set client_encoding='LATIN1';")
    print("voy comando")
    comando = 'select ord.id id, substring(to_char(ord."fechaElab",' + "'" +'yyyy-mm-dd' + "'" + '),1,10) fechaElab, ord."estadoOrden" estadoOrden ,ord.opciones opciones,ord."valorBruto" valorBruto,ord."descuento" descuento,ord."valorParcial" valorParcial, ord."iva" iva, ord."valorTotal" valorTotal,ord.observaciones observaciones,ord.area_id area, ord.proveedor_id proveedor,sol.item item,art.articulo, sol.iva iva,sol."recibidoOrdenCantidad" recibidoOrdenCantidad,sol."solicitadoOrdenCantidad" solicitadoOrdenCantidad ,sol."valorUnitario" valorUnitario	, sol."solicitadoOrdenValor" solicitadoOrdenValor,sol."recibidoOrdenValor" recibidoOrdenValor FROM solicitud_ordenesCompra ord, solicitud_solicitudesdetalle sol, mae_articulos art WHERE ord."fechaElab" >= ' + "'" + desdeFechaSolicitud + "'" + ' and ord."fechaElab" <= ' + "'" +  hastaFechaSolicitud + "'" + ' and ord.id = sol."ordenCompra_id" and sol.producto = art.codreg_articulo ORDER BY ord."fechaElab", sol.item'
    print("pase comando")
    cur.execute(comando)
    print(comando)

    ordenCompra = []

    for id, fechaElab, estadoOrden , opciones,valorBruto ,descuento, valorParcial,iva, valorTotal, observaciones,area,proveedor,item,\
        articulo, iva,recibidoOrdenCantidad,solicitadoOrdenCantidad,valorUnitario,  solicitadoOrdenValor, recibidoOrdenValor in cur.fetchall():
        ordenCompra.append(
            {"model": "solicitud.ordenescompra", "pk": id, "fields":
                {"id": id, "fechaElab":fechaElab, "estadoOrden": estadoOrden, "opciones": opciones, "valorBruto": valorBruto,
                  "valorParcial": valorParcial,"descuento":descuento,
                "iva": iva, "valorTotal": valorTotal, "observaciones": observaciones, "area": area, "proveedor": proveedor,
             "item": item, "articulo": articulo, "iva": iva,
             "recibidoOrdenCantidad": recibidoOrdenCantidad,"solicitadoOrdenCantidad": solicitadoOrdenCantidad ,
                 "valorUnitario":valorUnitario,"solicitadoOrdenValor":solicitadoOrdenValor , "recibidoOrdenValor": recibidoOrdenValor}})

    miConexion.close()
    print("ordenCompra")
    print(ordenCompra)

    # Cierro Conexion

    context['OrdenCompra'] = ordenCompra

    ## Voy a enviar estadosSolicitudes

    serialized1 = json.dumps(ordenCompra , cls=DecimalEncoder)

    print("Envio = ", json)

    return HttpResponse(serialized1, content_type='application/json')

class PostStoreOrdenesCompraConsulta(TemplateView):
        form_class = ordenesCompraForm
        template_name = 'Reportes/OrdenesCompraConsultaTrae1.html'

        def post(self, request):
            print("Entre a post de OrdenesCompraConsultas")

            context = {}

            return JsonResponse({'success': True, 'message': 'Orden Compra Created Successfully!'})

        def get_context_data(self, **kwargs):
            print("ENTRE POR EL GET_CONTEXT DEL VIEW de PostStoreOrdenesCOmpraConsulta : ")
            #solicitudId = self.request.GET["solicitudId"]

            username = self.request.GET['username']

            sedeSeleccionada = self.request.GET["sedeSeleccionada"]
            nombreUsuario = self.request.GET["nombreUsuario"]
            nombreSede = self.request.GET["nombreSede"]

            #print("SolictudId =", solicitudId)
            #print("username =", username)
            #print("sedeSeleccionada =", sedeSeleccionada)
            #print("nombreUsuario =", nombreUsuario)
            #print("nombreSede =", nombreSede)

            # context = super(PostStore, self).get_context_data(**kwargs)
            context = super().get_context_data(**kwargs)

            context['Username'] = username
            context['SedeSeleccionada'] = sedeSeleccionada
            context['NombreUsuario'] = nombreUsuario
            context['NombreSede'] = nombreSede
            #context['SolicitudId'] = solicitudId
            desdeFechaSolicitud = self.request.GET['desdeFechaSolicitud']
            hastaFechaSolicitud = self.request.GET['hastaFechaSolicitud']

            print("desdeFechaSolicitud = ", desdeFechaSolicitud)
            print("hastaFechaSolicitud = ", hastaFechaSolicitud)

            context['DesdeFechaSolicitud'] = desdeFechaSolicitud
            context['HastaFechaSolicitud'] = hastaFechaSolicitud

            return context


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)
## Fin Consilta Ordenes de Compras
