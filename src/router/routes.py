from flask import Response, redirect, render_template, jsonify, request, url_for

# from scapy.all import sniff, IP, TCP
from flask_login import logout_user, login_required

# Models
from models.modelUser import modelUser

from models.funciones import (
    obtener_reglas_ufw,
    obtener_reglas_ufw_contenido,
    delete_rule,
    scan_network,
    allow_connections,
    allow_connections_detail,
    validar_ingreso,
    start_capture,
    pre_start_capture,
    deactivate_activate_rule,
    save_report,
    save_filter,
    load_filter_data,
    load_report,
    load_reportData,
    delete_report,
    delete_filter,
)


def configurar_rutas(app, login_manager_app):
    @app.route("/")
    def login_user():
        return redirect(url_for("login"))

    @login_manager_app.user_loader
    def load_user(id):
        return modelUser.getById(id)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        try:
            if request.method == "POST":
                username = request.form.get("username")
                password_hash = request.form.get("password_hash")

                if validar_ingreso(username, password_hash):
                    return redirect(url_for("home_page"))
                else:
                    return render_template(
                        "login.html", error="Nombre de usuario o contraseña incorrectos"
                    )
            else:
                return render_template("login.html")

        except KeyError as e:
            return f"Error al iniciar sesion.{e}"

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/home")
    @login_required
    def home_page():
        return render_template("home-page.html")

    @app.route("/user-manual")
    @login_required
    def user_manual():
        return render_template("user-manual.html")

    @app.route("/traffic-packets/<id>/<filtro>")
    @login_required
    def packet_monitoring(id, filtro):
        registros = load_report()

        return render_template("traffic-packets.html", registros=registros)

    @app.route("/traffic-packets")
    @login_required
    def packet_monitoring_report_saved():
        registros = load_report()

        return render_template("traffic-packets.html", registros=registros)

    @app.route("/traffic-filter")
    @login_required
    def packet_filtering():
        devices = scan_network()
        registrosFilter = load_filter_data()

        return render_template(
            "packet-filter.html", devices=devices, registrosFilter=registrosFilter
        )

    @app.route("/ufw_manager")
    @login_required
    def obtener_reglas_ufw_route():
        devices = scan_network()

        resultado = obtener_reglas_ufw()

        reglas_in, reglas_out, reglas_default = resultado

        if reglas_in and reglas_out:
            return render_template(
                "config-firewall.html",
                reglas_in=reglas_in,
                reglas_out=reglas_out,
                reglas_default=reglas_default,
                devices=devices,
            )

        elif reglas_in:
            return render_template(
                "config-firewall.html",
                reglas_in=reglas_in,
                reglas_default=reglas_default,
                devices=devices,
            )

        elif reglas_out:
            return render_template(
                "config-firewall.html",
                reglas_out=reglas_out,
                reglas_default=reglas_default,
                devices=devices,
            )

        elif reglas_default:
            return render_template(
                "config-firewall.html",
                reglas_default=reglas_default,
                devices=devices,
            )

    @app.route("/rules-content-manager")
    @login_required
    def obtener_reglas_ufw_content():
        resultado = obtener_reglas_ufw_contenido()

        reglas_contenido = resultado

        return render_template(
            "rules-content.html",
            reglas_contenido=reglas_contenido,
        )

    @app.route("/packetdata", methods=["GET"])
    def packet_data():
        try:
            command_id = request.args.get("command_id")
            command_filter = request.args.get("command_filter")

            return Response(
                start_capture(
                    command_id,
                    command_filter,
                ),
                content_type="text/event-stream",
            )

        except Exception as e:
            # Manejar cualquier error que pueda ocurrir durante la captura
            return f"Error al capturar los paquetes: {e}"

    @app.route("/pre_start_capture", methods=["GET"])
    def pre_packet_capture():
        return Response(pre_start_capture(), content_type="text/event-stream")

    # Definir apertura de conexiones
    @app.route("/add_rule", methods=["POST"])
    @login_required
    def allow_rule():
        try:
            accion_regla = request.form.get("action_rule")
            tipo_regla = request.form.get("regla")
            ip_addr = request.form.get("ip_addr")
            domain = request.form.get("domain")
            direction = request.form.get("fromto")
            netmask = request.form.get("netmask")
            ip_dest = request.form.get("ip_dest")
            dest_netmask = request.form.get("dest_netmask")
            port = request.form.get("port")
            portStart = request.form.get("portStart")
            portLimit = request.form.get("portLimit")
            protocol = request.form.get("protocol")
            entry = request.form.get("entry")
            comment = request.form.get("comment")
            content_tp = request.form.getlist("contentOption")

            response = allow_connections(
                accion_regla,
                tipo_regla,
                ip_addr,
                domain,
                port,
                protocol,
                entry,
                direction,
                netmask,
                ip_dest,
                dest_netmask,
                portStart,
                portLimit,
                comment,
                content_tp,
            )
            return jsonify({"message": response})
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/add_rule_detail", methods=["POST"])
    @login_required
    def add_rule_detail():
        try:
            id_regla = request.form.get("rule_id")
            regla_name = request.form.get("name_detail_rule")
            # comment = request.form.get("comment")
            accion_regla = request.form.get("action_rule")
            entry = request.form.get("entry")
            domain = request.form.get("domain")

            response = allow_connections_detail(
                id_regla,
                regla_name,
                accion_regla,
                entry,
                domain,
            )
            return jsonify({"message": response})
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/save_filter", methods=["POST"])
    @login_required
    def save_filter_packet():
        try:
            name_filter = request.form.get("filterName")
            type_ip = request.form.get("typeFilterIp")
            type_domain = request.form.get("typeFilterDomain")
            type_content = request.form.get("typeFilterContent")
            type_mac = request.form.get("typeFilterMac")
            type_port = request.form.get("typeFilterPort")
            type_proto_red = request.form.get("typeFilterProtoRed")
            ip_addr = request.form.get("ip_addr")
            ip_dest = request.form.get("ip_dest")
            content_dst = request.form.getlist("content_dst")
            domain_dst = request.form.get("domain_dest")
            mac_addr = request.form.get("mac_addr")
            mac_dest = request.form.get("mac_dest")
            portSrc = request.form.get("portStart")
            portDst = request.form.get("portLimit")
            port_red_src = request.form.getlist("portRedSrc")
            port_red_dst = request.form.getlist("portRedDst")
            packet_protocol = request.form.get("packet_protocol")
            # Datos Generales
            general_ip = request.form.get("generalIp")
            general_domain = request.form.get("generalDomain")
            general_content = request.form.getlist("generalContent")
            general_port = request.form.get("generalPort")
            general_port_red = request.form.getlist("generalPortRed")
            # Obtener los datos de comparadores
            logic_operator_ip = request.form.get("logicOperatorIp")
            logic_operator_mac = request.form.get("logicOperatorMac")
            logic_operator_mac_port = request.form.get("logicOperatorMacPort")
            logic_operator_proto_red_proto = request.form.get(
                "logicOperatorProtoRedProto"
            )

            response = save_filter(
                name_filter,
                type_ip,
                type_domain,
                type_content,
                type_mac,
                type_port,
                type_proto_red,
                ip_addr,
                ip_dest,
                content_dst,
                domain_dst,
                port_red_src,
                port_red_dst,
                portSrc,
                portDst,
                packet_protocol,
                mac_addr,
                mac_dest,
                general_ip,
                general_domain,
                general_content,
                general_port,
                general_port_red,
                logic_operator_ip,
                logic_operator_mac,
                logic_operator_mac_port,
                logic_operator_proto_red_proto,
            )

            return jsonify({"message": response})

        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @app.route("/save_report", methods=["POST"])
    @login_required
    def save_report_excel():
        try:
            data = request.get_json()

            nombre_reporte = data.get("nombre")
            filtro_monitoreo = data.get("filtro")
            table_data = data.get("tableData")

            response = save_report(nombre_reporte, filtro_monitoreo, table_data)

            return jsonify({"message": response})

        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @app.route("/load_report_data", methods=["GET"])
    @login_required
    def load_report_data():
        try:
            id_report = request.args.get("registro_id")
            reporte = load_reportData(id_report)

            return jsonify(reporte)
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @app.route("/desactivar_regla", methods=["GET"])
    @login_required
    def desactivar_regla():
        try:
            regla_id = request.args.get("id_regla")
            regla_content_id = request.args.get("id")

            deactivate_activate_rule(regla_id, regla_content_id)

            if regla_content_id:
                return redirect(url_for("obtener_reglas_ufw_content"))
            else:
                return redirect(url_for("obtener_reglas_ufw_route"))

        except Exception as e:
            error_message = (
                f"Error al desactivar la regla: {type(e).__name__}: {str(e)}"
            )
            return error_message

    @app.route("/eliminar_reporte", methods=["GET"])
    @login_required
    def eliminar_reporte():
        try:
            id_reporte = request.args.get("reporte_id")

            response = delete_report(id_reporte)

            return jsonify({"message": response})

        except Exception as e:
            return f"Error al eliminar la regla: {e}"

    @app.route("/eliminar_filtro", methods=["GET"])
    @login_required
    def eliminar_filtro():
        try:
            id_reporte = request.args.get("id_filtro")

            response = delete_filter(id_reporte)

            return redirect(url_for("packet_filtering", response=response))

        except Exception as e:
            return f"Error al eliminar la regla: {e}"

    # Eliminar una regla establecida
    @app.route("/eliminar_regla", methods=["GET"])
    @login_required
    def eliminar_regla():
        try:
            regla = request.args.get("regla")
            id_regla = request.args.get("id_regla")

            # Obtén el número de la regla utilizando el nuevo método
            response = delete_rule(regla, id_regla)

            return jsonify({"message": response})

        except Exception as e:
            # Manejar cualquier error que pueda ocurrir durante la eliminación
            return f"Error al eliminar la regla: {e}"
