extends RefCounted
class_name TestBase

var passed: int = 0
var failed: int = 0

func assert_true(condition: bool, message: String = "") -> void:
	if condition:
		passed += 1
	else:
		failed += 1
		printerr("Assertion failed: " + message)

func assert_false(condition: bool, message: String = "") -> void:
	assert_true(not condition, message)

func assert_eq(a, b, message: String = "") -> void:
	if a == b:
		passed += 1
	else:
		failed += 1
		printerr("Assertion failed: expected %s, got %s. %s" % [str(a), str(b), message])

func assert_ne(a, b, message: String = "") -> void:
	if a != b:
		passed += 1
	else:
		failed += 1
		printerr("Assertion failed: expected not %s, got %s. %s" % [str(a), str(b), message])
