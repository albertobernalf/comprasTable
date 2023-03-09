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


import csv as aliascsv


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

def OrdenesCompraConsulta(request , username, sedeSeleccionada, nombreUsuario, nombreSede):
    pass
    print ("Entre a consulta Ordenes de Compra solicitud");
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
        valeQuerySet = SolicitudesDetalle.objects.filter(solicitud_id=solicitudId)

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
                    entragaMercancia=form.cleaned_data['entragaMercancia'],
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

                ## DESDE AQUI RUTINA ACTUALIZA ITEM EN SOLICITUD DETALLE

                # Fin consigo cuantos items tienen la solicitud

                # Imprimo en un for los valores de los items

                for campo in range(1, totalRegistros+1):
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

                    ## Fin UPDATE
                ## HASTA AQUI RUTINA ACTUALIZA ITEM EN SOLICITUD DETALLE

                return render(request, self.template_name, context)
                #return HttpResponse('Orden de Compra Created Successfully!')
                #return HttpResponseRedirect(reverse('post_storeOrdenesCompra/solicitudId=22'))
                #return JsonResponse({'success': True, 'message': 'Orden de Compra Actualizada Successfully!'})
            except:

                return render(request, self.template_name,{'success': True, 'message': 'Orden de Compra Created Successfully!'})

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
            comando = 'SELECT sol.id id,sol.item item, sol.descripcion_id, des.nombre descripcion, tip.nombre tipo ,sol.producto producto,  art.articulo nombre_producto ,pres.nombre presentacion, sol.iva iva ,sol."recibidoOrdenCantidad" recibidoOrdenCantidad,sol."recibidoOrdenValor" recibidoOrdenValor,sol."solicitadoOrdenCantidad" solicitadoOrdenCantidad,sol."solicitadoOrdenValor" solicitadoOrdenValor,sol."valorUnitario" valorUnitario FROM public.solicitud_solicitudesDetalle sol , public.solicitud_descripcioncompra des, public.solicitud_tiposcompra tip, public.solicitud_presentacion pres, public.mae_articulos art    , public.solicitud_usuarios usu , public.solicitud_usuarios usu1 , public.solicitud_usuarios usu2,  public.solicitud_estadosvalidacion est , public.solicitud_estadosvalidacion est1 , public.solicitud_estadosvalidacion est2  WHERE sol.solicitud_id = ' + solicitudId + ' AND sol."estadosAlmacen_id" = 3 AND  sol."ordenCompra_id"=0 AND des.id = sol.descripcion_id and tip.id = sol."tiposCompra_id" and pres.id = sol.presentacion_id and art.codreg_articulo = sol.producto and  usu2.id = sol."usuarioResponsableCompra_id"   and usu1.id = sol."usuarioResponsableAlmacen_id" and usu.id = sol."usuarioResponsableValidacion_id" and est1.id = sol."estadosAlmacen_id" and est2.id = "estadosCompras_id"  and est.id = sol."estadosValidacion_id" ORDER BY sol.item'
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

            # {"model": "solicitud.solicitudesdetalle", "pk": 6, "fields":

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

def CreaCsv(request):

    response = HttpResponse(content_type='text/csv')

    nombreReporteFinal = "OrdenCompra" + ".csv"
    response['Content-Disposition'] = 'attachment; filename= ' + nombreReporteFinal

    myFile = open(nombreReporteFinal, 'w')

    with myFile:
        writer = aliascsv.writer(response, myFile)

    response.write(u'\ufeff'.encode('utf8'))

    # write column headers in sheet

    #for row in rows:
    #     row_num = row_num + 1
    #     campo = ""
    #     campoTot = ""

    #        for col in range(len(lasColumnas)):
    #            campo = row[col]

    #            campoTot = campoTot + str(campo) + ","

    #            writer.writerow([smart_str(campoTot), ])



# Fin Create your views here. para Ordenes de Compras

