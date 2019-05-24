# -*- coding: utf-8 -*-
# @author lfwu@corp.netease.com (ChenTao)
# $Id: update.py 91632 2018-12-10 01:49:10Z gzlihao1@CORP.NETEASE.COM $
## @file

import sys
import types
import inspect
import game3d
import imp
from common import log
import _utils

def _update_function(oldobj, newobj):
	oldobj.func_code = newobj.func_code
	oldobj.func_defaults = newobj.func_defaults
	oldobj.func_doc = newobj.func_doc
	_utils.update_closure(oldobj, newobj)
	log.trace('UPDATE FUNCTION, name=%s' % oldobj.func_name)

def _update_activewrapper(oldobj, newobj):
	_update_function(oldobj.func, newobj.func)

def _update_method(oldobj, newobj):
	_update_function(oldobj.im_func, newobj.im_func)

def _is_type_match(v, oldv):
	res = (type(v) == type(oldv))
	if res:
		return res
	return inspect.isclass(v) and inspect.isclass(oldv)

def _get_handler(v):
	func = _update_funcs.get(type(v))
	if func is None:
		if inspect.isclass(v):
			func = _update_class
	return func

def _update_class(oldobj, newobj):
	slots = newobj.__dict__.get('__slots__')
	for k, v in newobj.__dict__.iteritems():
		if slots and k in slots:
			continue
		if k not in oldobj.__dict__:
			setattr(oldobj, k, v)
			# log.trace('ADD CLASS MEMBER, class=%s, name=%s, type=%s' % (str(oldobj), k, str(type(v))))

		oldv = oldobj.__dict__[k]
		if not isinstance(v, types.NoneType) and not isinstance(v, types.NoneType) and not _is_type_match(v, oldv):
			# log.error(
			# 		'TYPE NOT MATCH'
			# 		'class', oldobj,
			# 		'name', k,
			# 		'type_old', type(oldv),
			# 		'type_new', type(v))
			continue

		func = _get_handler(v)
		if func:
			func(oldv, v)
		elif isinstance(k, str) and not k.startswith('__'):
			#更新类的静态成员（注意！！！！！！！不管大小写都更新）
			# class.__dict__是dictproxy类型，不支持oldobj.__dict__[k] = v的方式赋值
			setattr(oldobj, k, v)
			# log.trace('UPDATE CLASS MEMBER, class=%s, name=%s, type=%s' % (
			# 			str(oldobj), k, str(type(v))))
		else:
			pass
			# log.trace('UPDATE CLASS MEMBER, class=%s, name=%s, type=%s' % (
			# 			str(oldobj), k, str(type(v))))


_update_funcs = {
	types.FunctionType : _update_function,
	types.MethodType : _update_method,
	types.ClassType : _update_class,
	types.TypeType : _update_class,
	_utils.active_wrapper: _update_activewrapper,
}

def _call_module_func(module, func_name):
	func = module.__dict__.get(func_name, None)
	if isinstance(func, types.FunctionType):
		func()

def update(module_name):
	# log.trace('UPDATE, module=%s' % module_name)

	old_module = sys.modules.get(module_name)
	if old_module:
		_call_module_func(old_module, '__before_update__')
		old_cache = {}
		for k, v in old_module.__dict__.iteritems():
			old_cache[k] = v

	if not old_module:
		new_module = __import__(module_name)
	else:
		new_module = reload(old_module)

	if not old_module:
		#未import过，不需要update
		_call_module_func(new_module, '__first_import__')
		return new_module

	#old_module和new_module是同一地址,reload时不存在的旧成员不会被删除

	for k, v in new_module.__dict__.iteritems():
		try:
			if k not in old_cache:
				#不需要手动添加，reload时已经在new_module.__dict__中
				# log.trace('ADD MODULE MEMBER, module=%s, name=%s, type=%s' % (
				# 			module_name, k, str(type(v))))
				continue
			oldobj = old_cache[k]

			if not isinstance(v, types.NoneType) and not isinstance(oldobj, types.NoneType) and not _is_type_match(v, oldobj):
				#新旧对象类型不同，保留旧对象
				new_module.__dict__[k] = oldobj
				log.error(
						'TYPE NOT MATCH',
						'module', module_name,
						'name', k,
						'type_old', type(oldobj),
						'type_new', type(v))
				continue

			func = _get_handler(v)
			if func:
				#把新的object内容更新到旧的object中
				func(oldobj, v)
				new_module.__dict__[k] = oldobj
			else:
				if not k.isupper():
					#不是常量，直接用旧对象, 避免运行时数据被清除
					new_module.__dict__[k] = oldobj
					log.trace('UPDATE SKIPPED, module=%s, name=%s, type=%s' % (
								module_name, k, str(type(v))))
				else:
					log.trace('UPDATE MODULE MEMBER, module=%s, name=%s, type=%s' % (
								module_name, k, str(type(v))))
		except:
			log.trace('UPDATE FAILED, module=%s, name=%s, type=%s' % (
					module_name, k, str(type(v))))

	_call_module_func(old_module, '__after_update__')

	return new_module
