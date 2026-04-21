import argparse
import sys
from server import start_server
from client import start_client
from clistack import ansi


def interactive_menu():
    ansi.print_color("=== Chat TCP ===", ansi.Color.YELLOW, bold=True)
    ansi.print_color("1) Servidor", ansi.Color.YELLOW)
    ansi.print_color("2) Cliente", ansi.Color.YELLOW)

    opcion = input("Selecciona (1/2): ").strip()

    if opcion == "1":
        # server maneja su propio modo interactivo
        from server import interactive_mode
        interactive_mode()

    elif opcion == "2":
        # client maneja su propio modo interactivo
        from client import interactive_mode
        interactive_mode()

    else:
        print("Opción inválida")


def main():
    parser = argparse.ArgumentParser(description="Chat TCP")
    subparsers = parser.add_subparsers(dest="mode")

    # server
    server_parser = subparsers.add_parser("server")
    server_parser.add_argument("--host")
    server_parser.add_argument("--port", type=int)

    # client
    client_parser = subparsers.add_parser("client")
    client_parser.add_argument("--host")
    client_parser.add_argument("--port", type=int)
    client_parser.add_argument("--name")

    # Sin argumentos → menu interactivo general
    if len(sys.argv) == 1:
        interactive_menu()
        return

    args = parser.parse_args()

    if args.mode == "server":
        host = args.host or "0.0.0.0"
        port = args.port or 5000
        start_server(host, port)

    elif args.mode == "client":
        host = args.host or "127.0.0.1"
        port = args.port or 5000
        start_client(host, port, args.name)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo...")
