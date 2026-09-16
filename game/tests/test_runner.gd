extends SceneTree

func _init() -> void:
	print("Starting automated test suite...")
	var total_passed = 0
	var total_failed = 0
	
	var dir = DirAccess.open("res://tests")
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		while file_name != "":
			if file_name.begins_with("test_") and file_name.ends_with(".gd") and file_name != "test_runner.gd" and file_name != "test_base.gd":
				print("Running suite: ", file_name)
				var script = load("res://tests/" + file_name)
				if script:
					var instance = script.new()
					for method in instance.get_method_list():
						if method["name"].begins_with("test_"):
							instance.call(method["name"])
					total_passed += instance.passed
					total_failed += instance.failed
			file_name = dir.get_next()
	
	print("Test Results: %d Passed, %d Failed" % [total_passed, total_failed])
	
	if total_failed > 0:
		quit(1)
	else:
		quit(0)
