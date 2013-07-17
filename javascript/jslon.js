/* Extremely loose JSON interpreter.
 * Copyright 2011 Wa (logicplace.com)
 * MIT Licensed
 */

JSLON = (function() {
var specification = /[\[{\]},:]|\s+|\/\*[\s\S]*\*\/|\/\/.*|"(\\.|\\(\r?\n|\n?\r)|[^"])*"|'(\\.|\\(\r?\n|\n?\r)|[^'])*'|\/(\\.|[^\/])+\/[igm]*|[$_a-zA-Z][$_a-zA-Z0-9]*|[+\-]?0x[0-9a-fA-F]+|[+\-]?[0-9]+e[+\-]?[0-9]*|[+\-]?[0-9]*\.[0-9]*|[+\-]?[0-9]+|Infinity|NaN|true|false|null|undefined/g

function usO(a, v){ return String.fromCharCode(parseInt(v,  8)); }
function usX(a, v){ return String.fromCharCode(parseInt(v, 16)); }
function unescapeString(string) {
	return string
	.replace(/\\(\r?\n|\n?\r)/g, "")
	.replace(/\\n/g, "\n")
	.replace(/\\t/g, "\t")
	.replace(/\\r/g, "\r")
	.replace(/\\f/g, "\f")
	.replace(/\\b/g, "\b")
	.replace(/\\([0-3]?[0-7]{1,2})/g, usO)
	.replace(/\\x([0-9a-fA-F]{2})/g, usX)
	.replace(/\\u([0-9a-fA-F]{4})/g, usX)
	.replace(/\\(.)/g, "\\1")
	;
}

function escapeString(str, q, esc) {
	var esc = (esc || "cu").match(/(c?)([oOx]?)(u?)/);
	if(!esc || (!esc[1] && !esc[2] && !esc[3])) {
		//Defaults
		esc = ["cu", "c", "", "u"];
	}

	return q + str.replace(/[^ -\[\]-~'"]/g, function(m) {
		var cc = m.charCodeAt(0);
		if(m == "\\") return "\\\\";
		else if(m == q) return "\\" + q;
		else if(m == "'" || m == '"') return m;
		else if(esc[1] && m == "\n") return "\\n";
		else if(esc[1] && m == "\t") return "\\t";
		else if(esc[1] && m == "\r") return "\\r";
		else if(esc[1] && m == "\f") return "\\f";
		else if(esc[1] && m == "\b") return "\\b";
		else if(esc[2] && cc < 256) switch(esc[2]) {
			case "x":
				var ret = cc.toString(16);
				if(ret.length == 1) return "\\x0" + ret;
				else return "\\x" + ret;
			case "o": return "\\" + cc.toString(8);
			case "O": {
				var ret = cc.toString(8);
				switch(ret.length) {
					case 1: return "\\00" + ret;
					case 2: return "\\0"  + ret;
					case 3: return "\\"  + ret;
				}
			}
		} else if(esc[3]) {
			var ret = cc.toString(16);
			switch(ret.length){
				case 1: return "\\u000" + ret;
				case 2: return "\\u00"  + ret;
				case 3: return "\\u0"   + ret;
				case 4: return "\\u"    + ret;
			}
		} else return "";
	}) + q;
}

function specific(obj, key, opts, depth) {
	var spec = opts.specific;
	if(spec && obj.constructor.name == spec.constructor.name && key in spec && spec[key]) {
		spec = spec[key];
		for(var k in opts) {
			if(!(k in spec) && k != "specific") spec[k] = opts[k]
		}
		return stringifyValue(obj[key], spec, depth);
	}
	return stringifyValue(obj[key], opts, depth);
}

