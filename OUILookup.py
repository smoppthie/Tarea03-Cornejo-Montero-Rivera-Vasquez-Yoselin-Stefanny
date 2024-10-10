#Integrantes: Yoselin Cornejo Rivera 21.063.962-4, Stefanny Montero Vasquez 21.263.741-6
import sys
import getopt
import requests
import subprocess
import platform
import time

# Función para obtener el fabricante a partir de una dirección MAC usando la API de maclookup.app
def get_mac_info(mac_address):
    """
    Consulta la API de maclookup.app para obtener el fabricante de una dirección MAC.
    
    Parámetros:
        mac_address (str): Dirección MAC a consultar.
        
    Retorna:
        str: Nombre del fabricante o un mensaje de error.
    """
    # URL de la API para consultar el fabricante de la MAC
    url = f"https://api.maclookup.app/v2/macs/{mac_address}"
    
    try:
        # Realiza la solicitud GET a la API
        response = requests.get(url)
        if response.status_code == 200:
            # Si la respuesta es exitosa, extrae la compañía de la respuesta JSON
            data = response.json()
            company = data.get('company', 'Fabricante no encontrado')  # Devuelve "Fabricante no encontrado" si no hay datos
            return company
        else:
            # Si no se pudo completar la consulta a la API, devuelve un mensaje de error
            return "Error al consultar la API"
    except requests.exceptions.RequestException as e:
        # Captura los errores de conexión y devuelve un mensaje apropiado
        return f"Error de conexión: {e}"

# Función para mostrar la tabla ARP del sistema y obtener el fabricante de cada dirección MAC encontrada
def show_arp_table():
    """
    Obtiene la tabla ARP del sistema y muestra los fabricantes de las direcciones MAC encontradas.
    """
    try:
        # Verifica el sistema operativo para usar el comando ARP adecuado
        if platform.system() == "Windows":
            # Ejecuta el comando ARP en Windows
            result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE)
        else:
            # Ejecuta el comando ARP en Linux/Unix
            result = subprocess.run(['arp', '-n'], stdout=subprocess.PIPE)
        
        # Decodifica la salida y la convierte en una lista de líneas
        arp_table = result.stdout.decode('utf-8').splitlines()
        
        # Recorre cada línea de la tabla ARP para extraer las direcciones MAC
        for line in arp_table:
            parts = line.split()
            # Verifica que la línea tenga suficientes partes para contener una dirección MAC
            if len(parts) >= 3:
                ip_address = parts[0]
                mac_address = parts[1] if platform.system() == "Windows" else parts[2]
                # Consulta el fabricante de la dirección MAC
                vendor = get_mac_info(mac_address)
                # Muestra la dirección IP, la dirección MAC y el fabricante correspondiente
                print(f"{ip_address} / {mac_address} / {vendor}")
    except Exception as e:
        # Captura cualquier excepción y muestra un mensaje de error
        print(f"Error al obtener la tabla ARP: {e}")

# Función principal que maneja los argumentos de la línea de comandos
def main(argv):
    """
    Función principal que procesa los argumentos de línea de comandos y ejecuta las acciones correspondientes.
    
    Parámetros:
        argv (list): Lista de argumentos pasados al script.
    """
    mac_address = ''  # Variable para almacenar la dirección MAC proporcionada
    try:
        # Define las opciones válidas y procesa los argumentos pasados
        opts, args = getopt.getopt(argv, "hm:a", ["help", "mac=", "arp"])
    except getopt.GetoptError:
        # Si hay un error en los argumentos, muestra el uso correcto y termina el programa
        print('Uso: OUILookup.py --mac <mac_address> | --arp | --help')
        sys.exit(2)

    # Recorre los argumentos y opciones proporcionados
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # Muestra el mensaje de ayuda y termina el programa
            print('Uso: OUILookup.py --mac <mac_address> | --arp | --help')
            print(' --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.')
            print(' --arp: muestra los fabricantes de los host disponibles en la tabla ARP.')
            print(' --help: muestra este mensaje y termina.')
            sys.exit()
        elif opt in ("--mac"):
            # Guarda la dirección MAC proporcionada para consultar más tarde
            mac_address = arg
        elif opt in ("--arp"):
            # Llama a la función para mostrar la tabla ARP y termina el programa
            show_arp_table()
            sys.exit()

    # Si se proporcionó una dirección MAC, consulta el fabricante
    if mac_address:
        start_time = time.time()  # Registra el tiempo de inicio de la consulta
        fabricante = get_mac_info(mac_address)  # Obtiene el fabricante de la MAC
        end_time = time.time()  # Registra el tiempo de finalización de la consulta
        elapsed_time = (end_time - start_time) * 1000  # Calcula el tiempo en milisegundos
        # Muestra la información de la dirección MAC y el fabricante
        print(f"MAC address: {mac_address}")
        print(f"Fabricante: {fabricante}")
        print(f"Tiempo de respuesta: {elapsed_time:.2f}ms")
    else:
        # Si no se proporcionaron argumentos válidos, muestra el uso correcto
        print('Uso: OUILookup.py --mac <mac_address> | --arp | --help')

# Punto de entrada del programa
if __name__ == "__main__":
    # Llama a la función principal pasando los argumentos de línea de comandos
    main(sys.argv[1:])
