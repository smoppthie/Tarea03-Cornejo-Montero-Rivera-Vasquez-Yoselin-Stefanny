import sys
import getopt
import requests
import subprocess
import platform
import time

def get_mac_info(mac_address):
    """
    Consulta la API de maclookup.app para obtener el fabricante de una dirección MAC.
    
    Parámetros:
        mac_address (str): Dirección MAC a consultar.
        
    Retorna:
        str: Nombre del fabricante o un mensaje de error.
    """
    url = f"https://api.maclookup.app/v2/macs/{mac_address}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            company = data.get('company', 'Fabricante no encontrado')
            return company
        else:
            return "Error al consultar la API"
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {e}"

def show_arp_table():
    """
    Obtiene la tabla ARP del sistema y muestra los fabricantes de las direcciones MAC encontradas.
    """
    try:
        # Detecta el sistema operativo para usar el comando adecuado
        if platform.system() == "Windows":
            # Comando para Windows
            result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE)
        else:
            # Comando para Linux/Unix
            result = subprocess.run(['arp', '-n'], stdout=subprocess.PIPE)
        
        # Decodifica la salida y la divide en líneas
        arp_table = result.stdout.decode('utf-8').splitlines()
        
        # Recorre cada línea de la tabla ARP
        for line in arp_table:
            parts = line.split()
            # Verifica que la línea tenga suficientes partes para contener una dirección MAC
            if len(parts) >= 3:
                ip_address = parts[0]
                mac_address = parts[1] if platform.system() == "Windows" else parts[2]
                # Consulta el fabricante de la dirección MAC
                vendor = get_mac_info(mac_address)
                print(f"{ip_address} / {mac_address} / {vendor}")
    except Exception as e:
        print(f"Error al obtener la tabla ARP: {e}")

def main(argv):
    """
    Función principal que procesa los argumentos de línea de comandos y ejecuta las acciones correspondientes.
    
    Parámetros:
        argv (list): Lista de argumentos pasados al script.
    """
    mac_address = ''
    try:
        # Define las opciones válidas y procesa los argumentos
        opts, args = getopt.getopt(argv, "hm:a", ["help", "mac=", "arp"])
    except getopt.GetoptError:
        # Si hay un error en los argumentos, muestra el uso correcto y termina
        print('Uso: OUILookup.py --mac <mac_address> | --arp | --help')
        sys.exit(2)

    # Procesa las opciones y argumentos
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # Muestra el mensaje de ayuda y termina
            print('Uso: OUILookup.py --mac <mac_address> | --arp | --help')
            print(' --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.')
            print(' --arp: muestra los fabricantes de los host disponibles en la tabla ARP.')
            print(' --help: muestra este mensaje y termina.')
            sys.exit()
        elif opt in ("--mac"):
            # Guarda la dirección MAC proporcionada
            mac_address = arg
        elif opt in ("--arp"):
            # Llama a la función para mostrar la tabla ARP y termina
            show_arp_table()
            sys.exit()

    if mac_address:
        # Si se proporcionó una dirección MAC, consulta el fabricante
        start_time = time.time()
        fabricante = get_mac_info(mac_address)
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convertir a milisegundos
        print(f"MAC address: {mac_address}")
        print(f"Fabricante: {fabricante}")
        print(f"Tiempo de respuesta: {elapsed_time:.2f}ms")
    else:
        # Si no se proporcionaron argumentos válidos, muestra el uso correcto
        print('Uso: OUILookup.py --mac <mac_address> | --arp | --help')

if __name__ == "__main__":
    # Llama a la función principal pasando los argumentos de línea de comandos
    main(sys.argv[1:])

