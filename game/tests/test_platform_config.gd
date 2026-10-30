extends "res://tests/test_base.gd"

func test_android_and_web_export_presets() -> void:
	var file: FileAccess = FileAccess.open("res://export_presets.cfg", FileAccess.READ)
	assert_not_null(file, "export_presets.cfg should exist.")
	if file == null:
		return

	var content: String = file.get_as_text()

	assert_contains(content, "screen/immersive_mode=false", "Immersive mode should be disabled (false) to avoid safe area cutoffs.")
	assert_true("include_filter=" in content and "*.json" in content, "include_filter should contain '*.json'.")
	assert_contains(content, "name=\"Web\"", "Web export preset should exist.")
	assert_contains(content, "platform=\"Web\"", "Web export preset platform should be Web.")
	assert_file_exists("res://assets/icons/icon.png", "icon.png should exist.")
	assert_file_exists("res://assets/icons/icon_foreground.png", "icon_foreground.png should exist.")
	assert_file_exists("res://assets/icons/icon_background.png", "icon_background.png should exist.")

	var cfg: ConfigFile = ConfigFile.new()
	var err: int = cfg.load("res://export_presets.cfg")
	assert_eq(err, OK, "export_presets.cfg should load cleanly as a ConfigFile.")
	if err == OK:
		var android_filter: String = str(cfg.get_value("preset.0", "include_filter", ""))
		var web_filter: String = str(cfg.get_value("preset.1", "include_filter", ""))
		assert_contains(android_filter, "*.ttf", "Android preset include_filter must include '*.ttf'.")
		assert_contains(web_filter, "*.ttf", "Web preset include_filter must include '*.ttf'.")

		var export_version: String = str(cfg.get_value("preset.0.options", "version/name", ""))
		var project_version: String = str(ProjectSettings.get_setting("application/config/version", ""))
		assert_eq(project_version, export_version, "project.godot config/version must match export_presets.cfg version/name.")

func test_project_settings() -> void:
	var file: FileAccess = FileAccess.open("res://project.godot", FileAccess.READ)
	assert_not_null(file, "project.godot should exist.")
	if file == null:
		return

	var content: String = file.get_as_text()
	assert_contains(content, "window/handheld/orientation=1", "Portrait orientation should be set.")
	assert_contains(content, "window/stretch/mode=\"canvas_items\"", "Stretch mode should be canvas_items.")
	assert_contains(content, "window/stretch/aspect=\"expand\"", "Stretch aspect should be expand.")
	assert_contains(content, "emulate_touch_from_mouse=true", "Emulate touch from mouse should be enabled.")
	assert_contains(content, "renderer/rendering_method=\"gl_compatibility\"", "Renderer should be set to gl_compatibility.")
	assert_contains(content, "renderer/rendering_method.mobile=\"gl_compatibility\"", "Mobile renderer should be set to gl_compatibility.")
	assert_contains(content, "McpInteractionServer=\"*res://autoloads/mcp_interaction_server.gd\"", "McpInteractionServer should point to res://autoloads/mcp_interaction_server.gd.")
	assert_file_exists("res://autoloads/mcp_interaction_server.gd", "mcp_interaction_server.gd should exist in res://autoloads/.")
	assert_file_exists("res://AGENTS.md", "game/AGENTS.md directory rules file should exist.")

func test_symbol_fallback_fonts() -> void:
	var symbols_path: String = "res://assets/fonts/NotoSansSymbols-Regular.ttf"
	var dejavu_path: String = "res://assets/fonts/DejaVuSans.ttf"
	assert_file_exists(symbols_path, "NotoSansSymbols-Regular.ttf must exist in res://assets/fonts/.")
	assert_file_exists(dejavu_path, "DejaVuSans.ttf must exist in res://assets/fonts/.")

	var symbols_font: FontFile = load(symbols_path) as FontFile
	var dejavu_font: FontFile = load(dejavu_path) as FontFile
	assert_not_null(symbols_font, "NotoSansSymbols-Regular.ttf must load as a valid FontFile.")
	assert_not_null(dejavu_font, "DejaVuSans.ttf must load as a valid FontFile.")

	var custom_font_path: String = str(ProjectSettings.get_setting("gui/theme/custom_font", ""))
	var custom_theme_path: String = str(ProjectSettings.get_setting("gui/theme/custom", ""))
	assert_true(custom_font_path != "" or custom_theme_path != "", "Either gui/theme/custom_font or gui/theme/custom must be configured.")

	var fonts_to_verify: Array[Font] = []
	if custom_font_path != "":
		assert_file_exists(custom_font_path, "Configured gui/theme/custom_font file must exist.")
		var custom_font: Font = load(custom_font_path) as Font
		assert_not_null(custom_font, "gui/theme/custom_font must load as a valid Font.")
		assert_false(custom_font is SystemFont, "Global custom_font must not be a SystemFont (use FontVariation or FontFile with fallbacks).")
		if custom_font != null:
			fonts_to_verify.append(custom_font)

	if custom_theme_path != "":
		assert_file_exists(custom_theme_path, "Configured gui/theme/custom theme file must exist.")
		var custom_theme: Theme = load(custom_theme_path) as Theme
		assert_not_null(custom_theme, "gui/theme/custom must load as a valid Theme.")
		if custom_theme != null and custom_theme.default_font != null:
			assert_false(custom_theme.default_font is SystemFont, "Theme default_font must not be a SystemFont.")
			fonts_to_verify.append(custom_theme.default_font)

	assert_gt(float(fonts_to_verify.size()), 0.0, "At least one global default font must be active to verify symbol fallbacks.")
	var required_symbols: Array[String] = ["☰", "✕", "▸", "▾", "★", "↺", "↻", "⌫", "▶", "→"]
	for active_font in fonts_to_verify:
		assert_gt(float(active_font.fallbacks.size()), 0.0, "Active default font must have symbol fallback fonts attached for Web/HTML5 builds.")
		for sym in required_symbols:
			assert_true(active_font.has_char(ord(sym)), "Active font must support UI symbol '%s' (U+%04X) via bundled fallbacks." % [sym, ord(sym)])
