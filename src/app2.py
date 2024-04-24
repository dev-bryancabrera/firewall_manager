from urllib.parse import quote

# Cadena que contiene el carácter '/'
cadena_original = "192.168.175.134:3000/traffic-packets/13/(net 2.20.196.0/24)"

# Reemplazar '/' por '-'
cadena_modificada = cadena_original.replace('/', '-')

print("Cadena modificada:", cadena_modificada)
