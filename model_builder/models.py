import numpy as np
from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField(null=True, blank=True)


class ExplainableObject(models.Model):
    label = models.TextField()
    unit = models.CharField(max_length=100)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="explainable_objects")


class ExplainableQuantity(ExplainableObject):
    value = models.FloatField()

def is_list_of_floats_numpy(obj):
    return isinstance(obj, list) and np.all(np.array(obj, dtype=float, copy=False))

class ExplainableHourlyQuantities(models.Model):
    values = models.JSONField(validators=[is_list_of_floats_numpy])
    start_date = models.DateTimeField()


class Timezone(models.Model):
    label = models.CharField(max_length=255)
    zone = models.CharField(max_length=255)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="timezones")


class Country(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=10)
    average_carbon_intensity = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="country_carbon_intensity")
    year = models.IntegerField()
    timezone = models.ForeignKey(Timezone, on_delete=models.PROTECT, related_name="countries")


class Network(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    bandwidth_energy_intensity = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="network_bandwidth_intensity"
    )


class Hardware(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    carbon_footprint_fabrication = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="hardware_carbon_footprint"
    )
    power = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="hardware_power"
    )
    lifespan = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="hardware_lifespan"
    )
    fraction_of_usage_time = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="hardware_usage_time"
    )


class Storage(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    carbon_footprint_fabrication = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_carbon_footprint"
    )
    power = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_power"
    )
    lifespan = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_lifespan"
    )
    fraction_of_usage_time = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_fraction_usage"
    )
    idle_power = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_idle_power"
    )
    storage_capacity = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_capacity"
    )
    data_replication_factor = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_data_replication"
    )
    data_storage_duration = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_duration"
    )
    base_storage_need = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="storage_need"
    )
    fixed_nb_of_instances = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, null=True, related_name="storage_instances"
    )


class Autoscaling(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    carbon_footprint_fabrication = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_carbon_footprint"
    )
    power = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_power"
    )
    lifespan = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_lifespan"
    )
    fraction_of_usage_time = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_usage_time"
    )
    server_utilization_rate = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_utilization_rate"
    )
    idle_power = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_idle_power"
    )
    ram = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_ram"
    )
    cpu_cores = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_cpu_cores"
    )
    power_usage_effectiveness = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_pue"
    )
    average_carbon_intensity = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_carbon_intensity"
    )
    base_ram_consumption = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_base_ram"
    )
    base_cpu_consumption = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="autoscaling_base_cpu"
    )
    storage = models.ForeignKey(Storage, on_delete=models.PROTECT, null=True, related_name="autoscaling_storage")


class Job(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    job_type = models.CharField(max_length=255, default="undefined")
    server = models.ForeignKey(Autoscaling, on_delete=models.PROTECT, null=True, related_name="jobs")
    data_upload = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="job_data_upload"
    )
    data_download = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="job_data_download"
    )
    data_stored = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="job_data_stored"
    )
    request_duration = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="job_request_duration"
    )
    ram_needed = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="job_ram_needed"
    )
    cpu_needed = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="job_cpu_needed"
    )
    description = models.TextField(blank=True)


class UserJourneyStep(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    user_time_spent = models.OneToOneField(
        ExplainableQuantity, on_delete=models.PROTECT, related_name="user_time_spent_step"
    )
    jobs = models.ManyToManyField(Job, null=True, related_name="uj_steps")


class UserJourney(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    uj_steps = models.ManyToManyField(UserJourneyStep, related_name="user_journeys")


class UsagePattern(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    hourly_user_journey_starts = models.OneToOneField(
        ExplainableHourlyQuantities, on_delete=models.PROTECT, related_name="hourly_user_journey"
    )
    user_journey = models.ForeignKey(UserJourney, on_delete=models.PROTECT, null=True, related_name="usage_patterns")
    devices = models.ManyToManyField(Hardware, null=True, related_name="usage_patterns")
    network = models.ForeignKey(Network, on_delete=models.PROTECT, null=True, related_name="usage_patterns")
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, related_name="usage_patterns")
    system = models.ForeignKey("System", on_delete=models.PROTECT, null=True, related_name="usage_patterns")


class System(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
