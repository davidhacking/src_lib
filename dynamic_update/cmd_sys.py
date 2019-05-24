# *- coding: utf-8 -*-
# Owner: gzcaichuanduo@corp.netease.com (Cai Chuanduo)
# $Id: cmd_sys.py 109796 2019-02-28 09:55:21Z gzlindi@CORP.NETEASE.COM $

import os
import sys

import render
import game3d

DETECT_UPDATE_DIRS = (
	'/data',
	'/script'
)

g_module_modify_time = {}

def reload_module(module_name):
	""" 更新模块 """
	from utils import update
	from common import module_cache

	for full_module_name in sys.modules.keys():
		if full_module_name.endswith(module_name):
			update.update(full_module_name)
			module_cache.update(full_module_name)
			print "更新%s成功" % full_module_name

	return "更新完毕"


HOTFIX_PATH = "hotfix/hotfix.py"

def hotfix(path=""):
	from share import share_func
	from common import hotfix_mgr
	from common.message import message

	path = path or HOTFIX_PATH
	hotfix = share_func.read_hotfix(path)
	message.show_custom_message("Hotfix begin.")
	hotfix_mgr.receive_hotfix(hotfix)
	message.show_custom_message("Hotfix ended.")

	# hotfix_mgr.g_staticdata = set()
	# hotfix_mgr.g_function = set()
	# hotfix_mgr.g_module = {}
	# for root, dirs, files in os.walk("hotfix/"):
	# 	for name in files:
	# 		path = "hotfix/%s" % name
	# 		hotfix = share_func.read_hotfix(path)
	# 		hotfix_mgr.receive_hotfix(hotfix)

	# print hotfix_mgr.g_staticdata
	# print hotfix_mgr.g_function
	# print hotfix_mgr.g_module

def network_debug(enable_debug):
	""" 开关网络日志 """
	import network
	network.enable_network_debug(enable_debug)
	return "网络日志开关 enable=%d" % enable_debug

def detect_update():
	""" 更新修改的数据py """
	from utils import update
	work_dir = os.getcwdu()
	m_list = []
	for part_path in DETECT_UPDATE_DIRS:
		full_path = u"%s%s" % (work_dir, part_path)
		_update_module_list(full_path, m_list)
	for module_name in m_list:
		print "更新：%s" % module_name
		update.update(module_name)
	return '更新成功'

def _update_module_list(full_path, m_list):
	from debug import wizard
	for dir_path, _, filenames in os.walk(full_path, True):
		for filename in filenames:
			if not filename.endswith(".py"):
				continue
			filepath = os.path.join(dir_path, filename)
			m_time = os.stat(filepath).st_mtime
			if filepath not in g_module_modify_time:
				g_module_modify_time[filepath] = m_time
				if m_time > wizard.g_last_module_time:
					m_list.append(_path2modulename(full_path, filepath))
			elif m_time > g_module_modify_time[filepath]:
				g_module_modify_time[filepath] = m_time
				m_list.append(_path2modulename(full_path, filepath))

def _path2modulename(syspath, filepath):
	module_path = filepath[len(syspath) + 1: -3]
	return module_path.replace('/', '.').replace('\\', '.').encode("utf-8")

def profile(enable_chart):
	""" 显示性能图表 """
	if enable_chart:
		render.activate_perf_graph(True)
		render.activate_chart(render.CT_SPRITE, True)
		render.activate_chart(render.CT_VRAM, True)
		game3d.show_render_info(True)
		return "显示图表"
	else:
		render.activate_perf_graph(False)
		render.activate_chart(render.CT_SPRITE, False)
		render.activate_chart(render.CT_VRAM, False)
		game3d.show_render_info(False)
		return "关闭图表"

def script_hotshot():
	""" 开始脚本profile """
	from common import xprofile
	xprofile.script_hotshot()

def script_cprofile(fcnt):
	""" 开始脚本profile """
	from common import xprofile
	xprofile.script_cprofile(fcnt)

def send_protocol(proto_name_args):
	import client2game

	elems = proto_name_args.split(".")
	proto_name = elems[0]
	args = elems[1:]
	for i in xrange(len(args)):
		try:
			args[i] = int(args[i])
		except:
			continue
	getattr(client2game, proto_name)(*args)

