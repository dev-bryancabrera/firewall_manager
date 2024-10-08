from flask import redirect, render_template, jsonify, request, send_file, url_for

from flask_login import logout_user, login_required

# Models
from models.modelUser import modelUser

from models.funciones import (
    create_automation,
    create_automation_content,
    create_notification_sender,
    create_service_automation,
    deactivate_activate_automation,
    delete_automation,
    delete_automation_content,
    delete_community,
    delete_notification_config,
    delete_notifications,
    delete_vpnclient,
    get_notifications,
    get_plataforms,
    get_plataforms_domain,
    get_user_databases,
    get_user_tables,
    load_automation,
    load_comunnity,
    load_service_automation,
    mark_read_notification,
    obtener_reglas_ufw,
    obtener_reglas_ufw_contenido,
    delete_rule,
    scan_network,
    allow_connections,
    allow_connections_detail,
    setup_vpnclient,
    setup_vpnserver,
    status_openvpn,
    update_notification_sender,
    validar_ingreso,
    create_community,
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
    vpnclient_list,
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

    @app.route("/load_notifications", methods=["GET"])
    def load_notifications():
        # Recuperar las notificaciones de la base de datos
        notifications = get_notifications()

        return notifications

    @app.route("/mark_as_read", methods=["GET"])
    def mark_as_read():
        try:
            notification_id = request.args.get("id_notificacion")

            response = mark_read_notification(notification_id)

            return response

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/delete_notification", methods=["DELETE"])
    def delete_notification():
        try:
            data = request.get_json()
            notification_id = data.get("id_notificacion")

            delete_notifications(notification_id)
            return "", 204
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/home")
    @login_required
    def home_page():
        return render_template("home-page.html")

    @app.route("/get_devices", methods=["GET"])
    @login_required
    def get_devices():
        devices = scan_network()
        return devices

    @app.route("/get_tables", methods=["GET"])
    @login_required
    def get_databases():
        db_name = request.args.get("database")

        tables = get_user_tables(db_name)
        return tables

    @app.route("/server-vpn")
    @login_required
    def server_vpn():
        lista_clientes = vpnclient_list()

        return render_template("server-vpn.html", lista_clientes=lista_clientes)

    @app.route("/status_openvpn", methods=["GET"])
    @login_required
    def api_status_openvpn():
        status = status_openvpn()
        return jsonify(status)

    @app.route("/community_management")
    @login_required
    def community_management():
        comunidades = load_comunnity()
        devices = scan_network()
        return render_template(
            "community-management.html", devices=devices, comunidades=comunidades
        )

    @app.route("/firewall_automation/<id>")
    @login_required
    def firewall_automation_id(id):
        automatizaciones = load_automation()
        plataformas = get_plataforms()

        return render_template(
            "firewall-automation.html",
            plataformas=plataformas,
            automatizaciones=automatizaciones,
        )

    @app.route("/firewall_automation")
    @login_required
    def firewall_automation():
        automatizaciones = load_automation()
        comunidades = load_comunnity()
        plataformas = get_plataforms()

        return render_template(
            "firewall-automation.html",
            plataformas=plataformas,
            automatizaciones=automatizaciones,
            comunidades=comunidades,
        )

    @app.route("/service_automation")
    @login_required
    def service_automation():
        automatizaciones = load_service_automation()
        comunidades = load_comunnity()
        databases = get_user_databases()

        return render_template(
            "service-automation.html",
            automatizaciones=automatizaciones,
            comunidades=comunidades,
            databases=databases,
        )

    @app.route("/user-manual-firewall")
    @login_required
    def user_manual():
        return render_template("user-manual-firewall.html")

    @app.route("/user-manual-monitoreo")
    @login_required
    def user_manual_monitoreo():
        return render_template("user-manual-monitoreo.html")

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

        reglas_in, reglas_out, reglas_forward, reglas_default = obtener_reglas_ufw()

        reglas_in = reglas_in or []
        reglas_out = reglas_out or []
        reglas_forward = reglas_forward or []
        reglas_default = reglas_default or []

        return render_template(
            "config-firewall.html",
            reglas_in=reglas_in,
            reglas_out=reglas_out,
            reglas_forward=reglas_forward,
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
            count_packets = request.args.get("count_packets")

            return start_capture(command_id, command_filter, count_packets)
        except Exception as e:
            # Manejar cualquier error que pueda ocurrir durante la captura
            return f"Error al capturar los paquetes: {e}"

    @app.route("/pre_start_capture", methods=["GET"])
    def pre_packet_capture():
        return pre_start_capture()

    @app.route("/domain_plataform", methods=["GET"])
    def domain_plataform():
        key = request.args.get("key_plataform")

        return get_plataforms_domain(key)

    @app.route("/add_notification_email", methods=["POST"])
    @login_required
    def allow_notifications_mail():
        try:
            email_server = request.form.get("emailServer")
            email_sender = request.form.get("emailSender")
            email_password = request.form.get("emailPassword")
            email_receiver = request.form.get("emailReceiver")

            response = create_notification_sender(
                email_server,
                email_sender,
                email_password,
                email_receiver,
            )

            return response
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/update_notification_email", methods=["POST"])
    @login_required
    def update_notifications_mail():
        try:
            email_sender = request.form.get("emailSender")
            email_password = request.form.get("emailPassword")
            email_receiver = request.form.get("emailReceiver")

            print(email_sender)

            response = update_notification_sender(
                email_sender,
                email_password,
                email_receiver,
            )

            return response
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/delete_notifications_mail", methods=["DELETE"])
    def delete_notifications_mail():
        try:
            print("llego")
            response = delete_notification_config()
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Definir apertura de conexiones
    @app.route("/add_rule", methods=["POST"])
    @login_required
    def allow_rule():
        try:
            action_rule = request.form.get("action_rule")
            type_rule = request.form.get("regla")
            ip_addr = request.form.get("ip_addr")
            local_red = request.form.get("localRed")
            local_ip_mac_red = request.form.get("localIpMacRed")
            local_ip_red = request.form.get("localIpRed")
            local_mac_red = request.form.get("localMacRed")
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
                action_rule,
                type_rule,
                ip_addr,
                local_red,
                local_ip_mac_red,
                local_ip_red,
                local_mac_red,
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
            return response
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
            domain = request.form.get("domain")

            response = allow_connections_detail(
                id_regla,
                regla_name,
                accion_regla,
                domain,
            )
            return response
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/add_automation_content", methods=["POST"])
    @login_required
    def allow_add_automation_content():
        try:
            automation_name = request.form.get("automationName")
            domain_plataform = request.form.getlist("domainPlataform")
            horario = request.form.get("horario")
            id_regla = request.form.get("id_regla")
            nombre_regla = request.form.get("nombre_regla")

            response = create_automation_content(
                automation_name,
                domain_plataform,
                horario,
                id_regla,
                nombre_regla,
            )
            return response
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
            return jsonify({"error": str(e)}), 500

    @app.route("/add_community", methods=["POST"])
    @login_required
    def allow_add_community():
        try:
            community_name = request.form.get("communityName")
            community_type = request.form.get("communityType")
            local_ip = request.form.getlist("localIp")
            initial_ip = request.form.get("initialIp")
            final_ip = request.form.get("finalIp")

            response = create_community(
                community_name,
                community_type,
                local_ip,
                initial_ip,
                final_ip,
            )
            return response
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/add_service_automation", methods=["POST"])
    @login_required
    def allow_add_service_automation():
        try:
            automation_name = request.form.get("automationName")
            community_id = request.form.get("community")
            service_type = request.form.get("serviceType")
            action_type = request.form.get("actionType")
            # Campos Mysql
            restriction_mysql = request.form.get("restrictionMysql")
            max_connection_type = request.form.get("maxConnectionType")
            max_connections = request.form.get("maxConnections")
            user_name = request.form.get("userName")
            access_type = request.form.get("accessType")
            mysql_max_duration = request.form.get("mysqlMaxDuration")
            # Campos ssh
            actionssh_type = request.form.get("actionsshType")
            network_usage = request.form.get("networkUsage")
            session_duration = request.form.get("sessionDuration")
            ssh_max_duration = request.form.get("sshMaxDuration")
            # Campos ftp
            actionftp_type = request.form.get("actionftpType")
            upload_directory = request.form.get("uploadDirectory")
            file_types = request.form.get("fileTypes")
            download_directory = request.form.get("downloadDirectory")
            max_transfer_size = request.form.get("maxTransferSize")

            response = create_service_automation(
                automation_name,
                community_id,
                service_type,
                action_type,
                restriction_mysql,
                max_connection_type,
                max_connections,
                user_name,
                access_type,
                mysql_max_duration,
                actionssh_type,
                network_usage,
                session_duration,
                ssh_max_duration,
                actionftp_type,
                upload_directory,
                file_types,
                download_directory,
                max_transfer_size,
            )
            return response
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/add_automation", methods=["POST"])
    @login_required
    def allow_add_automation():
        try:
            automation_name = request.form.get("automationName")
            automation_type = request.form.get("automationType")
            automation_action = request.form.get("automationAction")
            domain = request.form.get("domain")
            content_type = request.form.get("contentType")
            domain_plataform = request.form.getlist("domainPlataform")
            community_id = request.form.get("idComunnity")
            horario = request.form.get("horario")

            response = create_automation(
                automation_name,
                automation_type,
                automation_action,
                domain,
                content_type,
                domain_plataform,
                community_id,
                horario,
            )
            return response
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/add_vpn_server", methods=["POST"])
    @login_required
    def add_vpn_server():
        try:
            vpn_name = request.form.get("vpnName")
            vpn_asociation = request.form.get("vpnAsociation")
            vpn_secret_key = request.form.get("vpnSecretKey")

            response = setup_vpnserver(vpn_name, vpn_asociation, vpn_secret_key)
            return response
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/add_vpn_client", methods=["POST"])
    @login_required
    def add_vpn_client():
        try:
            client_name = request.form.get("clientName")
            client_key = request.form.get("clientKey")
            vpn_secret_key = request.form.get("secretVpn")
            print(client_name)
            response = setup_vpnclient(client_name, client_key, vpn_secret_key)
            return response
        except KeyError as e:
            return f"No se proporcionó el campo {e} en la solicitud POST."

    @app.route("/download_ovpn", methods=["GET"])
    def download_ovpn():
        ovpn_file = request.args.get("filename")
        return send_file(ovpn_file, as_attachment=True)

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

            response = deactivate_activate_rule(regla_id, regla_content_id)

            return response

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
            return jsonify({"error": f"Error al eliminar el reporte: {e}"})

    @app.route("/eliminar_filtro", methods=["GET"])
    @login_required
    def eliminar_filtro():
        try:
            id_reporte = request.args.get("id_filtro")

            response = delete_filter(id_reporte)

            # return redirect(url_for("packet_filtering", response=response))
            return response

        except Exception as e:
            return f"Error al eliminar el filtro: {e}"

    @app.route("/eliminar_comunidad", methods=["GET"])
    @login_required
    def eliminar_comunidad():
        try:
            id_comunidad = request.args.get("id")

            response = delete_community(id_comunidad)

            return response

        except Exception as e:
            return jsonify({"error": f"Error al eliminar la comunidad: {e}"})

    @app.route("/desactivar_automatizacion", methods=["GET"])
    @login_required
    def desactivar_automatizacion():
        try:
            id_automation = request.args.get("id")

            response = deactivate_activate_automation(id_automation)

            return response

        except Exception as e:
            error_message = (
                f"Error al desactivar la regla: {type(e).__name__}: {str(e)}"
            )
            return error_message

    @app.route("/eliminar_automatizacion", methods=["GET"])
    @login_required
    def eliminar_automatizacion():
        try:
            id_automatizacion = request.args.get("id")

            response = delete_automation(id_automatizacion)

            return response

        except Exception as e:
            return jsonify({"error": f"Error al eliminar la automatizacion: {e}"})

    @app.route("/eliminar_clientevpn", methods=["GET"])
    @login_required
    def eliminar_clientevpn():
        try:
            cliente_eliminar = request.args.get("client_name")
            vpn_secret_key = request.args.get("secret_vpn")

            response = delete_vpnclient(cliente_eliminar, vpn_secret_key)

            return response

        except Exception as e:
            return jsonify({"error": f"Error al eliminar el cliente vpn: {e}"})

    # Eliminar una regla establecida
    @app.route("/eliminar_regla", methods=["GET"])
    @login_required
    def eliminar_regla():
        try:
            regla = request.args.get("regla")
            id_regla = request.args.get("id_regla")

            response = delete_rule(regla, id_regla)

            return response

        except Exception as e:
            return jsonify({"error": f"Error al eliminar la regla: {e}"})

    @app.route("/eliminar_automatizacion_content", methods=["GET"])
    @login_required
    def eliminar_automatizacion_content():
        try:
            regla_id = request.args.get("regla_id")
            regla_nombre = request.args.get("regla_nombre")
            automatizacion_nombre = request.args.get("automatizacion_nombre")

            print(automatizacion_nombre)

            response = delete_automation_content(
                regla_id, regla_nombre, automatizacion_nombre
            )

            return response

        except Exception as e:
            return jsonify({"error": f"Error al eliminar la automatizacion: {e}"})
