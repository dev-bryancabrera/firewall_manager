#!/bin/bash

# Archivo de log que se monitoreará
LOGFILE="/var/log/syslog"

# Archivo para almacenar las IPs bloqueadas permanentemente
BLOCK_LOG_FILE="/var/log/blocked_ips.log"

# Crear archivo de log si no existe
touch "$BLOCK_LOG_FILE"

# Crear una lista de IPs permitidas por UFW para entrada y salida
EXEMPTED_IPS=($(ufw status numbered | grep -E 'ALLOW IN|ALLOW OUT' | awk '{print $3}' | grep -E '([0-9]{1,3}\.){3}[0-9]{1,3}'))

# Obtener la IP del servidor
SERVER_IP=$(hostname -I | awk '{print $1}')

# Función para obtener IPs activas en SSH
get_ssh_ips() {
    ss -ntu state established '( dport = :3553 or sport = :3553 )' |
        awk 'NR>1 {print $5}' | cut -d':' -f1 | grep -v "$SERVER_IP" | sort | uniq
}

# Comando para monitorear el log
tail -F "$LOGFILE" | while read LINE; do
    # Obtener IPs activas en SSH
    SSH_IPS=($(get_ssh_ips))

    if [[ "$LINE" == *"TRAFFIC_LIMIT_EXCEEDED"* ]]; then
        # Extraer la dirección IP fuente (SRC)
        IP=$(echo "$LINE" | grep -oP '(?<=SRC=)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')

        # Verificar si la IP está en la lista de IPs exentas
        if [[ " ${EXEMPTED_IPS[@]} " =~ " ${IP} " ]]; then
            echo "La IP $IP está exenta del bloqueo."
            continue
        fi

        # Verificar si la IP está conectada por SSH
        if [[ " ${SSH_IPS[@]} " =~ " ${IP} " ]]; then
            # Agregar la regla IPTables para bloquear la IP si aún no está bloqueada
            if ! sudo iptables -C INPUT -p tcp -s "$IP" --dport 3553 -j REJECT 2>/dev/null; then
                sudo iptables -A INPUT -p tcp -s "$IP" --dport 3553 -j REJECT
                CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')
                echo "$IP INPUT $(date +%s) $CURRENT_DATE" >>"$BLOCK_LOG_FILE"
                echo "Bloqueada la IP $IP en el puerto 3553 para entrada debido a límite de tráfico excedido."
            fi
        fi
    elif [[ "$LINE" == *"TRAFFIC_OUT_LIMIT_EXCEEDED"* ]]; then
        # Extraer la dirección IP destino (DST)
        DST_IP=$(echo "$LINE" | grep -oP '(?<=DST=)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')

        # Verificar si la IP está en la lista de IPs exentas
        if [[ " ${EXEMPTED_IPS[@]} " =~ " ${DST_IP} " ]]; then
            echo "La IP $DST_IP está exenta del bloqueo."
            continue
        fi

        # Verificar si la IP está conectada por SSH
        if [[ " ${SSH_IPS[@]} " =~ " ${DST_IP} " ]]; then
            # Agregar la regla IPTables para bloquear la IP de destino si aún no está bloqueada
            if ! sudo iptables -C OUTPUT -p tcp -d "$DST_IP" -j REJECT 2>/dev/null; then
                sudo iptables -A OUTPUT -p tcp -d "$DST_IP" -j REJECT
                CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')
                echo "$DST_IP OUTPUT $(date +%s) $CURRENT_DATE" >>"$BLOCK_LOG_FILE"
                echo "Bloqueada la IP de destino $DST_IP para salida debido a límite de tráfico excedido."
            fi
        fi
    elif [[ "$LINE" == *"TRAFFIC_OUT_50MB_LIMIT_EXCEEDED"* ]]; then
        # Extraer la dirección IP destino (DST)
        DST_IP=$(echo "$LINE" | grep -oP '(?<=DST=)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')

        # Verificar si la IP está en la lista de IPs exentas
        if [[ " ${EXEMPTED_IPS[@]} " =~ " ${DST_IP} " ]]; then
            echo "La IP $DST_IP está exenta del bloqueo."
            continue
        fi

        # Agregar un mensaje al log con la IP, la fecha y el mensaje de que se superó los 50 MB
        CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')
        logger -p local0.info "IP $DST_IP superó los 50 MB en $CURRENT_DATE"
        echo "IP $DST_IP superó los 50 MB en $CURRENT_DATE" >>"$BLOCK_LOG_FILE"
    fi

done
