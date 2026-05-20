import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('accounts', '0002_user_mfa_secret_authevent_usersession'),
        ('companies', '0001_initial'),
        ('customers', '0001_initial'),
        ('devices', '0001_initial'),
        ('workforce', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('incident_number', models.CharField(db_index=True, max_length=32)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('severity', models.CharField(choices=[('sev1', 'SEV1 - Critical Outage'), ('sev2', 'SEV2 - Major Degradation'), ('sev3', 'SEV3 - Minor Degradation'), ('sev4', 'SEV4 - Informational')], db_index=True, max_length=16)),
                ('status', models.CharField(choices=[('open', 'Open'), ('investigating', 'Investigating'), ('mitigated', 'Mitigated'), ('resolved', 'Resolved'), ('closed', 'Closed')], db_index=True, default='open', max_length=32)),
                ('impact', models.TextField(blank=True, default='')),
                ('affected_customers', models.PositiveIntegerField(default=0)),
                ('affected_services', models.JSONField(blank=True, default=list)),
                ('rca_summary', models.TextField(blank=True, default='')),
                ('rca_completed_at', models.DateTimeField(blank=True, null=True)),
                ('outage_started_at', models.DateTimeField(blank=True, null=True)),
                ('outage_ended_at', models.DateTimeField(blank=True, null=True)),
                ('detected_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('mitigated_at', models.DateTimeField(blank=True, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incidents', to='workforce.engineerteam')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_incidents', to='accounts.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incidents', to='companies.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_incidents', to='accounts.user')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incidents', to='customers.customeraccount')),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incidents', to='devices.device')),
            ],
            options={'db_table': 'ops_incidents'},
        ),
        migrations.CreateModel(
            name='IncidentTimelineEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_type', models.CharField(db_index=True, max_length=64)),
                ('message', models.TextField()),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incident_timeline_events', to='accounts.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_timeline_events', to='companies.company')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeline', to='incidents.incident')),
            ],
            options={'db_table': 'ops_incident_timeline'},
        ),
    ]
