# app.py
from flask import (Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response, Response, send_from_directory, send_file)
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import json
from oauth2client.service_account import ServiceAccountCredentials
import io
import xlwt
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import socket
import pdfkit

# ---------------------------------------------------------------------------------
# -------------CONFIGURACIÓN DE FOLDER PARA COMPROBANTES---------
UPLOAD_FOLDER = "static/comprobantes/"
# -------------CONFIGURACION BASE DE DATOS-----------------------
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
app = Flask(__name__)
app.secret_key = "^A%DJAJU^JJ123"
# if ip_address == "10.2.1.10":
#     app.config["MYSQL_HOST"] = "192.168.16.231"
#     app.config["MYSQL_USER"] = "juanrojas"
#     app.config["MYSQL_PASSWORD"] = ".2pMvGh77QsgjGGA"
#     app.config["MYSQL_DB"] = "prestamos_db"
# else:
    # app.config["MYSQL_HOST"] = "10.3.1.110"
    # app.config["MYSQL_USER"] = "root"
    # app.config["MYSQL_PASSWORD"] = "WNeqRzh!nHrfA9d**K!^"
    # app.config["MYSQL_DB"] = "prestamos_db_pruebas"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "prestamos_db_pruebas"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
mysql = MySQL(app)
# --------------------------------------------------------------


# -------------FUNCIONES AUXILIARES-----------------------------
def consultar_externos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # trae los registros de prestamo de la BD MySQL
    prestamo_tipo = "%" + "Prestamo externo" + "%"
    # cur.execute("SELECT * FROM registros WHERE prestamo LIKE %s and estado=%s",(prestamo_tipo,"Activo"))

    cur.execute(
        "SELECT *, registros.id AS id_registro FROM supervisor RIGHT JOIN registros ON supervisor.registros_id = registros.id WHERE prestamo LIKE %s and estado=%s",
        (prestamo_tipo, "Activo"),
    )
    data = cur.fetchall()
    cur.close()
    return data


def comprobar_permisos(rol):
    if rol == "admin":
        if "permisos" in session and session["permisos"] == "admin":
            return True
        else:
            return False
    elif rol == "user":
        if "permisos" in session and session["permisos"] == "user":
            return True
        else:
            return False
    elif rol == "checker":
        if "permisos" in session and session["permisos"] == "checker":
            return True
        else:
            return False
    return False


# función para traer dependencias
def getDependencias():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM dependencias")
    arrayValoresDependencias = cursor.fetchall()
    return arrayValoresDependencias


# función para traer aulas


def getAulas():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM aulas")
    arrayValoresAulas = cursor.fetchall()
    return arrayValoresAulas


# función para traer horarios
def getHorarios():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM horarios")
    arrayValoresHorario = cursor.fetchall()
    return arrayValoresHorario


# función para traer equipos medios
def getEquiposMedios():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM equipos")
    arrayValoresHorario = cursor.fetchall()
    return arrayValoresHorario


def renderTemplateIndex(template, tipoPersona):
    if "nombre" in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # trae los registros de prestamo de la BD MySQL
        cur.execute(
            "SELECT * FROM registros WHERE depPrestamo=%s and tipoPersona=%s and estado=%s",
            (session["dependencia"], tipoPersona, "Activo"),
        )
        data = cur.fetchall()
        cur.close()
        temp = template + ".html"
        return render_template(
            temp,
            registros=data,
            permisos=session["permisos"],
            nombre=session["nombre"],
            dependencias=getDependencias(),
            aulas=getAulas(),
            horarios=getHorarios(),
            equipos=getEquiposMedios(),
        )

    else:
        return render_template("login.html")


def getInfoPersonasFormBD(tabla, cedula):
    # traigo los registros pertenecientes a las personas
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if tabla == "profesores":
        cur.execute("SELECT * FROM profesores WHERE documento=%s", [cedula])
    elif tabla == "administrativos":
        cur.execute("SELECT * FROM administrativos WHERE documento=%s", [cedula])
    elif tabla == "estudiantes":
        cur.execute("SELECT * FROM estudiantes WHERE documento=%s", [cedula])
    arrayValoresPersonasFiltered = cur.fetchall()
    return json.dumps(arrayValoresPersonasFiltered)


def cargar_comprobante():
    if "file" not in request.files:
        flash("Sin partes del archivo")
    file = request.files["file"]
    if file.filename == "":
        flash("Ningún comprobante adjuntado")
    else:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        flash("Comprobante adjuntado correctamente")
    return file.filename


