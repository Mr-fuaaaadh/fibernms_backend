import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('companies', '0001_initial'), ('customers', '0001_initial'), ('devices', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='SLAProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('scope', models.CharField(choices=[('customer', 'Customer'), ('device', 'Device'), ('service', 'Service')], db_index=True, max_length=32)),
                ('service_name', models.CharField(blank=True, default='', max_length=255)),
                ('uptime_target', models.DecimalField(decimal_places=2, default=99.9, max_digits=5)),
                ('mttr_minutes_target', models.PositiveIntegerField(default=240)),
                ('mtbf_hours_target', models.PositiveIntegerField(default=720)),
                ('packet_loss_target', models.DecimalField(decimal_places=2, default=1.0, max_digits=5)),
                ('latency_ms_target', models.PositiveIntegerField(default=100)),
                ('response_time_minutes_target', models.PositiveIntegerField(default=30)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sla_profiles', to='companies.company')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sla_profiles', to='customers.customeraccount')),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sla_profiles', to='devices.device')),
            ],
            options={'db_table': 'ops_sla_profiles'},
        ),
        migrations.CreateModel(
            name='SLAMetricSnapshot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('period_start', models.DateTimeField(db_index=True)),
                ('period_end', models.DateTimeField(db_index=True)),
                ('uptime_percent', models.DecimalField(decimal_places=3, max_digits=6)),
                ('mttr_minutes', models.PositiveIntegerField(default=0)),
                ('mtbf_hours', models.PositiveIntegerField(default=0)),
                ('packet_loss_percent', models.DecimalField(decimal_places=3, default=0, max_digits=6)),
                ('latency_ms', models.PositiveIntegerField(default=0)),
                ('response_time_minutes', models.PositiveIntegerField(default=0)),
                ('is_breached', models.BooleanField(db_index=True, default=False)),
                ('breach_reasons', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sla_metric_snapshots', to='companies.company')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metric_snapshots', to='sla.slaprofile')),
            ],
            options={'db_table': 'ops_sla_metric_snapshots'},
        ),
        migrations.CreateModel(
            name='SLATimer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('target_type', models.CharField(choices=[('incident', 'Incident'), ('ticket', 'Ticket')], db_index=True, max_length=32)),
                ('target_id', models.UUIDField(db_index=True)),
                ('metric', models.CharField(db_index=True, max_length=64)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('due_at', models.DateTimeField(db_index=True)),
                ('stopped_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('running', 'Running'), ('paused', 'Paused'), ('met', 'Met'), ('breached', 'Breached'), ('cancelled', 'Cancelled')], db_index=True, default='running', max_length=32)),
                ('breach_notified_at', models.DateTimeField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sla_timers', to='companies.company')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timers', to='sla.slaprofile')),
            ],
            options={'db_table': 'ops_sla_timers'},
        ),
    ]

