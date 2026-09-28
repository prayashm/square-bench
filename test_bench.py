from bench import parse

assert parse("It's a square.\n\nAnswer: g") == "g"
assert parse("Answer: a\nwait, Answer: **g**") == "g"
assert parse("(d)") == "d"
assert parse("a square, clearly") is None
print("ok")
