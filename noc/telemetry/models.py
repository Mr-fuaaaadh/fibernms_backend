import uuid

from django.db import models


class TelemetryReading(models.Model):
    class Parameter(models.TextChoices):
        RX_POWER = 'rx_power', 'RX Power'
        TX_POWER = 'tx_power', 'TX Power'
        TEMPERATURE = 'temperature', 'Temperature'
        PACKET_LOSS = 'packet_loss', 'Packet Loss'
        LATENCY = 'latency', 'Latency'
        CPU_USAGE = 'cpu_usage', 'CPU Usage'
        MEMORY_USAGE = 'memory_usage', 'Memory Usage'
        OPTICAL_LOSS = 'optical_loss', 'Optical Loss'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(db_index=True)
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE, related_name='telemetry')
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='telemetry')
    parameter = models.CharField(max_length=32, choices=Parameter.choices, db_index=True)
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'noc_telemetry_readings'
        indexes = [
            models.Index(fields=['company', 'device', 'parameter', '-timestamp']),
            models.Index(fields=['company', 'parameter', '-timestamp']),
            models.Index(fields=['company', '-timestamp']),
        ]
