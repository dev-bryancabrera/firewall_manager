#!/bin/bash

# Funcion para verificar si los paquete estan instalados
check_install_package() {
    if ! dpkg -l | grep -q "$1"; then
        echo "Instalando $1..."
        sudo apt-get install -y "$1"
    fi
}

# Obtener la direccion IP publica
get_public_ip() {
    PUBLIC_IP=$(curl -s https://api.ipify.org)
    if [ -z "$PUBLIC_IP" ]; then
        echo "Error: No se pudo obtener la direccion IP pública."
        exit 1
    fi
}

# Obtener la interfaz de red
detect_network_interface() {
    INTERFACE=$(ip route | grep '^default' | awk '{print $5}')
    if [ -z "$INTERFACE" ]; then
        echo "Error: No se pudo detectar la interfaz de red."
        exit 1
    fi
}

# Crear las reglas de iptables
setup_firewall_rules() {
    sudo iptables -t nat -I POSTROUTING 1 -s 10.8.0.0/24 -o "$INTERFACE" -j MASQUERADE
    sudo iptables -I INPUT 1 -i tun0 -j ACCEPT
    sudo iptables -I FORWARD 1 -i "$INTERFACE" -o tun0 -j ACCEPT
    sudo iptables -I FORWARD 1 -i tun0 -o "$INTERFACE" -j ACCEPT
    sudo iptables -I INPUT 1 -i "$INTERFACE" -p udp --dport 1194 -j ACCEPT
}

# Configurar el servidor OpenVPN
function setup_server() {
    sudo cp -r /usr/share/easy-rsa /etc/openvpn/
    cd /etc/openvpn/easy-rsa/ || exit

    sudo ./easyrsa init-pki

    # Crear archivo .rnd si no existe
    if [ ! -f /etc/openvpn/easy-rsa/pki/.rnd ]; then
        sudo touch /etc/openvpn/easy-rsa/pki/.rnd
        sudo chmod 600 /etc/openvpn/easy-rsa/pki/.rnd
    fi

    # Crear el CA usando expect
    sudo expect <<EOF
spawn sudo ./easyrsa build-ca
expect "Enter New CA Key Passphrase:"
send "admin-openvpn\r"
expect "Re-Enter New CA Key Passphrase:"
send "admin-openvpn\r"
expect "Common Name (eg: your user, host, or server name) \\[Easy-RSA CA\\]:"
send "IntelHome CA\r"
expect eof
EOF

    sudo expect <<EOF
spawn sudo ./easyrsa --batch build-server-full servervpn-sigcenter nopass
expect "Confirm request details:"
send "yes\r"
expect "Enter pass phrase for /etc/openvpn/easy-rsa/pki/private/ca.key:"
send "admin-openvpn\r"
expect eof
EOF

    sudo expect <<EOF
spawn sudo ./easyrsa sign-req server servervpn-sigcenter
expect "Confirm request details:"
send "yes\r"
expect "Enter pass phrase for /etc/openvpn/easy-rsa/pki/private/ca.key:"
send "admin-openvpn\r"
expect eof
EOF

    sudo cp /etc/openvpn/easy-rsa/pki/issued/servervpn-sigcenter.crt /etc/openvpn/server/
    sudo cp /etc/openvpn/easy-rsa/pki/ca.crt /etc/openvpn/server/
    sudo cp /etc/openvpn/easy-rsa/pki/private/servervpn-sigcenter.key /etc/openvpn/server/

    cd /etc/openvpn/server/ || exit

    sudo openvpn --genkey --secret ta.key

    sudo mkdir -p /etc/openvpn/client/keys
    sudo chmod -R 700 /etc/openvpn/client/

    # Eliminar contenido existente y luego escribir el nuevo contenido
    cat >/etc/openvpn/server/server.conf <<EOF
port 1194
proto udp
dev tun
ca ca.crt
cert servervpn-sigcenter.crt
key servervpn-sigcenter.key
dh none
topology subnet
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist /var/log/openvpn/ipp.txt
push "redirect-gateway def1 bypass-dhcp"
push "route $PUBLIC_IP 255.255.255.255 vpn_gateway"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"
keepalive 10 120
tls-crypt ta.key
cipher AES-256-GCM
auth SHA512
max-clients 100
user nobody
group nogroup
persist-key
persist-tun
status /var/log/openvpn/openvpn-status.log
verb 3
explicit-exit-notify 1
EOF
}

# Funcion para crear un nuevo cliente
function create_client() {

    echo ""
    echo "Asigna un nombre para el cliente."
    echo "El nombre debe constar de caracteres alfanuméricos. Sin caracteres especiales"

    until [[ $CLIENT =~ ^[a-zA-Z0-9_-]+$ ]]; do
        read -rp "Nombre del Cliente: " -e CLIENT
    done

    if echo $CLIENT | grep -q '-'; then
        echo "No ingrese caracteres especiales!"
        exit
    fi

    echo ""
    echo "Quieres asignar una contraseña al cliente?"
    echo "(por ejemplo, encriptar la clave privada con una contraseña)"
    echo "   1) Añadir un cliente sin contraseña"
    echo "   2) Usar una contraseña para el cliente"
    echo ""

    # Solicitar y validar la opcion de proteccion con contraseña
    until [[ $PASS =~ ^[1-2]$ ]]; do
        read -rp "Select an option [1-2]: " -e -i 1 PASS
    done

    # Verificar si el cliente ya existe en easy-rsa
    CLIENTEXISTS=$(tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep -c -E "/CN=$CLIENT\$")
    if [[ $CLIENTEXISTS == '1' ]]; then
        echo ""
        echo "Ya existe un cliente registrado con ese nombre, seleccione otro"
        exit
    else
        cd /etc/openvpn/easy-rsa/ || return
        case $PASS in

        1)
            # Generar cliente sin contraseña usando expect
            sudo expect <<EOF
spawn sudo ./easyrsa --batch build-client-full "$CLIENT-sigcenter" nopass
expect "Enter pass phrase for /etc/openvpn/easy-rsa/pki/private/ca.key:"
send "admin-openvpn\r"
expect eof
EOF
            ;;
        2)
            # Generar cliente con contraseña usando expect
            echo "⚠️ Ingrese la contraseña para el cliente, recuérdela para establecer la conexion ⚠️"

            read -sp "Ingrese la contraseña para el cliente: " CLIENT_PASS
            echo

            # Usar expect para manejar ambos prompts
            sudo expect <<EOF
