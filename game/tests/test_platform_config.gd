extends "res://tests/test_base.gd"

func test_android_and_web_export_presets() -> void:
	var file := FileAccess.open("res://export_presets.cfg", FileAccess.READ)
	assert_true(file != null, "export_presets.cfg should exist.")
	if file == null:
		return
	
	var content := file.get_as_text()
	
	assert_true("screen/immersive_mode=false" in content, "Immersive mode should be disabled (false) to avoid safe area cutoffs.")
	assert_true("include_filter=" in content and "*.json" in content, "include_filter should contain '*.json'.")
	assert_true("name=\"Web\"" in content, "Web export preset should exist.")
	assert_true("platform=\"Web\"" in content, "Web export preset platform should be Web.")
	assert_true(FileAccess.file_exists("res://assets/icons/icon.png"), "icon.png should exist.")
	assert_true(FileAccess.file_exists("res://assets/icons/icon_foreground.png"), "icon_foreground.png should exist.")
	assert_true(FileAccess.file_exists("res://assets/icons/icon_background.png"), "icon_background.png should exist.")

func test_project_settings() -> void:
	var file := FileAccess.open("res://project.godot", FileAccess.READ)
	assert_true(file != null, "project.godot should exist.")
	if file == null:
		return
	
	var content := file.get_as_text()
	assert_true("window/handheld/orientation=1" in content, "Portrait orientation should be set.")
	assert_true("window/stretch/mode=\"canvas_items\"" in content, "Stretch mode should be canvas_items.")
	assert_true("window/stretch/aspect=\"expand\"" in content, "Stretch aspect should be expand.")
	assert_true("emulate_touch_from_mouse=true" in content, "Emulate touch from mouse should be enabled.")
	assert_true("renderer/rendering_method=\"gl_compatibility\"" in content, "Renderer should be set to gl_compatibility.")
	assert_true("renderer/rendering_method.mobile=\"gl_compatibility\"" in content, "Mobile renderer should be set to gl_compatibility.")
	assert_true("McpInteractionServer=\"*res://autoloads/mcp_interaction_server.gd\"" in content, "McpInteractionServer should point to res://autoloads/mcp_interaction_server.gd.")
	assert_true(FileAccess.file_exists("res://autoloads/mcp_interaction_server.gd"), "mcp_interaction_server.gd should exist in res://autoloads/.")
