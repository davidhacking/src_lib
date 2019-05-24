class SysConfig(models.Model):
    id = models.AutoField(primary_key=True)
    config_name = models.CharField('配置名称', max_length=128)
    config_value = models.CharField('配置数值', max_length=2048)

    def __str__(self):
        return str("id: %s, name: %s, value: %s" % (self.id, self.config_name, self.config_value))