spawn sudo ./easyrsa --batch build-client-full "$CLIENT-sigcenter"
expect "Enter PEM pass phrase:"
send "$CLIENT_PASS\r"
expect "Verifying - Enter PEM pass phrase:"
send "$CLIENT_PASS\r"
expect "Enter pass phrase for /etc/openvpn/easy-rsa/pki/private/ca.key:"
send "admin-openvpn\r"
expect eof
EOF

            ;;
        esac

        if [[ $? -ne 0 ]]; then
            echo "Error al generar la solicitud de certificado para el cliente."
            exit 1
        fi

        # Firmar el certificado del cliente usando expect para manejar el prompt de passphrase
        #         sudo expect <<EOF
        # spawn sudo ./easyrsa sign-req client "$CLIENT-sigcenter"
        # expect "Confirm request details:"
        # send "yes\r"
        # expect "Enter pass phrase for /etc/openvpn/easy-rsa/pki/private/ca.key:"
        # send "admin-openvpn\r"
        # expect eof
        # EOF

        # Copiar el certificado y la clave privada al directorio de claves del cliente
        sudo cp /etc/openvpn/easy-rsa/pki/issued/"$CLIENT-sigcenter".crt /etc/openvpn/client/keys/
        sudo cp /etc/openvpn/easy-rsa/pki/private/"$CLIENT-sigcenter".key /etc/openvpn/client/keys/

        echo "Client $CLIENT added."
    fi

    # Crear archivo de configuracion para el cliente
    KEY_DIR=/etc/openvpn/client/keys
    OUTPUT_DIR=/etc/openvpn/client/files
    BASE_CONFIG=/etc/openvpn/client/plantilla.conf

    sudo mkdir -p $OUTPUT_DIR

    sudo bash -c "cat ${BASE_CONFIG} \
        <(echo -e '<ca>') \
        ${KEY_DIR}/ca.crt \
        <(echo -e '</ca>\n<cert>') \
        ${KEY_DIR}/$CLIENT-sigcenter.crt \
        <(echo -e '</cert>\n<key>') \
        ${KEY_DIR}/$CLIENT-sigcenter.key \
        <(echo -e '</key>\n<tls-crypt>') \
        ${KEY_DIR}/ta.key \
        <(echo -e '</tls-crypt>') \
        > ${OUTPUT_DIR}/$CLIENT-sigcenter.ovpn"
}

# Funcion para eliminar un cliente
function delete_client() {

    NUMBEROFCLIENTS=$(tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep -c "^V")
    if [[ $NUMBEROFCLIENTS == '0' ]]; then
        echo ""
        echo "No tienes clientes registrados!"
        exit 1
    fi

    echo ""
    echo "Seleccione el cliente que se quiere eliminar"
    tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep "^V" | cut -d '=' -f 2 | nl -s ') '
    until [[ $CLIENTNUMBER -ge 1 && $CLIENTNUMBER -le $NUMBEROFCLIENTS ]]; do
        if [[ $CLIENTNUMBER == '1' ]]; then
            read -rp "Selecciona un cliente [1]: " CLIENTNUMBER
        else
            read -rp "Selecciona un cliente [1-$NUMBEROFCLIENTS]: " CLIENTNUMBER
        fi
    done

    CLIENT=$(tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep "^V" | cut -d '=' -f 2 | sed -n "$CLIENTNUMBER"p)
    cd /etc/openvpn/easy-rsa/ || return

    # Revocar un cliente usando expect
    sudo expect <<EOF
spawn sudo ./easyrsa --batch revoke "$CLIENT"
expect "Enter pass phrase for /etc/openvpn/easy-rsa/pki/private/ca.key:"
send "admin-openvpn\r"
expect eof
EOF

    # Generar el CRL
    sudo expect <<EOF
spawn sudo EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl
expect "Enter pass phrase for /etc/openvpn/easy-rsa/pki/private/ca.key:"
send "admin-openvpn\r"
expect eof
EOF

    sudo rm -f /etc/openvpn/crl.pem
    sudo cp /etc/openvpn/easy-rsa/pki/crl.pem /etc/openvpn/crl.pem
    sudo chmod 644 /etc/openvpn/crl.pem
    sudo find /home/tecnico/openvpn/ -maxdepth 2 -name "$CLIENT.ovpn" -delete
    sudo rm -f "/etc/openvpn/client/files/$CLIENT.ovpn"
    sudo sed -i "/^$CLIENT,.*/d" /var/log/openvpn/ipp.txt
    sudo cp /etc/openvpn/easy-rsa/pki/index.txt{,.bk}
    sudo rm -f "/etc/openvpn/client/keys/$CLIENT.crt" "/etc/openvpn/client/keys/$CLIENT.key"

    echo ""
    echo "Certificados y cliente $CLIENT revocado."
}

