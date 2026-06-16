from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Deriv Organismo")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
