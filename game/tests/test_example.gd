extends TestBase

var _hook_counter: int = 0

func before_each() -> void:
	_hook_counter += 1

func after_each() -> void:
	assert_gt(float(_hook_counter), 0.0, "before_each should run before each test method.")

func test_example() -> void:
	assert_true(true, "Example test passed.")
	assert_false(false, "assert_false should pass on false.")
	assert_eq(2 + 2, 4, "Basic equality check.")
	assert_ne("a", "b", "Basic inequality check.")
	assert_gt(5.0, 3.0, "5.0 > 3.0")
	assert_gte(5.0, 5.0, "5.0 >= 5.0")
	assert_lt(2.0, 4.0, "2.0 < 4.0")
	assert_lte(4.0, 4.0, "4.0 <= 4.0")
	assert_approx(0.1 + 0.2, 0.3, 0.0001, "Floating point approximate equality.")
	assert_contains("OpenGameStack", "Game", "String contains check.")
	assert_contains([1, 2, 3], 2, "Array contains check.")
	assert_contains({"key": "value"}, "key", "Dictionary key contains check.")
