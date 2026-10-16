"""
Tiny second service - exists specifically to give the main app
something real to call, so distributed tracing has an actual chain
to trace instead of a single hop.
"""
import secrets

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI(title="greeting-service")
FastAPIInstrumentor.instrument_app(app)

GREETINGS = [
    "Hey there!",
    "Welcome to the Single-VM SRE Platform.",
    "All systems observed.",
    "Running lean on 1GB of RAM.",
]


@app.get("/greet")
def greet():
    return {"greeting": secrets.choice(GREETINGS)}


@app.get("/healthz")
def health():
    return {"status": "healthy"}
