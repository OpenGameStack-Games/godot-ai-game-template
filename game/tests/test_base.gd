# tests/test_base.gd
class_name TestBase
extends RefCounted

## Base class for automated unit tests in the template.

var passed_count: int = 0
var failed_count: int = 0
var current_test_name: String = ""
var test_root_window: Window = null

# Backwards compatibility properties
var passed: int:
	get:
		return passed_count
	set(val):
		passed_count = val

var failed: int:
	get:
		return failed_count
	set(val):
		failed_count = val

func cleanup() -> void:
	pass

func assert_true(condition: bool, message: String = "") -> void:
	if condition:
		passed_count += 1
	else:
		failed_count += 1
		var err: String = "  [FAIL] %s: Expected true, got false" % [current_test_name]
		if message != "":
			err += " - " + message
		printerr(err)

func assert_false(condition: bool, message: String = "") -> void:
	assert_true(!condition, message)

func assert_eq(actual: Variant, expected: Variant, message: String = "") -> void:
	if actual == expected:
		passed_count += 1
	else:
		failed_count += 1
		var err: String = "  [FAIL] %s: Expected '%s', but got '%s'" % [current_test_name, str(expected), str(actual)]
		if message != "":
			err += " - " + message
		printerr(err)

func assert_ne(actual: Variant, expected: Variant, message: String = "") -> void:
	if actual != expected:
		passed_count += 1
	else:
		failed_count += 1
		var err: String = "  [FAIL] %s: Expected value not to equal '%s'" % [current_test_name, str(expected)]
		if message != "":
			err += " - " + message
		printerr(err)

func assert_null(val: Variant, message: String = "") -> void:
	if val == null:
		passed_count += 1
	else:
		failed_count += 1
		var err: String = "  [FAIL] %s: Expected null, but got '%s'" % [current_test_name, str(val)]
		if message != "":
			err += " - " + message
		printerr(err)

func assert_not_null(val: Variant, message: String = "") -> void:
	if val != null:
		passed_count += 1
	else:
		failed_count += 1
		var err: String = "  [FAIL] %s: Expected not null, but got null" % [current_test_name]
		if message != "":
			err += " - " + message
		printerr(err)
