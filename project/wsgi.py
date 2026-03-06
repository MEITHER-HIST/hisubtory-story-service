"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
sys.path.append("/usr/local/lib/python3.12/site-packages")
sys.path.append("/app")
from django.core.wsgi import get_wsgi_application
from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Tracing 서비스 이름 설정
resource = Resource(attributes={
    "service.name": os.getenv("OTEL_SERVICE_NAME", "story-service")
})

# Tracer Provider 설정
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317"), insecure=True)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Django 자동 추적 활성화
DjangoInstrumentor().instrument()

application = get_wsgi_application()
