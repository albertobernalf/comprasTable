-- Script de cargue de datos inicial :

-- tengo que subir bien solicitud_sedescompra para que me siba bien areas,


-- translate(btrim(direccionl::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text)

select * from imhotep_usuarios;

select * from imhotep_sedes;
select * from solicitud_sedesCompra;
--delete from solicitud_sedesCompra;

--delete from solicitud_sedesCompra;

--Sedes: Problema
create extension dblink;

SELECT dblink_connect ('mycon1','host=192.168.0.237 user=postgres password=BD_m3d1c4l dbname=bd_imhotep') ;

insert into solicitud_sedescompra (codreg_sede, nom_sede, codreg_ips,direccion,telefono,departamento, municipio, zona , sede, estadoReg)
SELECT codreg_sede, nom_sede, codreg_ips,direccion,telefono,departamento, municipio, zona , sede, 'A'
FROM dblink('mycon1', 'SELECT codreg_sede, nom_sede, codreg_ips,direccion,telefono,departamento, municipio, zona , sede   FROM imhotep_sedes'::text)
 c(codreg_sede character  (10), nom_sede character (30), codreg_ips character (15), direccion character (200),   telefono character (120), departamento character varying (120), municipio character varying (120),zona character varying (120),sede character varying (120) );


insert into solicitud_sedesCompra(codreg_sede ,  nom_sede ,  codreg_ips,  direccion ,  telefono ,  departamento ,  municipio ,  zona ,  sede ,  estadoreg)

select codreg_sede ,  translate(btrim(nom_sede::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text)  ,  codreg_ips,  translate(btrim(direccion::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text) ,  translate(btrim(telefono::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text) ,  translate(btrim(departamento::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text) ,  translate(btrim(municipio::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text) ,translate(btrim(zona::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text) ,  sede ,  'A'
from imhotep_sedes;


update solicitud_sedesCompra set direccion = 'Calle 36 Sur No. 77-33 Barrio Kennedy'  where codreg_sede = 'MK' ;
update solicitud_sedesCompra set direccion = 'Avenida Carrera 45 # 94 - 31/39 (Autopista Norte)' where codreg_sede = 'MN' ;
update solicitud_sedesCompra set direccion = 'Cra 66A #4G-86' where codreg_sede = 'AM' ;
update solicitud_sedesCompra set direccion = 'Cl. 1d # 17A - 35' where codreg_sede = 'SJ' ;
update solicitud_sedesCompra set direccion = 'Cra 102 # 17-49/57' where codreg_sede = 'SF' ;
update solicitud_sedesCompra set direccion = 'Cr 21 No 169 15/25 Bodega 2' where codreg_sede = 'MT' ;

--52973594
-- 12345
 SELECT t.codreg_poblacion id, t.desc_poblacion nombre FROM public.mae_poblacion t
   
-- Usuarios : Problema
delete from solicitud_usuarios;
select *  from solicitud_usuarios;

SELECT dblink_connect ('mycon1','host=192.168.0.237 user=postgres password=BD_m3d1c4l dbname=bd_imhotep') ;
insert into solicitud_usuarios values (1,'11111','NO APLICA','1', 'NO APLICA','A',7);

insert into solicitud_usuarios (num_identificacion, nom_usuario, clave_usuario,carg_usuario, estadoReg,sede_id)
SELECT translate(btrim(num_identificacion::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text)  , translate(btrim(nom_usuario::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text) , translate(btrim(clave_usuario::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text) ,translate(btrim(carg_usuario::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text)  , 'A',8
FROM dblink('mycon1', 'SELECT num_identificacion, nom_usuario, clave_usuario,carg_usuario FROM imhotep_usuarios'::text)
 c(num_identificacion character varying (30), nom_usuario character varying (150), clave_usuario character varying (20), carg_usuario character varying (80) )
where  num_identificacion in ('7548543','35195339','52046796','52956447','80760858','65761741','79307851','65822566','79646248','1032381487','64868812','49754113','55238662','52148511','52888300','52869056','1072657156','52908843','1016069653','51892844','1014281484','1013611750','52735753','1102388730','52161946','52233695',
'19456950','79717519','1014245115','53139189','1024567274','1019057514','1014250241','79690980','52973594','1010202398','1022981421','52027259','53079814','1032367193','1026281960',
'1010182068','52982328','53093836','1013605270','79830038','1110446284','1012329750','1012369594','1020805372','16788445','80738164','53026159','1013614781');



52735753  // 1225
-- OJO ESTE USUARIO ES COMODIN PARA LOS DEFAULTS

-- Problema no inserta todo por caracteres especiales, tildes caracteres extraños etc.

 B4s32023*

-- Areas. OK

select * from mae_areas;
select * from solicitud_sedesCompra;
select * from solicitud_areas;
delete  from solicitud_areas;


insert into solicitud_areas (area,estadoreg,sede_id)
select  translate(btrim(areas.area::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text),'A', sedes.id
from mae_areas areas, solicitud_sedesCompra sedes
where areas.sede = sedes.sede;

select * from solicitud_areas;
select * from mae_areas;

insert into solicitud_areas (area,estadoReg, sede_id)
SELECT translate(btrim(area::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text), 'A', 8
FROM dblink('mycon1', 'SELECT area   FROM mae_areas'::text)
 c(area character varying  (80));

select * from solicitud_usuarios;
B4s32023*




delete from public.solicitud_solicitudes;;
delete from public.solicitud_solicitudesdetalle;;

select * from public.solicitud_solicitudes;
select * from public.solicitud_solicitudesdetalle;

INSERT INTO solicitud_solicitudesdetalle ( item ,  cantidad ,  justificacion ,  "especificacionesTecnicas" ,  "especificacionesAlmacen" ,  "especificacionesCompras" ,  estadoreg ,             descripcion_id, "estadosAlmacen_id", "estadosCompras_id", "estadosSolicitud_id", "estadosValidacion_id", solicitud_id, "tiposCompra_id", "usuarioResponsableValidacion_id", "entregadoAlmacen", presentacion_id, "solicitadoAlmacen", producto )  VALUES(1, 10,'parayap','','','','A',1, 1, 1, 1, 1, 11, 6,17,0,6, 0,'COMPU001'  )

select * from public.solicitud_presentacion;
select * from public.solicitud_tiposcompra;


INSERT INTO solicitud_solicitudesdetalle ( item ,  cantidad ,  justificacion ,  "especificacionesTecnicas" ,  "especificacionesAlmacen" ,  "especificacionesCompras" ,  estadoreg ,             descripcion_id, "estadosAlmacen_id", "estadosCompras_id", "estadosSolicitud_id", "estadosValidacion_id", solicitud_id, "tiposCompra_id", "usuarioResponsableValidacion_id", "entregadoAlmacen", presentacion_id, "solicitadoAlmacen", producto, , "usuarioResponsableCompra", , "usuarioResponsableAlmacen_id" )  VALUES(1, 10,'para yap','','','','A',1, 1, 1, 1, 1, 17, 6,17,0,1, 0,'COMPU001'  )

SELECT dblink_connect ('mycon1','host=192.168.0.237 user=postgres password=BD_m3d1c4l dbname=bd_imhotep') ;


create table mae_articulos (codreg_articulo,articulo)
AS
SELECT codreg_articulo codreg_articulo,  translate(btrim(articulo::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text)      articulo   
FROM dblink('mycon1', 'SELECT codreg_articulo, articulo , activo  FROM mae_articulos'::text)
 c(codreg_articulo character varying  (30), articulo  character varying  (300) , activo character(1))
where activo='S' ;

select * 
FROM public.mae_articulos t 
where activo='S' 
order by t.articulo


SELECT translate(btrim(area::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text), 'A', 8
FROM dblink('mycon1', 'SELECT area   FROM mae_areas'::text)
 c(area character varying  (80));




-- Proveedores -- Problemas  UTF8

select * from mae_proovedores;

create extension dblink;
 
SELECT dblink_connect ('mycon1','host=192.168.0.237 user=postgres password=BD_m3d1c4l dbname=bd_imhotep') ;



select * from solicitud_proveedores ;
drop table proveedores_2023;

CREATE TABLE proveedores_2023 (codreg_proveedor  character varying(50), proveedor character varying(80), correo character varying(200),estado character varying(1), direccion character varying(80), nit character varying(30),telefono  character varying(30));
 
-- Para copiar los datos desde Excel a la Tavbla

select * from proveedores_2023 where direccion is null;
update  proveedores_2023 set direccion = '.' where direccion is null;
select * from proveedores_2023 where telefono is null;
update  proveedores_2023 set telefono = '0' where telefono ='.';


select * from solicitud_proveedores;

COPY proveedores_2023  FROM '/mnt/sda3/PostgreSQL/9.4/ComprasTable/proveedores.csv' HEADER CSV DELIMITER ';';

insert into solicitud_proveedores (codreg_proveedor, proveedor,correo,estadoReg, direccion, nit, telefono)
select codreg_proveedor, translate(btrim(proveedor::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text),
			 translate(btrim(correo::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text),
			'A', 
			translate(btrim(direccion::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text),
			translate(btrim(nit::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text),
			translate(btrim(telefono::text),'óÓáÁéÉíÍúÚñÑ'::text,'oOaAeEiIuUnN'::text)
from proveedores_2023;




select * from proveedores_2023;  -- 159 reg

-- Se valida

INSERT INTO solicitud_solicitudesdetalle ( item ,  cantidad ,  justificacion ,  "especificacionesTecnicas" ,  "especificacionesAlmacen" ,  "especificacionesCompras" ,  estadoreg ,             descripcion_id, "estadosAlmacen_id", "estadosCompras_id", "estadosSolicitud_id", "estadosValidacion_id", solicitud_id, "tiposCompra_id", "usuarioResponsableValidacion_id", "entregadoAlmacen", presentacion_id, "solicitadoAlmacen", producto,"usuarioResponsableAlmacen_id","usuarioResponsableCompra_id",iva, "recibidoOrdenCantidad","recibidoOrdenValor", "solicitadoOrdenCantidad", "solicitadoOrdenValor", "valorUnitario")  VALUES(1, 10,'se necesitan','','','','A',1, 1, 1, 1, 1, 21, 4,342,0,5, 0,'COMPU001',1,1,0,0,0,0,0,0  )