def memory_analyse():
	import gc
	print "------------module memory---------------"
	total_m = 0

	modules = sys.modules.values()
	modules.sort(cmp=lambda x, y: cmp(str(x), str(y)))
	for module in modules:
		if str(module).find(".py") <= 0:
			continue
		keys = dir(module)
		total = 0
		for k in keys:
			v = getattr(module, k, None)
			if v is None:
				continue
			total += sys.getsizeof(v)
		total_m += total
		print "memory_analyse", module, total
	print "------------module memory end---------------", total_m
	all_objs = gc.get_objects()
	cls2sizes = {}
	total_c = 0
	for obj in all_objs:
		cls = str(type(obj))
		if cls not in cls2sizes:
			cls2sizes[cls] = [0, 0]
		cls2sizes[cls][0] += 1
		cls2sizes[cls][1] += sys.getsizeof(obj)
		total_c += sys.getsizeof(obj)
	MIN_SIZE = 1024
	print "------------class memory---------------"

	clss = cls2sizes.keys()
	clss.sort(cmp=lambda x, y: cmp(str(x), str(y)))
	for cls in clss:
		sizes = cls2sizes[cls]
		if sizes[1] > MIN_SIZE:
			print "memory_analyse", cls, sizes[0], sizes[1]
	print "------------class memory end ---------------", total_c

def memory_display():
	import profiling
	print "当前内存: ", profiling.get_process_mem_used() / 1024 / 1024

def show_log():
	from const import const
	from common.message import message
	const.IN_DEBUG = not const.IN_DEBUG
	message.show_custom_message("当前打印log状态为%d " % const.IN_DEBUG)


g_gtrace_tag = 0
g_gtrace_timer = None

def toggle_gtrace(max_timespan_sec=None):
	"""
	http://km.netease.com/#/article/194301
	max_timespan_sec = None means only to stop
	"""
	import gtrace
	from common import xfile
	from common import low_power_mode
	from utils import timer

	global g_gtrace_tag
	global g_gtrace_timer

	if max_timespan_sec is None and g_gtrace_tag % 2 == 0:
		return
	g_gtrace_tag += 1
	if g_gtrace_tag % 2 == 1:
		interval_ms = 10
		gtrace.start(interval_ms, max_timespan_sec)
		g_gtrace_timer = timer.once(max_timespan_sec * 0.95, toggle_gtrace)
		low_power_mode.push_delta_sec_stack(999999)
	else:
		path = xfile.get_full_path("prof%03d.gt" % g_gtrace_tag)
		gtrace.stop(path)
		g_gtrace_timer = None
		low_power_mode.pop_delta_sec_stack()

def show_ui_info():
	from common.message import message
	from ui import ui_mgr
	print "================================================="
	print "【UI_CANVAS】"
	init_canvas = ui_mgr.g_canvas.keys()
	init_canvas.sort()
	print "  init canvas[%s]: %s" % (len(init_canvas), init_canvas)
	show_canvas = ui_mgr.g_canvas_show
	print "  show canvas[%s]: %s" % (len(show_canvas), show_canvas)
	print "【UI_WIDGET】"
	show_canvas_list = []
	for canvas in show_canvas:
		canvas_id = canvas.get_id()
		show_canvas_list.append(canvas_id)
		panels = canvas._panels.keys()
		panels.sort()
		print "  canvas %s[is_dynamic = %s]:" % (canvas_id, len(canvas._panels_stable) > 0)
		print "    widget[%s]: %s" % (len(panels), panels)
	print "================================================="

	message.show_custom_message("Canvas: %s" % show_canvas_list)

g_postprocess = True
def toggle_postprocess():
	import render
	from common.message import message

	global g_postprocess

	if g_postprocess:
		message.show_custom_message("后处理已关闭")
		render.enable_postprocess(False)
	else:
		message.show_custom_message("后处理已开启")
		render.enable_postprocess(True)

	g_postprocess = not g_postprocess

g_enable_hdr = False
def toggle_hdr():
	import render
	from common.message import message

	global g_enable_hdr
	if g_enable_hdr:
		message.show_custom_message("HDR已关闭")
	else:
		message.show_custom_message("HDR已开启")

	g_enable_hdr = not g_enable_hdr
	render.set_post_process_active("hdr_old", g_enable_hdr, 0)
	render.set_post_process_active("hdr_old", g_enable_hdr, 1)

def toggle_pcf():
	from xgame.scene import combat_scene
	from common.message import message

	if combat_scene.ENABLE_PCF:
		message.show_custom_message("PCF已关闭, 请重新进入场景")
	else:
		message.show_custom_message("PCF已开启, 请重新进入场景")

	combat_scene.ENABLE_PCF = not combat_scene.ENABLE_PCF

def on_back():
	from ui import ui_mgr
	ui_mgr.on_back(None, None)

def print_device_model():
	from common import platform
	import profiling
	from common.message import message
	device_model = platform.get_device_model()
	video_card = profiling.get_video_card_name()
	message.show_custom_message("device_model:%s, video_card:%s" % (device_model, video_card))

def memory_warning():
	import game
	import game_init
	game_init.skip_update_time = True
	game.on_memory_warning()
