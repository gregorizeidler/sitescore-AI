from prometheus_fastapi_instrumentator import Instrumentator
instrumentator = Instrumentator()
def setup_instrumentation(app):
    instrumentator.instrument(app).expose(app, include_in_schema=False, should_gzip=True)
