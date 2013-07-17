import JSLON, codecs, time

def comp(k, x, y):
	if type(x) == type(y) and x == y:
		print "Test %s passed." % k
	else:
		print "Test %s FAILED. Expected (%s)/received (%s):\n%s\n%s" % (
			k, type(x).__name__, type(y).__name__, x, y
		)
	#endif
#enddef

def main():
	f = codecs.open("../test.jslon", encoding="utf-8", mode="r")
	data = f.read()
	f.close()
	now = time.time()
	root = JSLON.parse(data)
	print "Parse time: %.3f s" % (time.time() - now)
	print "====== parse ======"
	for x in root:
		if   x == "literal": comp(x, u"literal", root[x])
		elif x == "double": comp(x, u"double", root[x])
		elif x == "single": comp(x, u"single", root[x])
		elif x == "line continueheeee": comp(x, u"line continueheeee", root[x])
		elif x == "inline hex": comp(x, u"inline hex", root[x])
		elif x == "str1": comp(x, u"double quotes", root[x])
		elif x == "str2": comp(x, u"single quotes", root[x])
		elif x == "str3": comp(x, u"linecontinue", root[x])
		elif x == "str4": comp(x, u"escapes\x01\x02\x40 \x200", root[x])
		elif x == "num1": comp(x, 123, root[x])
		elif x == "num2": comp(x, 1.1, root[x])
		elif x == "num3": comp(x, 0, root[x])
		elif x == "num4": comp(x, 0.1, root[x])
		elif x == "num5": comp(x, 1, root[x])
		elif x == "num6": comp(x, 1e10, root[x])
		elif x == "num7": comp(x, 1e-5, root[x])
		elif x == "num8": comp(x, -15, root[x])
		elif x == "hex1": comp(x, 1, root[x])
		elif x == "hex2": comp(x, 10, root[x])
		elif x == "oct1": comp(x, 7, root[x])
		elif x == "oct2": comp(x, 8, root[x])
		elif x == "oct3": comp(x, 40, root[x])
		elif x == "regex": comp(x, u"123/a\\n%%?", root[x].pattern)
		elif x == "arr1":
			comp(x + "[0]", u"hi", root[x][0])
			comp(x + "[1]", 1, root[x][1])
			comp(x + "[2]", 2, root[x][2])
			comp(x + "[3]", 3, root[x][3])
			comp(x + "[4]", u"regex", root[x][4].pattern)
			comp(x + "[5].hi", u"hi", root[x][5]["hi"])
			comp(x + "[6][0]", 1, root[x][6][0])
			comp(x + "[6][1]", 2, root[x][6][1])
			comp(x + "[7]", 5, root[x][7])
		elif x == "arr2":
			comp(x + "[0]", 1, root[x][0])
			comp(x + "[1]", 2, root[x][1])
			comp(x + "[2]", u"c", root[x][2])
			comp(x + "[3]", 4, root[x][3])
		elif x == "obj": comp(x + ".abc", u"def", root[x]["abc"])
		elif x == "Infinity":
			comp(x, float, type(root[x]))
			comp(x, "inf", str(root[x]))
		elif x == "NaN":
			comp(x, float, type(root[x]))
			comp(x, "nan", str(root[x]))
		elif x == "true":      comp(x, True, root[x])
		elif x == "false":     comp(x, False, root[x])
		elif x == "null":      comp(x, None, root[x])
		elif x == "undefined": comp(x, JSLON.undefined(), root[x])
		elif x == "dup": comp(x, 2, root[x])
	#endfor

	print "\n====== stringify ======"
	comp("Number", u"687123", JSLON.stringify(687123))
	comp("Floating point number", u"10.4", JSLON.stringify(10.4))
	comp("String", u'"abc"', JSLON.stringify("abc"))
	comp("String with escapes", u'"abc\\nd\\u0005"', JSLON.stringify("abc\nd\x05"))
	comp("Array of numbers", u"[1,2,3,4]", JSLON.stringify([1, 2, 3, 4]))
	comp("Array of arrays", u"[1,[2,[3]],4,[5,[[6,7],8]]]", JSLON.stringify([1, [2, [3]], 4, [5, [[6, 7], 8]]]))
	comp("Object of strings", u'{"a":"b","c":"d"}', JSLON.stringify({"a": 'b', "c": 'd'}))

	print "\n====== stringify with options ======"
	comp("Octal number", u"01", JSLON.stringify(1, {"numBase": 8}))
	comp("Hexadecimal number", u"0x1", JSLON.stringify(1, {"numBase": 16}))
	comp("Single quoted string", u"'abc'", JSLON.stringify("abc", {"quotes": "'"}))
	comp("String (strEscapes: cOu)", u'"abc\\nd\\005a\\u0999"',
		JSLON.stringify(u"abc\nd\x05a\u0999", {"strEscapes": "cOu"})
	)
	comp("String (strEscapes: ou)", u'"abc\\12d\\5a\\u0999"',
		JSLON.stringify(u"abc\nd\x05a\u0999", {"strEscapes": "ou"})
	)
	comp("String (strEscapes: x)", u'"abc\\x0ad\\x05a"',
		JSLON.stringify(u"abc\nd\x05a\u0999", {"strEscapes": "x"})
	)
	comp("Prettyprinted object (keyOwnLine|openOwnLine|endOwnLine, specific)",
		u'{\n\t"a":\n\t\t[\n\t\t\t0x1,2,{\n\t\t\t\t"b":\n\t\t\t\t\t"abc"\n\t\t\t},\n\t\t\t3\n\t\t]\n}',
		JSLON.stringify({"a": [1, 2, {"b": "abc"}, 3]},{
			"keyOwnLine": True,
			"openOwnLine": True,
			"endOwnLine": True,
			"specific": {"a": {"specific": [{"numBase": 16}]}},
		})
	)
	comp("Prettyprinted object (spaceAfterKey)", u'{"a": "b"}',
		JSLON.stringify({"a":"b"}, {"spaceAfterKey": True})
	)
	comp("Prettyprinted array (entriesPerLine, depth)", u'[1,2,\n 3,4,\n 5]',
		JSLON.stringify([1, 2, 3, 4, 5], {"entriesPerLine": 2, "depth": " "})
	)
#enddef

if __name__ == "__main__": main()
