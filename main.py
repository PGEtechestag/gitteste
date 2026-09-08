import sys
import traceback

try:
    import customtkinter as ctk
    from ui.main_window import MainWindow

    def main():
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        app = MainWindow()
        app.mainloop()

    if __name__ == "__main__":
        main()
except Exception as e:
    print("=" * 50)
    print("ERRO AO INICIAR O APLICATIVO")
    print("=" * 50)
    print(f"\n{e}\n")
    traceback.print_exc()
    print()
    input("Pressione Enter para fechar...")
    sys.exit(1)
