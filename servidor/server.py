import asyncio
import websockets

clientes = {}
tablero = [['.' for _ in range(3)] for _ in range(3)]
simbolosDisponibles = ['X', 'O']
jugadasPartida = []

class Cliente:
    def __init__(self, nombre, simbolo):
        self.nombre = nombre
        self.simbolo = simbolo
        self.victorias = 0
        self.estado = 'bloqueado'

def imprimir_tablero():
    for fila in tablero:
        print(" ".join(fila))

def estadoTablero():
    contenido_tablero = '-'.join('-'.join(fila) for fila in tablero)
    return contenido_tablero

def validaNombreJugador(nombreCliente, websocket):
    for ws, cliente in clientes.items():
        print(cliente.nombre)
        if websocket != ws:
            if cliente.nombre == nombreCliente:

                return False 
    return True

def validarInscripcion(nombreCliente):
    if len(clientes) < 2:
        #simbolo = 'X' if len(clientes) == 0 else 'O'
        cliente = Cliente(nombreCliente, '.')
        return True, cliente
    else:
        return False, False
    
def verJugadores():
    listaJugadores = 'clientes: '
    for cliente in clientes.values():
        listaJugadores += f'{cliente.nombre} '
    return listaJugadores

def reiniciarTablero():
    global tablero
    print(tablero)
    i=0
    for fila in tablero:
        if fila.count('.') == 0:
            i+=1
    print(i)
    if i>2:
        tablero = [['.' for _ in range(3)] for _ in range(3)]
        print('reiniciando')
    
def validarJugada(fila, columna):
    global tablero
    if tablero[fila][columna] == '.':
        return True
    else:
        return False

def verificarGanador():
    global tablero
    for fila in tablero:
        if fila.count(fila[0]) == len(fila) and fila[0] != '.':
            tablero = [['.' for _ in range(3)] for _ in range(3)]
            return True
    
    for col in range(len(tablero)):
        columna = [tablero[fila][col] for fila in range(len(tablero))]
        if columna.count(columna[0]) == len(columna) and columna[0] != '.':
            tablero = [['.' for _ in range(3)] for _ in range(3)]
            return True
        
    if tablero[0][0] == tablero[1][1] == tablero[2][2] != '.':
        tablero = [['.' for _ in range(3)] for _ in range(3)]
        return True
    if tablero[0][2] == tablero[1][1] == tablero[2][0] != '.':
        tablero = [['.' for _ in range(3)] for _ in range(3)]
        return True
    
    return False

async def chat_server(websocket, path):
    try:
        async for mensaje in websocket:
            print('-----------------------------------------------------------------')
            try:
                print(mensaje)
                estado = ''
                ganador = False
                mensajeSplit = mensaje.split('#')

                if mensajeSplit[1] == 'INSCRIBIR':
                    capacidad, cliente = validarInscripcion(mensajeSplit[2])
                    estado = 'inscrito' if capacidad else 'capacidadSuperada'
                    estado = 'inscrito' if validaNombreJugador(cliente.nombre, websocket) else 'nombreRepetido'
                    if estado == 'inscrito':
                        clientes[websocket] = cliente
                        partidaIniciada = False
                    elif estado == 'nombreRepetido':
                        await websocket.send(f"#NOK-NOMBRE-REPETIDO#")
                
                elif mensajeSplit[1] == 'JUGADA':
                    jugada = mensajeSplit[2].split('-')
                    fila = int(jugada[0])
                    columna = int(jugada[1])
                    estado = 'jugadaOK' if validarJugada(fila, columna) else 'jugadaNOK'
                    if estado == 'jugadaOK':
                        tablero[fila][columna] = clientes[websocket].simbolo
                        jugadasPartida.append(clientes[websocket].simbolo)
                        ganador = verificarGanador()
                        if ganador:
                            clientes[websocket].victorias += 1
                            marcador = ''
                            for cliente in clientes.values():
                                marcador += f"{cliente.nombre}:{cliente.victorias}#"

                else:
                    estado = 'error'

                for ws, cliente in clientes.items():
                    print(f"{cliente.nombre} {cliente.simbolo} {cliente.victorias}")
                    print(estado)

                    if websocket != ws:
                        print('socket diferente al que envio el mensaje')

                        if estado == 'inscrito':
                            mensaje2Clientes = f"{clientes[websocket].nombre} se ha unido a la partida"
                            
                        elif estado == 'jugadaOK':
                            mensaje2Clientes = f"#JUGADARIVAL-OK#{fila}-{columna}#"

                        else:
                            mensaje2Clientes = f"ERROR DESCONOCIDO DESDE OTRO CLIENTE"

                        await ws.send(mensaje2Clientes)

                        if len(clientes) == 2 and not partidaIniciada:
                            await ws.send(f"#JUEGO-INICIADO#O#")

                        if ganador:
                            await ws.send(f"#GANADOR#{clientes[websocket].nombre}#")
                            await ws.send(f"#PUNTUACION#{marcador}")

                       
                    else:
                        print('Desde este socket se envio el mensaje')
                        if estado == 'inscrito':
                            cliente.simbolo = simbolosDisponibles.pop()
                            mensaje2Cliente = f"#INSCRIPCION-OK#{cliente.simbolo}"
                            
                        elif estado == 'capacidadSuperada':
                            mensaje2Cliente = f"#NOK-CAPACIDAD#"

                        elif estado == 'nombreRepetido':
                            mensaje2Cliente = f"#NOK-NOMBRE-REPETIDO#"

                        elif estado == 'jugadaOK':
                            
                            mensaje2Cliente = f"#JUGADA-OK#"

                        else:
                            mensaje2Cliente = f"ERROR DESCONOCIDO DESDE EL RIVAL"

                        await websocket.send(mensaje2Cliente)

                        if len(clientes) == 2 and not partidaIniciada:
                            await websocket.send(f"#JUEGO-INICIADO#O#")
                            partidaIniciada = True

                        if ganador:
                            await websocket.send(f"#GANADOR#{clientes[websocket].nombre}#")
                            await websocket.send(f"#PUNTUACION#{marcador}")

                    reiniciarTablero()

                    print(estadoTablero())
                    imprimir_tablero()
                    print(f'cantidad jugadores: {len(clientes)}')
                    print(verJugadores())
                    print(f"simbolos disponibles: {simbolosDisponibles}")
                    print(f"Jugadas partida actual: {jugadasPartida}")
                    

                    await ws.send(f"#ESTADO-TABLERO#{estadoTablero()}")


                        

                
            except:
                print('except')
                for ws, cliente in clientes.items():
                    
                    if websocket == ws:
                        mensajeError = f"EXCEPT: ERROR DESCONOCIDO DESDE TU CLIENTE"
                        await ws.send(mensajeError)

                    else:
                        mensajeError = f"EXCEPT: ERROR DESCONOCIDO DESDE OTRO CLIENTE"
                        await ws.send(mensajeError)
            
    finally:
        cliente = clientes[websocket]
        simbolosDisponibles.append(cliente.simbolo)
        del clientes[websocket]


if __name__ == "__main__":
    start_server = websockets.serve(chat_server, "localhost", 8300)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()