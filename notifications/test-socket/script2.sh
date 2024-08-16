#!/bin/bash

INTERFACE="enp0s3"
TRAFFIC_LIMIT=10485760  # 10MB en bytes
LOG_FILE="/var/log/monitor_trafico.log"
SERVER_IP=$(hostname -I | awk '{print $1}')
PREV_RX_BYTES=0
PREV_TX_BYTES=0

while true; do
    # Obtiene las direcciones IP activas mediante SSH
    IP_LIST=$(ss -ntu state established '( dport = :3553 or sport = :3553 )' | awk '{print $5}' | cut -d':' -f1 | grep -v "$SERVER_IP" | grep -v 'Address' | sort | uniq)
    
    RX_BYTES=$(cat /sys/class/net/$INTERFACE/statistics/rx_bytes)
    TX_BYTES=$(cat /sys/class/net/$INTERFACE/statistics/tx_bytes)
    
    DELTA_RX=$((RX_BYTES - PREV_RX_BYTES))
    DELTA_TX=$((TX_BYTES - PREV_TX_BYTES))
    
    TOTAL_BYTES=$((DELTA_RX + DELTA_TX))
    
    # Actualiza los valores previos
    PREV_RX_BYTES=$RX_BYTES
    PREV_TX_BYTES=$TX_BYTES

    # Calcula el tráfico total en MB
    TOTAL_MB=$((TOTAL_BYTES / 1024 / 1024))

    for IP in $IP_LIST; do
        echo "Tráfico reciente para IP $IP: $TOTAL_MB MB" | tee -a $LOG_FILE

        if [ "$TOTAL_BYTES" -ge "$TRAFFIC_LIMIT" ]; then
            # Verifica si ya existe una regla de bloqueo para esta IP en INPUT y OUTPUT
            if ! sudo iptables -C INPUT -s "$IP" -j DROP 2>/dev/null; then
                echo "Límite de $((TRAFFIC_LIMIT / 1024 / 1024))MB alcanzado para IP $IP, bloqueando tráfico en $INTERFACE" | tee -a $LOG_FILE
                sudo iptables -A INPUT -s "$IP" -j DROP
                sudo iptables -A OUTPUT -d "$IP" -j DROP
            else
                echo "La IP $IP ya está bloqueada." | tee -a $LOG_FILE
            fi
        fi
    done

    sleep 10  # Espera 10 segundos antes de volver a verificar
done
