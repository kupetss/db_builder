from ui import ConsoleUI


def main() -> None:
    ui = ConsoleUI()

    try:
        ui.run()
    except KeyboardInterrupt:
        print("\nВыход")


if __name__ == "__main__":
    main()