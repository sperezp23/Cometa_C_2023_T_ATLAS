from urllib import request

# Definimos la URL del archivo a descargar

remote_url = 'https://www.google.com/robots.txt'

# Definimos el nombre del archivo local a guardar

local_file = 'local_copy.txt' 

# Se realiza la descarga y se guarda el archivo de manera local

request.urlretrieve(remote_url, local_file)