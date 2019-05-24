def save_config(key, value):
	from taosha_perf.models import SysConfig
	conf = None
	try:
		conf = SysConfig.objects.get(config_name=key)
	except:
		pass
	if not conf:
		conf = SysConfig(config_name=key, config_value=value)
	else:
		conf.config_value = value
	conf.save()
	pass