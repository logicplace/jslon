var JSLON = require("./jslon.js")
, fs = require("fs");

function comp(k, x, y){
	if(x === y) console.log("Test " + k + " passed.");
	else{
		console.log("Test " + k + " FAILED. Expected/received:");
		console.log(x);
		console.log(y);
	}
}

fs.readFile("../test.jslon", "utf8", function(err, data) {
	var time = Date.now()
	, root = JSLON.parse(data);
	console.log("Parse time: " + (Date.now() - time) + " ms");
	console.log("====== parse ======");
	for(var x in root) {
		switch(x) {
			case "literal": comp(x, "literal", root[x]); break;
			case "double": comp(x, "double", root[x]); break;
			case "single": comp(x, "single", root[x]); break;
			case "line continueheeee": comp(x, "line continueheeee", root[x]); break;
			case "inline hex": comp(x, "inline hex", root[x]); break;
			case "str1": comp(x, "double quotes", root[x]); break;
			case "str2": comp(x, "single quotes", root[x]); break;
			case "str3": comp(x, "linecontinue", root[x]); break;
			case "str4": comp(x, "escapes\1\2\x40 \400", root[x]); break;
			case "num1": comp(x, 123, root[x]); break;
			case "num2": comp(x, 1.1, root[x]); break;
			case "num3": comp(x, 0, root[x]); break;
			case "num4": comp(x, 0.1, root[x]); break;
			case "num5": comp(x, 1, root[x]); break;
			case "num6": comp(x, 1e10, root[x]); break;
			case "num7": comp(x, 1e-5, root[x]); break;
			case "num8": comp(x, -15, root[x]); break;
			case "hex1": comp(x, 1, root[x]); break;
			case "hex2": comp(x, 10, root[x]); break;
			case "oct1": comp(x, 7, root[x]); break;
			case "oct2": comp(x, 8, root[x]); break;
			case "oct3": comp(x, 40, root[x]); break;
			case "regex": comp(x, "/123/a\\n%%?/", root[x].toString()); break;
			case "arr1":
				comp(x + "[0]", "hi", root[x][0]);
				comp(x + "[1]", 1, root[x][1]);
				comp(x + "[2]", 2, root[x][2]);
				comp(x + "[3]", 3, root[x][3]);
				comp(x + "[4]", "/regex/", root[x][4].toString());
				comp(x + "[5].hi", "hi", root[x][5].hi);
				comp(x + "[6][0]", 1, root[x][6][0]);
				comp(x + "[6][1]", 2, root[x][6][1]);
				comp(x + "[7]", 5, root[x][7]);
				break;
			case "arr2":
				comp(x + "[0]", 1, root[x][0]);
				comp(x + "[1]", 2, root[x][1]);
				comp(x + "[2]", "c", root[x][2]);
				comp(x + "[3]", 4, root[x][3]);
				break;
			case "obj": comp(x + ".abc", "def", root[x].abc); break;
			//NOTE that these statics are not strictly equivalent with the same
			//ones from other modules.
			case "Infinity":  comp(x, String(Infinity), String(root[x])); break;
			case "NaN":       comp(x, String(NaN), String(root[x])); break;
			case "true":      comp(x, String(true), String(root[x])); break;
			case "false":     comp(x, String(false), String(root[x])); break;
			case "null":      comp(x, String(null), String(root[x])); break;
			case "undefined": comp(x, String(undefined), String(root[x])); break;
			case "dup": comp(x, 2, root[x]); break;
		}
	}

	// Other parse tests
	try {
		var doubleBlocks = JSLON.parse('/* Comment */ "Not comment */"');
		comp("DoubleBlocks", "Not comment */", doubleBlocks);
	} catch (e) {
		comp("DoubleBlocks", 'String "Not comment */"', "Error: " + e.message);
	}

	console.log("\n====== stringify ======");
	comp("Number", "687123", JSLON.stringify(687123));
	comp("Floating point number", "10.4", JSLON.stringify(10.4));
	comp("String", '"abc"', JSLON.stringify("abc"));
	comp("String with escapes", '"abc\\nd\\u0005"', JSLON.stringify("abc\nd\05"));
	comp("Array of numbers", "[1,2,3,4]", JSLON.stringify([1, 2, 3, 4]));
	comp("Array of arrays", "[1,[2,[3]],4,[5,[[6,7],8]]]", JSLON.stringify([1, [2, [3]], 4, [5, [[6, 7], 8]]]));
	comp("Object of strings", '{"a":"b","c":"d"}', JSLON.stringify({a: 'b', c: 'd'}));
	console.log("\n====== stringify with options ======");
	comp("Octal number", "01", JSLON.stringify(1, {numBase: 8}));
	comp("Hexadecimal number", "0x1", JSLON.stringify(1, {numBase: 16}));
	comp("Single quoted string", "'abc'", JSLON.stringify("abc", {quotes: "'"}));
	comp("String (strEscapes: cOu)", '"abc\\nd\\005a\\u0999"',
		JSLON.stringify("abc\nd\05a\u0999", {strEscapes: "cOu"})
	);
	comp("String (strEscapes: ou)", '"abc\\12d\\5a\\u0999"',
		JSLON.stringify("abc\nd\05a\u0999", {strEscapes: "ou"})
	);
	comp("String (strEscapes: x)", '"abc\\x0ad\\x05a"',
		JSLON.stringify("abc\nd\05a\u0999", {strEscapes: "x"})
	);
	comp("Prettyprinted object (keyOwnLine|openOwnLine|endOwnLine, specific)",
		'{\n\t"a":\n\t\t[\n\t\t\t0x1,2,{\n\t\t\t\t"b":\n\t\t\t\t\t"abc"\n\t\t\t},\n\t\t\t3\n\t\t]\n}',
		JSLON.stringify({"a": [1, 2, {"b": "abc"}, 3]},{
			keyOwnLine: true,
			openOwnLine: true,
			endOwnLine: true,
			specific: {a: {specific: [{numBase: 16}]}},
		})
	);
	comp("Prettyprinted object (spaceAfterKey)", '{"a": "b"}',
		JSLON.stringify({"a":"b"}, {spaceAfterKey: true})
	);
	comp("Prettyprinted array (entriesPerLine, depth)", '[1,2,\n 3,4,\n 5]',
		JSLON.stringify([1, 2, 3, 4, 5], {entriesPerLine: 2, depth: " "})
	);
});