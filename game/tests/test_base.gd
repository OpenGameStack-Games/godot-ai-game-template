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

## Optional hook invoked before each `test_*` method in the suite.
func before_each() -> void:
	pass

## Optional hook invoked after each `test_*` method in the suite.
func after_each() -> void:
	pass

## Optional hook invoked once after all `test_*` methods in the suite finish.
func cleanup() -> void:
	pass

func _record_failure(detail: String, message: String = "") -> void:
	failed_count += 1
	var err: String = "  [FAIL] %s: %s" % [current_test_name, detail]
	if message != "":
		err += " - " + message
	printerr(err)

func assert_true(condition: bool, message: String = "") -> void:
	if condition:
		passed_count += 1
	else:
		_record_failure("Expected true, got false", message)

func assert_false(condition: bool, message: String = "") -> void:
	if not condition:
		passed_count += 1
	else:
		_record_failure("Expected false, got true", message)

func assert_eq(actual: Variant, expected: Variant, message: String = "") -> void:
	if actual == expected:
		passed_count += 1
	else:
		_record_failure("Expected '%s', but got '%s'" % [str(expected), str(actual)], message)

func assert_ne(actual: Variant, expected: Variant, message: String = "") -> void:
	if actual != expected:
		passed_count += 1
	else:
		_record_failure("Expected value not to equal '%s'" % [str(expected)], message)

func assert_gt(actual: float, expected: float, message: String = "") -> void:
	if actual > expected:
		passed_count += 1
	else:
		_record_failure("Expected %s > %s" % [str(actual), str(expected)], message)

func assert_gte(actual: float, expected: float, message: String = "") -> void:
	if actual >= expected:
		passed_count += 1
	else:
		_record_failure("Expected %s >= %s" % [str(actual), str(expected)], message)

func assert_lt(actual: float, expected: float, message: String = "") -> void:
	if actual < expected:
		passed_count += 1
	else:
		_record_failure("Expected %s < %s" % [str(actual), str(expected)], message)

func assert_lte(actual: float, expected: float, message: String = "") -> void:
	if actual <= expected:
		passed_count += 1
	else:
		_record_failure("Expected %s <= %s" % [str(actual), str(expected)], message)

func assert_approx(actual: float, expected: float, tolerance: float = 0.0001, message: String = "") -> void:
	if absf(actual - expected) <= tolerance:
		passed_count += 1
	else:
		_record_failure("Expected %s to be within %s of %s" % [str(actual), str(tolerance), str(expected)], message)

func assert_null(val: Variant, message: String = "") -> void:
	if val == null:
		passed_count += 1
	else:
		_record_failure("Expected null, but got '%s'" % [str(val)], message)

func assert_not_null(val: Variant, message: String = "") -> void:
	if val != null:
		passed_count += 1
	else:
		_record_failure("Expected not null, but got null", message)

func assert_contains(haystack: Variant, needle: Variant, message: String = "") -> void:
	var found: bool = false
	if haystack is String and needle is String:
		found = (haystack as String).contains(needle as String)
	elif haystack is Array:
		found = (haystack as Array).has(needle)
	elif haystack is Dictionary:
		found = (haystack as Dictionary).has(needle)
	if found:
		passed_count += 1
	else:
		_record_failure("Expected '%s' to contain '%s'" % [str(haystack), str(needle)], message)

func assert_file_exists(path: String, message: String = "") -> void:
	if FileAccess.file_exists(path):
		passed_count += 1
	else:
		_record_failure("Expected file to exist at '%s'" % [path], message)
