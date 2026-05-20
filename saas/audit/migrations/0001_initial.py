import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('accounts', '0002_user_mfa_secret_authevent_usersession'),
        ('companies', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]
    operations = [
        migrations.CreateModel(
            name='AuditEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(db_index=True, max_length=128)),
                ('object_id', models.CharField(blank=True, db_index=True, default='', max_length=64)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_events', to='accounts.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audit_events', to='companies.company')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype')),
            ],
            options={'db_table': 'saas_audit_events'},
        ),
    ]

