from django.db import models



class Intradaymarketdata(models.Model):
    dt = models.DateTimeField(primary_key=True)
    trade = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    numtrades = models.IntegerField()
    lowtoday = models.DecimalField(max_digits=10, decimal_places=2)
    hightoday = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'intradaymarketdata'


class Modelfactors(models.Model):
    dt = models.DateTimeField(primary_key=True)
    ret_5_min = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    ret_30_min = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    ret_1_hour = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    ret_3_hour = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    ret_6_hour = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    ret_12_hour = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    ret_24_hour = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    volume_5_min_vnorm = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    volume_30_min_vnorm = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    volume_1_hour_vnorm = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    volume_3_hour_vnorm = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    volume_6_hour_vnorm = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    volume_12_hour_vnorm = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    volume_24_hour_vnorm = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    volatility_1_hour = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    volatility_3_hour = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    volatility_6_hour = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    volatility_12_hour = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    volatility_24_hour = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    avg_trd_size_5_min = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    avg_trd_size_30_min = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    avg_trd_size_1_hour = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    avg_trd_size_3_hour = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    avg_trd_size_6_hour = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    avg_trd_size_12_hour = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    avg_trd_size_24_hour = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    ret_in_1_hour = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    ret_in_12_hour = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    ret_in_24_hour = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    volume_5_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    volume_30_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    volume_1_hour = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    volume_3_hour = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    volume_6_hour = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    volume_12_hour = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    volume_24_hour = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modelfactors'
