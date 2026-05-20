import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('accounts', '0002_user_mfa_secret_authevent_usersession'), ('companies', '0001_initial'), ('devices', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='MaintenanceWindow',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], db_index=True, default='draft', max_length=32)),
                ('planned_start', models.DateTimeField(db_index=True)),
                ('planned_end', models.DateTimeField(db_index=True)),
                ('expected_outage_minutes', models.PositiveIntegerField(default=0)),
                ('affected_services', models.JSONField(blank=True, default=list)),
                ('affected_customers', models.PositiveIntegerField(default=0)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('notification_sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_maintenance_windows', to='accounts.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maintenance_windows', to='companies.company')),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='maintenance_windows', to='devices.device')),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requested_maintenance_windows', to='accounts.user')),
            ],
            options={'db_table': 'ops_maintenance_windows'},
        ),
    ]

