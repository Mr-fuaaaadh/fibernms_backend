import uuid

from django.db import models


class EngineerTeam(models.Model):
    class TeamType(models.TextChoices):
        NOC = 'noc', 'NOC'
        FIELD = 'field', 'Field'
        IP_CORE = 'ip_core', 'IP Core'
        ACCESS = 'access', 'Access'
        MANAGER = 'manager', 'Manager'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='engineer_teams')
    name = models.CharField(max_length=255)
    team_type = models.CharField(max_length=32, choices=TeamType.choices, default=TeamType.NOC, db_index=True)
    escalation_email = models.EmailField(blank=True, default='')
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ops_engineer_teams'
        constraints = [
            models.UniqueConstraint(fields=['company', 'name'], name='uq_ops_team_company_name'),
        ]
        indexes = [models.Index(fields=['company', 'team_type', 'is_active'])]


class EngineerProfile(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        BUSY = 'busy', 'Busy'
        OFF_SHIFT = 'off_shift', 'Off Shift'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='engineer_profiles')
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='engineer_profile')
    team = models.ForeignKey(EngineerTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='engineers')
    skills = models.JSONField(default=list, blank=True)
    availability = models.CharField(max_length=32, choices=Availability.choices, default=Availability.AVAILABLE, db_index=True)
    current_load = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ops_engineer_profiles'
        indexes = [
            models.Index(fields=['company', 'availability', 'current_load']),
            models.Index(fields=['company', 'team']),
        ]