# -----------------------------FUNCIONES DE RUTAS-------------------------------------------------------------
# ruta inicial
@app.route("/")
def home():
    if "nombre" in session:
        if comprobar_permisos("admin") or comprobar_permisos("user"):
            # retorna la plantilla con los datos guardados
            return render_template("home.html")
        elif comprobar_permisos("checker"):
            return render_template(
                "prestamosExternos.html", registros=consultar_externos()
            )
    else:
        # retorna la plantilla de login si no está logeado
        return render_template("login.html")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# ruta para comprobar prestamos
@app.route("/mostrarEquiposSalida")
def mostrarEquiposSalida():
    if "nombre" in session and comprobar_permisos("checker"):
        temp = "prestamosExternos.html"
        return render_template(temp, registros=consultar_externos())

    else:
        return render_template("login.html")


# ruta docentes
@app.route("/indexDocentes")
def indexDocentes():
    if comprobar_permisos("admin") or comprobar_permisos("user"):
        toRender = renderTemplateIndex("indexDocentes", "DOCENTE")
        return toRender
    else:
        return render_template("not_allowed.html")


# ruta estudiantes.
@app.route("/indexEstudiantes")
def indexEstudiantes():
    if comprobar_permisos("admin") or comprobar_permisos("user"):
        toRender = renderTemplateIndex("indexEstudiantes", "ESTUDIANTE")
        return toRender
    else:
        return render_template("not_allowed.html")


# ruta contratistas
@app.route("/indexContratistas")
def indexContratistas():
    if comprobar_permisos("admin") or comprobar_permisos("user"):
        toRender = renderTemplateIndex("indexContratistas", "CONTRATISTA")
        return toRender
    else:
        return render_template("not_allowed.html")


# ruta información docentes
@app.route("/getInfoDocente/<cedula>", methods=["GET", "POST"])
def getInfoDocente(cedula):
    info = getInfoPersonasFormBD("profesores", cedula)
    return info


# ruta información contratista
@app.route("/getInfoContratista/<cedula>", methods=["GET", "POST"])
def getInfoContratista(cedula):
    info = getInfoPersonasFormBD("administrativos", cedula)
    return info


# ruta información estudiantes
@app.route("/getInfoEstudiante/<cedula>", methods=["GET", "POST"])
def getInfoEstudiante(cedula):
    info = getInfoPersonasFormBD("estudiantes", cedula)
    return info


# ruta para obtener info del equipo
@app.route("/getInfoEquipo/<codInventario>", methods=["GET", "POST"])
def getInfoEquipo(codInventario):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM equipos WHERE codigo=%s", [codInventario])
    infoEquipo = cur.fetchall()
    return json.dumps(infoEquipo)


# ruta de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if "nombre" in session:
        if comprobar_permisos("user") or comprobar_permisos("admin"):
            return redirect(url_for("home"))
        elif comprobar_permisos("checker"):
            return render_template(
                "prestamosExternos.html", registros=consultar_externos()
            )
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"].encode("utf-8")

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = curl.fetchone()
        curl.close()
        try:
            if user is None:
                return "El usuario ingresado no fue encontrado"
            elif bcrypt.hashpw(password, user["password"].encode("utf-8")) == user[
                "password"
            ].encode("utf-8"):
                session["nombre"] = user["nombre"]
                session["dependencia"] = user["dependencia"]
                session["permisos"] = user["permisos"]
                if comprobar_permisos("user") or comprobar_permisos("admin"):
                    return render_template("home.html", nombre=session["nombre"])
                elif comprobar_permisos("checker"):
                    return render_template(
                        "prestamosExternos.html",
                        registros=consultar_externos(),
                        nombre=session["nombre"],
                    )
            else:
                return "El email o password ingresados son incorrectos"
        except Exception as e:
            return e
    else:
        return render_template("login.html")