# Funcion para desinstalar OpenVPN
function uninstall_openvpn() {

    echo ""
    read -rp "Estas seguro de eliminar OpenVPN? [y/n]: " -e -i n REMOVE
    if [[ $REMOVE == 'y' ]]; then
        # Obtener la configuracion de OpenVPN
        PORT=$(grep '^port ' /etc/openvpn/server/server.conf | cut -d " " -f 2)
        PROTOCOL=$(grep '^proto ' /etc/openvpn/server/server.conf | cut -d " " -f 2)

        sudo systemctl stop openvpn-server@server.service
        sudo apt-get remove --purge -y openvpn easy-rsa
        sudo rm -rf /etc/openvpn
        sudo rm -rf /var/log/openvpn/

        sudo apt autoremove -y

        INTERFACE=$(ip route | grep '^default' | awk '{print $5}')
        if [ -z "$INTERFACE" ]; then
            echo "Error: No se pudo detectar la interfaz de red."
        else
            # Eliminar reglas de iptables
            sudo iptables -t nat -D POSTROUTING -s 10.8.0.0/24 -o "$INTERFACE" -j MASQUERADE
            sudo iptables -D INPUT -i tun0 -j ACCEPT
            sudo iptables -D FORWARD -i "$INTERFACE" -o tun0 -j ACCEPT
            sudo iptables -D FORWARD -i tun0 -o "$INTERFACE" -j ACCEPT
            sudo iptables -D INPUT -i "$INTERFACE" -p udp --dport 1194 -j ACCEPT
        fi

        # SELinux
        if hash sestatus 2>/dev/null; then
            if sestatus | grep "Current mode" | grep -qs "enforcing"; then
                if [[ $PORT != '1194' ]]; then
                    semanage port -d -t openvpn_port_t -p "$PROTOCOL" "$PORT"
                fi
            fi
        fi

        echo ""
        echo "OpenVPN desinstalado!"
    else
        echo ""
        echo "Desinstalacion cancelada!"
    fi
}

# Configuracion inicial del servidor y cliente si no existe el servidor
if [ ! -d /etc/openvpn/server ]; then

    # Verificar e instalar paquetes necesarios
    check_install_package openvpn
    check_install_package easy-rsa

    echo "Configuracion del servidor OpenVPN:"

    get_public_ip
    setup_server
    detect_network_interface
    setup_firewall_rules

    sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
    sudo sysctl -p
    echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward

    # Certificado para los clientes
    sudo cp /etc/openvpn/easy-rsa/pki/ca.crt /etc/openvpn/client/keys/
    sudo cp /etc/openvpn/server/ta.key /etc/openvpn/client/keys/

    # Eliminar contenido existente y luego escribir el nuevo contenido en client.conf
    cat >/etc/openvpn/client/client.conf <<EOF
client
remote $PUBLIC_IP 1194
proto udp
dev tun
resolv-retry infinite
nobind
user nobody
group nogroup
persist-key
persist-tun
redirect-gateway def1
remote-cert-tls server
cipher AES-256-GCM
auth SHA512
verb 3
EOF

    # Crear plantilla.conf con el mismo contenido que client.conf
    sudo bash -c 'cat /etc/openvpn/client/client.conf > /etc/openvpn/client/plantilla.conf'

    create_client

    sudo systemctl restart openvpn-server@server.service
    sudo systemctl enable openvpn-server@server.service
    sudo systemctl restart openvpn
    sudo systemctl enable openvpn

    echo "Servidor OpenVPN y cliente inicial configurados correctamente."
else
    echo "Que accion desea realizar?"
    echo ""
    echo "1) Crear nuevo cliente"
    echo "2) Eliminar un cliente"
    echo "3) Desinstalar OpenVPN"
    echo ""
    echo -n "Seleccione una opcion: "
    read -r OPTION

    case $OPTION in
    1)
        create_client
        ;;
    2)
        delete_client
        ;;
    3)
        uninstall_openvpn
        ;;
    *)
        echo "Opcion no valida."
        ;;
    esac
fi
