import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('companies', '0001_initial'), ('workforce', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='EscalationPolicy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('target_type', models.CharField(choices=[('incident', 'Incident'), ('ticket', 'Ticket'), ('sla', 'SLA')], db_index=True, max_length=32)),
                ('severity', models.CharField(blank=True, db_index=True, default='', max_length=32)),
                ('timeout_minutes', models.PositiveIntegerField(default=30)),
                ('steps', models.JSONField(blank=True, default=list)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='escalation_policies', to='companies.company')),
                ('manager_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manager_escalation_policies', to='workforce.engineerteam')),
                ('noc_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='noc_escalation_policies', to='workforce.engineerteam')),
            ],
            options={'db_table': 'ops_escalation_policies'},
        ),
        migrations.CreateModel(
            name='EscalationEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('target_type', models.CharField(db_index=True, max_length=32)),
                ('target_id', models.UUIDField(db_index=True)),
                ('level', models.CharField(choices=[('noc', 'NOC'), ('manager', 'Manager'), ('executive', 'Executive')], db_index=True, max_length=32)),
                ('reason', models.TextField()),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('assigned_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='escalation_events', to='workforce.engineerteam')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='escalation_events', to='companies.company')),
                ('policy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='escalations.escalationpolicy')),
            ],
            options={'db_table': 'ops_escalation_events'},
        ),
    ]
