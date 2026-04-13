import typer
# Importe le module init que tu viens de créer
from devctl.commands import init

app = typer.Typer()

# Ajoute le sous-menu init à l'application principale
app.add_typer(init.app, name="init", help="Initialise un nouveau projet avec sa base de code.")

@app.callback()
def callback():
    """
    devctl : L'orchestrateur local pour tes projets Spring/Angular
    """
    pass

@app.command()
def ping():
    """
    Commande de test pour vérifier que le CLI répond.
    """
    typer.secho("pong ! Le CLI devctl est opérationnel.", fg=typer.colors.GREEN, bold=True)

def main():
    app()

if __name__ == "__main__":
    main()