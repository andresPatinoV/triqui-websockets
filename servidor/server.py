import asyncio
import websockets

clientes = {}
tablero = [['.' for _ in range(3)] for _ in range(3)]

class Cliente:
    def __init__(self, nombre, simbolo):
        self.nombre = nombre
        self.simbolo = simbolo
        self.victorias = 0

def imprimir_tablero(tablero):
    for fila in tablero:
        print(" ".join(fila))

async def chat_server(websocket, path):
    try:
        async for mensaje in websocket:
            print(mensaje)
            try:
                
                estado = ''
                mensajeSplit = mensaje.split('#')
                if mensajeSplit[1] == 'INSCRIBIR':
                    if len(clientes) <= 2:
                        simbolo = 'X' if len(clientes) == 0 else 'O'
                        clientes[websocket] = Cliente(mensajeSplit[2], simbolo)
                        estado = 'inscrito'
                    else:
                        estado = 'capacidad'

                    print(estado)
                    print(mensajeSplit[1])
                
                elif mensajeSplit[1] == 'JUGADA':
                    jugada = mensajeSplit[2].split('-')
                    fila = int(jugada[0])
                    columna = int(jugada[1])
                    estado = 'jugadaOK'
                    print(estado)

                
                else:
                    estado = 'error'
                print(estado)

                for ws, cliente in clientes.items():
                    print(f"{cliente.nombre} {cliente.simbolo} {cliente.victorias}")
                    print(estado)
                    if websocket != ws:
                        if estado == 'inscrito':
                            mensaje2Clientes = f"{cliente.nombre} se ha unido a la partida"
                        elif estado == 'capacidad':
                            mensaje2Clientes = f"Servidor Lleno, intente mas tarde"
                        elif estado == 'jugadaOK':
                            mensaje2Clientes = f"{cliente.nombre}: {fila}-{columna}"
                        else:
                            mensaje2Clientes = f"ERROR DESCONOCIDO DESDE TU CLIENTE"

                        await websocket.send(mensaje2Clientes)
                        print('awat1')
                    else:
                        if estado == 'inscrito':
                            mensaje2Cliente = f"Bienvenido: {cliente.nombre}"
                        elif estado == 'capacidad':
                            mensaje2Cliente = f""
                        elif estado == 'jugadaOK':
                            tablero[fila][columna] = cliente.simbolo
                            mensaje2Clientes = f"{cliente.nombre}: {fila}-{columna}"
                        else:
                            mensaje2Clientes = f"ERROR DESCONOCIDO DESDE EL RIVAL"

                        await ws.send(mensaje2Cliente)
                        print('awat2')

                    imprimir_tablero(tablero)

                
            except:
                print('except')
                for ws, cliente in clientes.items():
                    if websocket == ws:
                        mensajeError = f"ERROR: El mensaje no tiene un formato reconocido!"
                        await ws.send(mensajeError)
                    else:
                        mensajeError = f"ERROR: El mensaje de tu rival no tiene un formato reconocido!"
                        await ws.send(mensajeError)
            
    finally:
        del clientes[websocket]

if __name__ == "__main__":
    start_server = websockets.serve(chat_server, "localhost", 8300)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()