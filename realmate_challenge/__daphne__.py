from daphne.cli import CommandLineInterface

def main():
    args = ["realmate_challenge.asgi:application", "-p", "8000"]
    CommandLineInterface().run(args)

