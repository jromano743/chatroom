import socket
import threading
import argparse
import sys
from clistack import ansi

lock = threading.Lock()


def receive_messages(sock, my_name):
    while True:
        try:
            msg = sock.recv(1024).decode("utf-8")
            if not msg:
                break

            with lock:
                if msg.startswith("[") and "]:" in msg:
                    name_part, text_part = msg.split("]:", 1)
                    name_part += "]"

                    full_msg = f"{name_part}:{text_part}"

                    if name_part == f"[{my_name}]":
                        ansi.print_color(full_msg, ansi.Color.GREEN, bold=True)
                    else:
                        ansi.print_color(full_msg, ansi.Color.CYAN, bold=True)
                else:
                    ansi.print_color(msg, ansi.Color.YELLOW)

        except:
            break

    try:
        sock.close()
    except:
        pass


def start_client(host="127.0.0.1", port=5000, name=None):
    if not name:
        name = input("Tu nombre: ").strip()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((host, port))
    except:
        ansi.print_color(f"No se pudo conectar a {host}:{port}", ansi.Color.RED)
        return

    client.send(name.encode("utf-8"))

    threading.Thread(
        target=receive_messages,
        args=(client, name),
        daemon=True
    ).start()

    ansi.print_color(
        f"Conectado a {host}:{port} como {name}",
        ansi.Color.GREEN
    )

    ansi.print_color("Escribe mensajes (Ctrl+C para salir)", ansi.Color.YELLOW)

    try:
        while True:
            msg = input().strip()

            sys.stdout.write("\033[F\033[K")
            sys.stdout.flush()

            if msg:
                client.send(msg.encode("utf-8"))

    except KeyboardInterrupt:
        pass

    finally:
        try:
            client.close()
        except:
            pass

        ansi.print_color("Conexión cerrada.", ansi.Color.RED)


# -------------------------
# INTERACTIVE MODE
# -------------------------
def interactive_mode():
    ansi.print_color("=== Configuración del cliente ===", ansi.Color.YELLOW, bold=True)

    host = input("Host [127.0.0.1]: ").strip() or "127.0.0.1"
    port = input("Port [5000]: ").strip() or "5000"
    name = input("Nombre: ").strip()

    start_client(host, int(port), name)


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente de chat TCP")
    parser.add_argument("--host", help="Host del servidor")
    parser.add_argument("--port", type=int, help="Puerto del servidor")
    parser.add_argument("--name", help="Nombre de usuario")

    if len(sys.argv) == 1:
        interactive_mode()
    else:
        args = parser.parse_args()

        host = args.host or "127.0.0.1"
        port = args.port or 5000
        name = args.name

        start_client(host, port, name)