# ruta de cerrar sesión
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ruta para registrar usuario
@app.route("/registerUser", methods=["GET", "POST"])
def registerUser():
    # atiende petición por GET
    if request.method == "GET":
        if "nombre" in session:
            if comprobar_permisos("admin"):
                return render_template(
                    "registerUser.html", dependencias=getDependencias()
                )
            else:
                return render_template("not_allowed.html")
        else:
            return redirect(url_for("login"))
    # atiende petición por POST
    else:
        if comprobar_permisos("admin"):
            nombre = request.form["name"]
            email = request.form["email"]
            password = request.form["password"].encode("utf-8")
            dependencia = request.form.get("selectDependenciaSolicitante")
            permisos = request.form.get("selectPermisos")
            hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO users (nombre, email, password,dependencia,permisos) VALUES (%s,%s,%s,%s,%s)",
                (
                    nombre,
                    email,
                    hash_password,
                    dependencia,
                    permisos,
                ),
            )
            flash("Usuario agregado correctamente.")
            mysql.connection.commit()
            return redirect(url_for("home"))


# ruta para cargar novedades por carga por excel
@app.route("/cargarNovedades", methods=["GET", "POST"])
def cargarNovedades():
    # atiende petición por GET
    if request.method == "GET":
        if "nombre" in session:
            return render_template("cargarNovedades.html")
        else:
            return redirect(url_for("login"))
    if (
        request.method == "POST"
        and comprobar_permisos("admin")
        or comprobar_permisos("user")
    ):
        upload_file = request.files["upload-file"]
        try:
            if upload_file.filename != "":
                data = pd.read_excel(upload_file)
                data_list = data.values.tolist()
                data_to_instert = []
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                for lista in data_list:
                    persona_entrega = session["nombre"]
                    tipo_persona = "CONTRATISTA"
                    usuario = lista[1]
                    documento = lista[0]
                    dependencia_novedad = session["dependencia"]
                    dependencia_solicitante = ""
                    observaciones = ""
                    novedad = (
                        "Información de la novedad: "
                        + str(lista[2])
                        + " Observaciones: "
                        + str(lista[3])
                    )
                    estado_novedad = "Activo"
                    tupla_registros = (
                        dt_string,
                        usuario,
                        tipo_persona,
                        documento,
                        dependencia_novedad,
                        dependencia_solicitante,
                        novedad,
                        estado_novedad,
                        observaciones,
                        dt_string,
                        persona_entrega,
                    )
                    data_to_instert.append(tupla_registros)
                    print(data_to_instert)

                mySql_insert_query = """INSERT INTO registros (fechaPrestamo, nombre, tipoPersona, cedula, depPrestamo, depSolicitante, prestamo, estado, observaciones, fechaEntrega, personaEntrega) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cur = mysql.connection.cursor()
                cur.executemany(mySql_insert_query, data_to_instert)
                mysql.connection.commit()
                flash("Registros agregados correctamente.", "success")
        except Exception as e:
            print(e)
            flash(
                "Ocurrió un error al intentar subir la información. Por favor verifique e intente nuevamente.",
                "danger",
            )
        return render_template("cargarNovedades.html")


# ESTA FUNCIÓN PERMITE REGSITRAR EL NOMBRE DEL SUPERVISOR
@app.route("/editar_nombreSupervisor/<id>", methods=["GET", "POST"])
def EDITAR_NOMBRE_SUPERVISOR(id):
    nombre = request.form.get("nombre")
    cur = mysql.connection.cursor()

    # Verificar si el registro ya existe
    cur.execute("SELECT * FROM supervisor WHERE registros_id = %s", (id,))
    existe_supervisor = cur.fetchone()
    if existe_supervisor:
        # El registro ya existe, realizar la actualización
        cur.execute(
            "UPDATE supervisor SET nombre_supervisor = %s WHERE registros_id = %s",
            (nombre, id),
        )
    else:
        # El registro no existe, realizar la inserción
        cur.execute(
            "INSERT INTO supervisor (registros_id, nombre_supervisor) VALUES (%s, %s)",
            (id, nombre),
        )

    mysql.connection.commit()

    return render_template("prestamosExternos.html", registros=consultar_externos())


# ---------------------------------------------------------------------------------------------------------------------------------


@app.route("/pazsalvo")
def pazsalvo():
    return render_template("paz_salvo.html")


@app.route("/consulta_all", methods=["POST"])
def consulta_all():
    mensaje_error = None
    cedula = request.form.get("cedula")
    dependencia = request.form.get("dependencia")

    if not cedula or not dependencia:
        mensaje_error = "Rellene todos los campos antes de enviar el formulario."
    else:
        registro_administrativo = buscar_en_base_de_datos(cedula, dependencia)
        if registro_administrativo:
            estado_registro = verificar_estado_activo(cedula)
            if estado_registro == "No existen registros activos para la cédula.":  # La consulta de registros activos está vacía
                return render_template(
                    "consulta_allowed.html",
                    mensaje="Está a paz y salvo con la institución.",
                    resultado=registro_administrativo,
                )
            elif estado_registro == "Existen registros activos para la cédula.":
                # Aquí, además del resultado, enviamos el parámetro 'registro'
                registro = obtener_registro_cedula_activo(cedula)
                return render_template(
                    "consulta_not_allowed.html",
                    resultado=registro_administrativo,
                    registros=registro
                )
            else:
                mensaje_error = estado_registro  # Mensaje de error personalizado
        else:
            mensaje_error = "No se encontró un registro administrativo."

    return render_template("paz_salvo.html", mensaje_error=mensaje_error)



# Esta función busca los datos en la tabla "administrativos".
def buscar_en_base_de_datos(cedula, dependencia):
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        query = "SELECT * FROM administrativos WHERE documento = %s AND dependencia = %s"
        cursor.execute(query, (cedula, dependencia))
        registro = cursor.fetchone()
        cursor.close()
        return registro
    except Exception as e:
        print("Error al buscar en la tabla 'administrativos':", str(e))
        return None

# Esta función verifica el estado en la tabla "registros".
def verificar_estado_activo(cedula):
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        query = "SELECT estado FROM registros WHERE cedula = %s AND estado = 'Activo'"
        cursor.execute(query, (cedula,))
        registros_activos = cursor.fetchall()
        cursor.close()
        if registros_activos:
            return "Existen registros activos para la cédula."
        else:
            return "No existen registros activos para la cédula."
    except Exception as e:
        print("Error al verificar el estado en la tabla 'registros':", str(e))
        return None
    
def obtener_registro_cedula_activo(cedula):
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        query = "SELECT * FROM registros WHERE cedula = %s AND estado = 'Activo'"
        cursor.execute(query, (cedula,))
        registro = cursor.fetchall()
        cursor.close()
        return registro
    except Exception as e:
        print("Error al obtener el registro: ", str(e))
        return None



@app.route("/generar_formato", methods=["POST"])
def generar_formato():
    contrato = request.form[
        "contrato"
    ]  # Obten el valor del contrato desde el formulario
    documento = request.form[
        "documento"
    ]  # Obten el valor del documento desde el formulario
    nombre = request.form["nombre"]  # Obten el valor del nombre desde el formulario

    html_file = "templates/plantilla_pazsalvo.html"
    options = {"page-size": "A4", "orientation": "Portrait"}
    pdf_file = "Formato_paz_salvo.pdf"

    # Abre la plantilla HTML y reemplaza los marcadores {{ contrato }} y {{ documento }}
    with open(html_file, "r") as file:
        content = file.read()
        content = content.replace("{{ contrato }}", contrato)
        content = content.replace("{{ resultado.documento }}", documento)
        content = content.replace("{{ resultado.nombre }}", nombre)

    # Crea un nuevo archivo HTML con los valores del contrato y documento
    new_html_file = "templates/plantilla_pazsalvo_con_datos.html"
    with open(new_html_file, "w") as file:
        file.write(content)

    # Convierte el nuevo HTML a PDF
    pdfkit.from_file(new_html_file, pdf_file, options=options)

    return send_file(pdf_file, as_attachment=False)


@app.route("/generar_certificado", methods=["POST"])
def generar_certificado():
    contrato = request.form[
        "contrato"
    ]  # Obten el valor del contrato desde el formulario
    documento = request.form[
        "documento"
    ]  # Obten el valor del documento desde el formulario
    nombre = request.form["nombre"]  # Obten el valor del nombre desde el formulario

    html_file = "templates/plantilla_certificado.html"
    options = {"page-size": "A4", "orientation": "Portrait"}
    pdf_file = "Certificado_paz_salvo.pdf"

    # Abre la plantilla HTML y reemplaza los marcadores {{ contrato }} y {{ documento }}
    with open(html_file, "r") as file:
        content = file.read()
        content = content.replace("{{ contrato }}", contrato)
        content = content.replace("{{ resultado.documento }}", documento)
        content = content.replace("{{ resultado.nombre }}", nombre)

    # Crea un nuevo archivo HTML con los valores del contrato y documento
    new_html_file = "templates/plantilla_certificado_con_datos.html"
    with open(new_html_file, "w") as file:
        file.write(content)

    # Convierte el nuevo HTML a PDF
    pdfkit.from_file(new_html_file, pdf_file, options=options)

    return send_file(pdf_file, as_attachment=False)


# ----------------------------------------------------------------------------------------------------------------------


# Funcion para restablecer contraseña
@app.route("/resetPassword", methods=["POST"])
def resetPassword():
    # atiende petición por POST
    if request.method == "POST" and comprobar_permisos("admin"):
        email = request.form["email"]
        password = request.form["password"].encode("utf-8")
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE users SET password = %s WHERE email = %s", (hash_password, email)
        )
        flash("Contraseña cambiada exitosamente.")
        mysql.connection.commit()
    return redirect(url_for("home"))


@app.route("/add_record", methods=["POST"])
def add_record():
    if (
        request.method == "POST"
        and comprobar_permisos("admin")
        or comprobar_permisos("user")
    ):
        nombre = request.form["nombreSolic"]
        # captura la cédula dependiendo del indentificador usado
        tipoPersona = ""
        urlToRedirect = ""
        if "cedDocente" in request.form:
            cedula = request.form["cedDocente"]
            tipoPersona = "DOCENTE"
            urlToRedirect = "indexDocentes"
        elif "cedEstudiante" in request.form:
            cedula = request.form["cedEstudiante"]
            tipoPersona = "ESTUDIANTE"
            urlToRedirect = "indexEstudiantes"
        elif "cedContratistas" in request.form:
            cedula = request.form["cedContratistas"]
            tipoPersona = "CONTRATISTA"
            urlToRedirect = "indexContratistas"
        dependenciaSolicitante = request.form["selectDependenciaSolicitante"]
        dependenciaPrestamo = session["dependencia"]
        personaEntrega = session["nombre"]
        prestamo = request.form.getlist("items")
        filename = cargar_comprobante()
        estado = "Activo"
        data = []
        for pres in prestamo:
            splitPrest = pres.split("Observaciones:")
            observaciones = splitPrest[1]
            row = (
                nombre,
                tipoPersona,
                cedula,
                dependenciaSolicitante,
                dependenciaPrestamo,
                pres,
                estado,
                observaciones,
                personaEntrega,
                filename,
            )
            data.append(row)
        cur = mysql.connection.cursor()
        if len(prestamo) >= 1:
            sql = "INSERT INTO registros (nombre,tipoPersona, cedula, depSolicitante,depPrestamo,prestamo,estado,observaciones,personaEntrega,comprobante) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.executemany(sql, data)
            mysql.connection.commit()
            flash("¡Registro agregado correctamente!")
        else:
            flash("¡No se han creado registros debido a que no agregaron artículo.!")
        return redirect(url_for(urlToRedirect))


@app.route("/updateRecords", methods=["POST"])
def updateRecords():
    if (
        request.method == "POST"
        and comprobar_permisos("admin")
        or comprobar_permisos("user")
    ):
        ids = request.form.getlist("selected[]")
        estado = "Inactivo"
        data = []
        personaRecibe = session["nombre"]
        for id in ids:
            row = (estado, personaRecibe, id)
            data.append(row)
        print(data)
        cur = mysql.connection.cursor()
        cur.executemany(
            "UPDATE registros SET estado=%s,fechaEntrega=current_timestamp,personaRecibe=%s WHERE id = %s",
            data,
        )
        flash("Registro actualizado correctamente")
        mysql.connection.commit()
        return redirect(url_for("indexDocentes"))


@app.route("/createDoc", methods=["POST"])
def createDoc():
    if (
        request.method == "POST"
        and comprobar_permisos("admin")
        or comprobar_permisos("user")
    ):
        cedula = request.form["cedulaDoc"]
        nombre = request.form["nombreDoc"]
        dep = request.form["depDoc"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO profesores (documento, nombre, dependencia) VALUES (%s,%s,%s)",
            (
                cedula,
                nombre,
                dep,
            ),
        )
        mysql.connection.commit()
        return redirect(url_for("indexDocentes"))


@app.route("/createCont", methods=["POST"])
def createCont():
    if (
        request.method == "POST"
        and comprobar_permisos("admin")
        or comprobar_permisos("user")
    ):
        cedula = request.form["cedulaCont"]
        nombre = request.form["nombreCont"]
        dep = request.form["depCont"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO administrativos (documento, nombre, dependencia) VALUES (%s,%s,%s)",
            (
                cedula,
                nombre,
                dep,
            ),
        )
        mysql.connection.commit()
        return redirect(url_for("indexContratistas"))


@app.route("/createEst", methods=["POST"])
def createEst():
    if (
        request.method == "POST"
        and comprobar_permisos("admin")
        or comprobar_permisos("user")
    ):
        cedula = request.form["cedulaEst"]
        nombre = request.form["nombreEst"]
        dep = request.form["depEst"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO estudiantes (documento, nombre, dependencia) VALUES (%s,%s,%s)",
            (
                cedula,
                nombre,
                dep,
            ),
        )
        mysql.connection.commit()
        return redirect(url_for("indexEstudiantes"))


@app.route(
    "/download/report/<fechaInicio>/<fechaFin>/<tipoPersona>", methods=["GET", "POST"]
)
def download_report(fechaInicio, fechaFin, tipoPersona):
    if (
        request.method == "GET"
        and comprobar_permisos("admin")
        or comprobar_permisos("user")
    ):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if tipoPersona == "DOCENTE":
            cursor.execute(
                "SELECT * FROM registros WHERE tipoPersona = 'DOCENTE' AND fechaPrestamo>=%s AND fechaPrestamo<=%s",
                (fechaInicio, fechaFin),
            )
        elif tipoPersona == "CONTRATISTA":
            cursor.execute(
                "SELECT * FROM registros WHERE estado = 'Activo' AND tipoPersona = 'CONTRATISTA' AND fechaPrestamo>=%s AND fechaPrestamo<=%s",
                (fechaInicio, fechaFin),
            )
        result = cursor.fetchall()
        # output in bytes
        output = io.BytesIO()
        # create WorkBook object
        workbook = xlwt.Workbook()
        # add a sheet
        if tipoPersona == "DOCENTE":
            sh = workbook.add_sheet("Reporte_docentes")
        elif tipoPersona == "CONTRATISTA":
            sh = workbook.add_sheet("Reporte_contratistas")
        # add headers
        sh.write(0, 0, "Id")
        style = xlwt.XFStyle()
        style.num_format_str = "DD/MM/YYYY h:mm:ss AM/PM"
        sh.write(0, 1, "Fecha Prestamo/novedad")
        if tipoPersona == "DOCENTE":
            sh.write(0, 2, "Nombre Docente")
        elif tipoPersona == "CONTRATISTA":
            sh.write(0, 2, "Nombre Contratista")
        sh.write(0, 3, "Tipo")
        sh.write(0, 4, "Cédula")
        if tipoPersona == "DOCENTE":
            sh.write(0, 5, "Dependencia Docente")
        elif tipoPersona == "CONTRATISTA":
            sh.write(0, 5, "Dependencia Contratista")
        sh.write(0, 6, "Prestamo/Novedad")
        sh.write(0, 7, "Estado prestamo/novedad")
        idx = 0
        for row in result:
            sh.write(idx + 1, 0, str(row["id"]))
            sh.write(idx + 1, 1, row["fechaPrestamo"], style)
            sh.write(idx + 1, 2, row["nombre"])
            sh.write(idx + 1, 3, row["tipoPersona"])
            sh.write(idx + 1, 4, row["cedula"])
            sh.write(idx + 1, 5, row["depSolicitante"])
            sh.write(idx + 1, 6, row["prestamo"])
            sh.write(idx + 1, 7, row["estado"])
            idx += 1

        workbook.save(output)
        output.seek(0)
        cursor.close()
        if tipoPersona == "DOCENTE":
            return Response(
                output,
                mimetype="application/ms-excel",
                headers={
                    "Content-Disposition": "attachment;filename=reporte_prestamos_docentes.xls"
                },
            )
        elif tipoPersona == "CONTRATISTA":
            return Response(
                output,
                mimetype="application/ms-excel",
                headers={
                    "Content-Disposition": "attachment;filename=reporte_prestamo_novedades_contratistas.xls"
                },
            )


@app.route("/files/<path:path>")
def get_file(path):
    if (
        request.method == "GET"
        and comprobar_permisos("admin")
        or comprobar_permisos("user")
        or comprobar_permisos("checker")
    ):
        return send_from_directory(UPLOAD_FOLDER, path, as_attachment=False)
    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)
