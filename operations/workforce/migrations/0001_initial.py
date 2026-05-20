import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('accounts', '0002_user_mfa_secret_authevent_usersession'), ('companies', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='EngineerTeam',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('team_type', models.CharField(choices=[('noc', 'NOC'), ('field', 'Field'), ('ip_core', 'IP Core'), ('access', 'Access'), ('manager', 'Manager')], db_index=True, default='noc', max_length=32)),
                ('escalation_email', models.EmailField(blank=True, default='', max_length=254)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engineer_teams', to='companies.company')),
            ],
            options={'db_table': 'ops_engineer_teams'},
        ),
        migrations.CreateModel(
            name='EngineerProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('skills', models.JSONField(blank=True, default=list)),
                ('availability', models.CharField(choices=[('available', 'Available'), ('busy', 'Busy'), ('off_shift', 'Off Shift')], db_index=True, default='available', max_length=32)),
                ('current_load', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engineer_profiles', to='companies.company')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='engineers', to='workforce.engineerteam')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='engineer_profile', to='accounts.user')),
            ],
            options={'db_table': 'ops_engineer_profiles'},
        ),
    ]

