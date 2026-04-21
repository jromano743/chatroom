import socket
import threading
import argparse
import sys
from clistack import ansi

clients = []
names = {}
lock = threading.Lock()


def broadcast(message):
    with lock:
        for client in clients[:]:
            try:
                client.send(message)
            except:
                clients.remove(client)


def handle_client(client_socket):
    try:
        name = client_socket.recv(1024).decode("utf-8").strip()

        with lock:
            names[client_socket] = name

        broadcast(f"[{name}] se ha unido al chat.\n".encode("utf-8"))

        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break

            text = msg.decode("utf-8")
            broadcast(f"[{name}]: {text}".encode("utf-8"))

    except:
        pass

    finally:
        with lock:
            name = names.get(client_socket, "Desconocido")

            if client_socket in clients:
                clients.remove(client_socket)

            if client_socket in names:
                del names[client_socket]

        ansi.print_color(f"[{name}] se desconectó.", ansi.Color.MAGENTA)
        broadcast(f"[{name}] salió del chat.\n".encode("utf-8"))

        try:
            client_socket.close()
        except:
            pass


def start_server(host="0.0.0.0", port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((host, port))
    server.listen()

    ansi.print_color(
        f"Servidor iniciado en {host}:{port}",
        ansi.Color.CYAN,
        bold=True
    )

    try:
        while True:
            client_socket, addr = server.accept()

            ansi.print_color(
                f"Nuevo usuario conectado desde {addr}",
                ansi.Color.YELLOW
            )

            with lock:
                clients.append(client_socket)

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket,),
                daemon=True
            )
            thread.start()

    except KeyboardInterrupt:
        ansi.print_color("\nCerrando servidor...", ansi.Color.RED, bold=True)

    finally:
        with lock:
            for client in clients:
                try:
                    client.close()
                except:
                    pass

        try:
            server.close()
        except:
            pass

        ansi.print_color("Servidor cerrado correctamente.", ansi.Color.RED)


def interactive_mode():
    ansi.print_color("=== Configuración del servidor ===", ansi.Color.CYAN, bold=True)

    host = input("Host [0.0.0.0]: ").strip() or "0.0.0.0"
    port = input("Port [5000]: ").strip() or "5000"

    start_server(host, int(port))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Servidor de chat TCP")
    parser.add_argument("--host", help="Host del servidor")
    parser.add_argument("--port", type=int, help="Puerto del servidor")

    if len(sys.argv) == 1:
        interactive_mode()
    else:
        args = parser.parse_args()
        host = args.host or "0.0.0.0"
        port = args.port or 5000
        start_server(host, port)
