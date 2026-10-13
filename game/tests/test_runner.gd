# tests/test_runner.gd
extends SceneTree

## Headless test runner for automated testing.

const TestBaseScript = preload("res://tests/test_base.gd")

func _init() -> void:
	print("==================================================")
	print("Running Automated Tests...")
	print("==================================================")
	
	var total_passed: int = 0
	var total_failed: int = 0
	var test_files: Array[String] = _discover_tests("res://tests")
	
	for file_path in test_files:
		var script: GDScript = load(file_path) as GDScript
		if script == null:
			continue
		
		var test_instance: Object = script.new()
		if not (test_instance is TestBaseScript):
			continue

		var test_obj: Variant = test_instance
		test_obj.test_root_window = root
		var script_name: String = file_path.get_file()
		print("\nSuite: %s" % script_name)
		
		var method_list: Array[Dictionary] = script.get_script_method_list()
		for method_info in method_list:
			var method_name: String = method_info.name
			if method_name.begins_with("test_"):
				test_obj.current_test_name = method_name
				test_obj.call(method_name)
				print("  [OK] %s" % method_name)
		
		total_passed += int(test_obj.passed_count)
		total_failed += int(test_obj.failed_count)
		test_obj.cleanup()
	
	print("\n==================================================")
	print("Test Results: %d Passed, %d Failed" % [total_passed, total_failed])
	print("==================================================")
	
	if total_failed > 0:
		quit(1)
	else:
		quit(0)

func _discover_tests(dir_path: String) -> Array[String]:
	var results: Array[String] = []
	var dir: DirAccess = DirAccess.open(dir_path)
	if dir != null:
		dir.list_dir_begin()
		var file_name: String = dir.get_next()
		while file_name != "":
			if not dir.current_is_dir():
				if file_name.begins_with("test_") and file_name.ends_with(".gd") and file_name != "test_runner.gd" and file_name != "test_base.gd":
					results.append(dir_path.path_join(file_name))
			file_name = dir.get_next()
	return results