var nextIsNewLine = false;
function stringifyValue(obj, options, depth) {
	var nextDepth = (options.depth || "\t");
	switch(obj.constructor.name) {
		case "Object": {
			var ret = "{", entries = 0;
			depth += nextDepth;
			if(options.openOwnLine) ret += "\n" + depth;
			for(var key in obj) {
				if(nextIsNewLine) ret += "\n" + depth;
				if(options.entriesPerLine && entries == options.entriesPerLine) {
					if(!nextIsNewLine)ret += "\n" + depth;
					entries = 0;
				}
				nextIsNewLine = false;
				var q = "";
				if(!("keyQuotes" in options) || options.keyQuotes) q = options.quotes || '"';
				if(q == "" && key.match(/^[$_a-zA-Z][$_a-zA-Z0-9]*$/)) {
					ret += key + ":";
				} else {
					ret += escapeString(key, q || '"', options.strEscapes) + ":";
				}
				if(options.spaceAfterKey) ret += " ";
				if(options.keyOwnLine) {
					depth += nextDepth;
					ret += "\n" + depth;
				}
				ret += specific(obj, key, options, depth) + ",";
				if(options.keyOwnLine) {
					depth = depth.slice(0, -nextDepth.length);
				}
				++entries;
			}
			ret = ret.slice(0, -1)
			depth = depth.slice(0, -nextDepth.length);
			if(options.endOwnLine) {
				if(!ret.match(/[\r\n]\s*$/)) ret += "\n" + depth;
				nextIsNewLine = true;
			}
			return ret + "}";
		} case "Array": {
			var ret = "[";
			depth += nextDepth;
			if(options.openOwnLine) ret += "\n" + depth;
			for(var i = 0, entries = 0; i < obj.length; ++i, ++entries) {
				if(nextIsNewLine) ret += "\n" + depth;
				if(options.entriesPerLine && entries == options.entriesPerLine) {
					if(!nextIsNewLine) ret += "\n" + depth;
					entries = 0;
				}
				nextIsNewLine = false;
				ret += specific(obj, i, options, depth) + ",";
			}
			ret = ret.slice(0, -1)
			depth = depth.slice(0, -nextDepth.length);
			if(options.endOwnLine) {
				if(!ret.match(/[\r\n]\s*$/)) ret += "\n" + depth;
				nextIsNewLine = true;
			}
			return ret + "]";
		} case "String": {
			if(options.quotes == "'" || options.quotes == '"') {
				return escapeString(obj, options.quotes, options.strEscapes);
			} else {
				return escapeString(obj, '"', options.strEscapes);
			}
		} case "Number": {
			if(obj == NaN || obj == Infinity) return obj.toString();
			switch(Math.floor(obj) != obj ? 10 : (options.numBase || 10)){
				case 8: return "0" + obj.toString(8);
				case 10: return obj.toString();
				case 16: return "0x" + obj.toString(16);
			}
		} case "Boolean": case "RegExp": {
			return obj.toString();
		}
	}
}

return {
	parse: function(string){
		var tokens = string.match(specification), ret, parents = [], cur = null, curIdx = null;
		if(!tokens)throw new SyntaxError("Unable to tokenize.");

		//console.log(tokens);

		function set(x, key) {
			if(key == ":") {
				curIdx = String(x);
			} else {
				if(curIdx != null) {
					cur[curIdx] = x;
					curIdx = null;
				}
				else if(cur != null) cur.push(x);
				else ret = x;
				if(x != null && (x.constructor.name == "Object" || x.constructor.name == "Array")) {
					parents.push(cur);
					cur = x;
				}
			}
		}

		function up(nom){
			if(parents.length == 0) {
				throw new SyntaxError("Ending " + nom + " without a beginning.");
			}
			cur = parents.pop();
		}

		//Remove junk
		var newTokens = [];
		for(var i=0; i < tokens.length; ++i) {
			if(!tokens[i].match(/^(\s+|\/\*[\s\S]*\*\/|\/\/.*)$/)) {
				newTokens.push(tokens[i]);
			}
		}
		tokens = newTokens;

		//Process tokens
		for(var i=0; i < tokens.length; ++i) {
			var token = tokens[i];
			//console.log(token);
			switch(token.charAt(0)) {
				case ":": break; //Already taken care of
				case "{": set({}); break;
				case "[": set([]); break;
				case "}": up("brace"); break;
				case "]": up("bracket"); break;
				case ",":
					if(cur == null) throw new SyntaxError("Unexpected comma.");
					break;
				case "/":
					var end = token.lastIndexOf("/");
					//Make regex
					set(new RegExp(token.slice(1, end).replace("\\/", "/"), token.slice(end + 1)));
					break;
				case "'":
					set(unescapeString(token.slice(1, -1)), tokens[i+1]);
					break;
				case '"':
					set(unescapeString(token.slice(1, -1)), tokens[i+1]);
					break;
				default:
					switch(token) {
						case "Infinity": set(Infinity, tokens[i+1]); break;
						case "NaN": set(NaN, tokens[i+1]); break;
						case "true": set(true, tokens[i+1]); break;
						case "false": set(false, tokens[i+1]); break;
						case "null": set(null, tokens[i+1]); break;
						case "undefined": set(undefined, tokens[i+1]); break;
						default:
							var tk;
							if(tk=token.match(/([+\-]?)0x(.*)/)) { //Hex
								set(parseInt(tk[1] + tk[2], 16));
							} else if(token.match(/^[+\-]?[0-9]+e[+\-]?[0-9]*$/)) { //Float
								set(parseFloat(token));
							} else if(token.match(/^[+\-]?[0-9.]+$/)) { //Number
								if(token == ".") set(0);
								else if(token.indexOf(".") != -1) set(parseFloat(token));
								else if((tk = token.match(/^([+\-]?)0(.*)/))) {
									set(parseInt(tk[1] + tk[2],8));
								} else set(parseInt(token));
							} else { //Key/literal (variable name limitations)
								set(token, tokens[i+1]);
							}
							break;
					}
					break;
			}
		}
		return ret;
	},

	stringify: function(obj, options){
		if(typeof(options) == "undefined") options = {};
		nextIsNewLine = false;
		return stringifyValue(obj, options, "");
	},
}
})();

if(typeof(module) != "undefined") {
	module.exports = JSLON;
}

