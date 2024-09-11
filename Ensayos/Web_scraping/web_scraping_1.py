import requests
from bs4 import BeautifulSoup

url = 'https://nssdc.gsfc.nasa.gov/planetary/factsheet/'

response = requests.get(url)

if response.status_code == 200:
    print('Obtuvimos la pagina')
    soup = BeautifulSoup(response.text, 'html.parser')
    tabla = soup.find_all('tr')

    # print(len(tabla))

    for dato in tabla:
        info = dato.find('td')
        if info:
            print(info.text)
    
else:
    print(f'Error al cargar la web código: {response.status_code}' )

