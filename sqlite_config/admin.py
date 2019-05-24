from xxx.models import SysConfig
class SysConfigAdmin(admin.ModelAdmin):
    list_display = ('config_name', 'config_value')
    fields = ('config_name', 'config_value')


admin.site.register(SysConfig, SysConfigAdmin)