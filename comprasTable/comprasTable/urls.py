"""comprasTable URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf  import settings
from django.conf.urls.static import  static
from solicitud import views


urlpatterns = [
    path('admin/', admin.site.urls),
    # Acceso al Programa
    # Salidas de Menus

    path('chaining/', include('smart_selects.urls')),
    path('medicalCompras/', views.menuAcceso),
    path('validaAcceso/', views.validaAcceso),
    path('Solicitudes/<str:username>, <str:sedeSeleccionada>,<str:nombreUsuario>, <str:nombreSede>', views.Solicitudes),
    path('guardarSolicitudes/<str:username>, <str:sedeSeleccionada>,<str:nombreUsuario>, <str:fecha>, <str:nombreSede>, <str:area>',       views.guardarSolicitudes),
    path('GuardarValidacion/<str:username>, <str:sedeSeleccionada>,<str:nombreUsuario>, <str:nombreSede>, <str:enviovalidacionDef>',        views.GuardarValidacion),
    path('salir/', views.salir),

    # Validacion

    path('ValidacionConsulta/<str:username>, <str:sedeSeleccionada>,<str:nombreUsuario>, <str:nombreSede>', views.ValidacionConsulta),
    path('ValidacionConsulta/ValidacionBusca/', views.PostStoreValidacion.as_view(),name='post_storeValidacion'),
    path('fetch/>', views.load_dataValidacion, name='load_dataValidacion'),
    path('ValidacionConsulta/ValidacionBusca/', views.post_editValidacion, name='post_editValidacion'),
    path('ValidacionConsulta/ValidacionBusca/postValidacion/<int:id>,<str:username>,<str:sedeSeleccionada>,<str:nombreUsuario>,<str:nombreSede>,<str:solicitudId>/edit/', views.post_editValidacion, name='post_editValidacion'),
    path('load_dataValidacion/<str:solicitudId>', views.load_dataValidacion, name='load_dataValidacion'),
    path('postValidacion/<int:id>/delete', views.post_deleteValidacion, name='post_deleteValidacion'),
    path('ValidacionConsulta/ValidacionBusca/postValidacion/<int:id>/delete', views.post_deleteValidacion, name='post_deleteValidacion'),

    # Fin Validacion


    # Almacen



    # Fin Almacen

    # Compras



    # Fin Compras


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Añadir
admin.site.site_header = 'Administracion Medical Compras'
admin.site.site_title = "Portal de Medical Compras"
admin.site.index_title = "Bienvenidos al portal de administración Medical Compras"

