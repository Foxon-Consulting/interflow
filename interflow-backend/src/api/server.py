import uvicorn
import os

def run():
    """Point d'entrée pour démarrer le serveur API."""
    # Configuration pour conteneur ou développement local
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "5000"))

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=False,
        use_colors=False
    )


if __name__ == "__main__":
    run()
