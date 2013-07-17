#-*- coding:utf-8 -*-
# Extremely loose JSON interpreter.
# Copyright 2013 Wa (logicplace.com)
# MIT Licensed

import re

class undefined(object):
	def __nonzero__(self): return False
	def __eq__(self, other): return other == undefined or self.__class__ == other.__class__
#endclass

class options(dict):
	def __init__(self, opts = {}):
		def default(name, default):
			self[name] = opts[name] if name in opts else default
		#enddef

		default("quotes", '"')
		default("keyQuotes", True)
		default("numBase", 10)
		default("strEscapes", "cu")
		default("entriesPerLine", 0)
		default("openOwnLine", False)
		default("endOwnLine", False)
		default("keyOwnLine", False)
		default("spaceAfterKey", False)
		default("depth", "\t")
		default("specific", None)

		# Ensure all "specific" entries are instantiations of options.
		spec = self
		while spec["specific"] is not None and spec["specific"].__class__ is dict:
			spec = spec["specific"] = options(spec["specific"])
		#endwhile
	#enddef
#endclass

class JSLON(object):
	__specification = re.compile(
		r'([\[{\]},:])|'                             # Flow
		r'\s+|'                                      # Space
		r'\/\*[\s\S]*\*\/|'                          # Comment (Multi-line)
		r'\/\/.*|'                                   # Comment (EOL)
		r'"((?:\\.|\\(?:\r?\n|\n?\r)|[^"])*)"|'      # Single quoted string
		r"'((?:\\.|\\(?:\r?\n|\n?\r)|[^'])*)'|"      # Double quoted string
		r'\/((?:\\.|[^\/])+)\/([igm]*)|'             # RegEx
		r'(Infinity|NaN|true|false|null|undefined)|' # Constants
		r'([$_a-zA-Z][$_a-zA-Z0-9]*)|'               # Variable name/valid key
		r'([+\-]?0x[0-9a-fA-F]+)|'                   # Hexadecimal
		r'([+\-]?[0-9]+e[+\-]?[0-9]*)|'              # Float (e-notation)
		r'([+\-]?[0-9]*\.[0-9]*)|'                   # Float (decimal notation)
		r'([+\-]?[0-9]+)'                            # Number
	)

	__escspec    = re.compile(r'(c?)([oOx]?)(u?)')
	__badchars   = re.compile(r'[^ -\[\]-~'"'"'"]')
	__validkey   = re.compile(r'^[$_a-zA-Z][$_a-zA-Z0-9]*$')
	__endswithnl = re.compile(r'[\r\n]\s*$')

	__replcont  = re.compile(r'\\(?:\r?\n|\n?\r)')
	__reploct   = re.compile(r'\\([0-3]?[0-7]{1,2})')
	__replhex   = re.compile(r'\\x([0-9a-fA-F]{2})')
	__repluni   = re.compile(r'\\u([0-9a-fA-F]{4})')
	__replother = re.compile(r'\\(.)')

	@staticmethod
	def __usO(mo): return unichr(int(mo.group(1), 8))
	@staticmethod
	def __usX(mo): return unichr(int(mo.group(1), 16))
	@staticmethod
	def __usOther(mo):
		c = mo.group(1)
		if   c == "n": return u"\n"
		elif c == "t": return u"\t"
		elif c == "r": return u"\r"
		elif c == "f": return u"\f"
		elif c == "b": return u"\b"
		else: return c
	#enddef

	@staticmethod
	def __unescapeString(string):
		return JSLON.__replother.sub(JSLON.__usOther,
			JSLON.__repluni.sub(JSLON.__usX, JSLON.__replhex.sub(JSLON.__usX,
				JSLON.__reploct.sub(JSLON.__usO, JSLON.__replcont.sub("",
					string
				))
			))
		)
	#enddef

	@staticmethod
	def __escapeString(string, q, esc="cu"):
		esc = JSLON.__escspec.match(esc).groups()
		if not (esc[0] or esc[1] or esc[2]):
			esc = ("c", "", "u")
		#endif

		def esBC(mo):
			m = mo.group(0)
			cc = ord(m)
			if m == "\\": return u"\\\\"
			elif m == q: return u"\\" + q
			elif m == "'" or m == '"': return m
			elif esc[0] and m == "\n": return u"\\n"
			elif esc[0] and m == "\t": return u"\\t"
			elif esc[0] and m == "\r": return u"\\r"
			elif esc[0] and m == "\f": return u"\\f"
			elif esc[0] and m == "\b": return u"\\b"
			elif esc[1] and cc < 256:
				if   esc[1] == "x": return u"\\x%02x" % cc
				elif esc[1] == "o": return u"\\%o" % cc
				elif esc[1] == "O": return u"\\%03o" % cc
			elif esc[2]: return u"\\u%04x" % cc
			# Should never come to this.
			else: return u""
		#enddef

		return q + JSLON.__badchars.sub(esBC, string) + q
	#enddef

	def __init__(self, obj=None):
		self.__nextIsNewLine = False
		if obj is not None:
			self.data = obj
		#endif
	#enddef

	def __specific(self, obj, key, opts, depth=""):
		spec = opts["specific"]
		if spec and type(obj) == type(spec) and (
			(type(spec) is list and key < len(spec)) or
			(type(spec) is dict and key in spec)
		) and spec[key]:
			spec = spec[key]
			for k in opts:
				if k not in spec and k != "specific": spec[k] = opts[k]
			#endfor
			return self.__stringifyValue(obj[key], spec, depth)
		#endif
		return self.__stringifyValue(obj[key], opts, depth)
	#enddef

	def __stringifyValue(self, obj, opts, depth=""):
		nextDepth = opts["depth"]
		objtype = type(obj)
		if   obj is None: return "null"
		elif obj == undefined: return "undefined"
		elif objtype == dict:
			ret, entries = u"{", 0
			depth += nextDepth
			if opts["openOwnLine"]: ret += u"\n" + depth;
			for key in obj:
				if self.__nextIsNewLine: ret += u"\n" + depth
				if opts["entriesPerLine"] and entries == opts["entriesPerLine"]:
					if not self.__nextIsNewLine: ret += u"\n" + depth
					entries = 0;
				#endif
				self.__nextIsNewLine = False

				if opts["keyQuotes"]: q = opts["quotes"]
				else: q = u""

				if q == u"" and JSLON.__validkey.match(key):
					ret += key + u":"
				else:
					ret += self.__escapeString(key, q or u'"', opts["strEscapes"]) + u":";
				#endif

				if opts["spaceAfterKey"]: ret += u" "
				if opts["keyOwnLine"]:
					depth += nextDepth
					ret += u"\n" + depth
				#endif
				ret += self.__specific(obj, key, opts, depth) + u",";
				if opts["keyOwnLine"]:
					depth = depth[0:-len(nextDepth)]
				#endif

				entries += 1
			#endfor
			ret = ret[0:-1]
			depth = depth[0:-len(nextDepth)]

			if opts["endOwnLine"]:
				if not JSLON.__endswithnl.search(ret): ret += u"\n" + depth
				self.__nextIsNewLine = True
			#endif
			return ret + u"}"
		elif objtype == list:
			ret, entries = u"[", 0
			depth += nextDepth
			if opts["openOwnLine"]: ret += u"\n" + depth
			for i in range(len(obj)):
				if self.__nextIsNewLine: ret += u"\n" + depth
				if opts["entriesPerLine"] and entries == opts["entriesPerLine"]:
					if not self.__nextIsNewLine: ret += u"\n" + depth;
					entries = 0;
				#endif
				self.__nextIsNewLine = False

				ret += self.__specific(obj, i, opts, depth) + u",";
				entries += 1
			#endfor
			ret = ret[0:-1]
			depth = depth[0:-len(nextDepth)]

			if opts["endOwnLine"]:
				if not JSLON.__endswithnl.search(ret): ret += u"\n" + depth
				self.__nextIsNewLine = True
			#endif
			return ret + u"]"
		elif objtype in [str, unicode]:
			return unicode(JSLON.__escapeString(obj,
				opts["quotes"] if opts["quotes"] in ["'", '"'] else u'"',
				opts["strEscapes"]
			))
		elif objtype in [int, long, float]:
			if objtype == float:
				if   str(obj) == "nan": return u"NaN"
				elif str(obj) == "inf": return u"Infinity"
				else: base = 10
			else: base = opts["numBase"]
			if   base ==  8: return u"0%o" % obj
			elif base == 10: return unicode(obj)
			elif base == 16: return u"0x%x" % obj
		elif objtype == bool:
			return u"true" if obj else u"false"
		elif objtype == type(JSLON.__specification):
			# TODO: Check if RegEx is valid for JavaScript.
			return u"/" + obj.pattern + u"/g" + (u"i" if obj.flags & re.I else u"") + (u"m" if obj.flags & re.M else u"")
		else: raise Exception("Cannot encode type %s as JSON." % objtype.__name__)
	#enddef

	def parse(self, string):
		parents, p = [], [None, None]
		# p is cur, curIdx

		def setval(x, key=None, p=p):
			if key == ":":
				p[1] = str(x)
			else:
				if p[1] is not None:
					p[0][p[1]] = x
					p[1] = None
				elif p[0] is not None: p[0].append(x)
				if type(x) in [dict, list]:
					parents.append(p[0])
					p[0] = x
				#endif
			#endif
		#enddef

		def up(name, parents=parents, p=p):
			if len(parents) == 0:
				raise SyntaxError("Ending " + name + " without a beginning.")
			#endif
			p[0] = parents.pop()
		#enddef

		def listget(ls, i):
			if i < len(ls): return ls[i]
			else: return [None]
		#enddef

		tokens = JSLON.__specification.findall(string)
		for i, token in enumerate(tokens):
			flow, sstr, dstr, regex, reflags, const, uqkey, hexnum, efloat, dfloat, num = token
			string = sstr or dstr or uqkey
			afloat = efloat or dfloat

			if flow:
				if   flow == ":": continue # Already handled
				elif flow == "{": setval({})
				elif flow == "[": setval([])
				elif flow == "}": up("brace")
				elif flow == "]": up("bracket")
				elif flow == ",":
					if p[0] is None: raise SyntaxError("Unexpected comma.")
				#endif
			elif regex:
				# In Python, the global flag isn't considered.
				setval(re.compile(
					regex.replace(r'\/', "/"),
					(re.I if "i" in reflags else 0) | (re.M if "m" in reflags else 0)
				))
			elif string: setval(JSLON.__unescapeString(string), listget(tokens, i + 1)[0])
			elif hexnum: setval(int(hexnum, 16))
			elif afloat:
				# Special case.
				if afloat == ".": setval(0)
				# In JavaScript, #.0* is int type, not float.
				elif afloat.replace("0", "")[-1] == ".": setval(int(afloat[0:afloat.index(".")]))
				else: setval(float(afloat))
			elif num:
				if num[0] == "0": setval(int(num, 8))
				else: setval(int(num))
			elif const:
				nextFlow = listget(tokens, i + 1)[0]
				iscol = nextFlow == ":"
				if   const == "Infinity":  setval(const if iscol else float("inf"), nextFlow)
				elif const == "NaN":       setval(const if iscol else float("nan"), nextFlow)
				elif const == "true":      setval(const if iscol else True,         nextFlow)
				elif const == "false":     setval(const if iscol else False,        nextFlow)
				elif const == "null":      setval(const if iscol else None,         nextFlow)
				elif const == "undefined": setval(const if iscol else undefined(),  nextFlow)
			#endif
		#endfor
		self.data = p[0]
		return self
	#enddef

	def stringify(self, opts = {}):
		self.__nextIsNewLine = False
		return self.__stringifyValue(self.data, options(opts))
	#enddef

	def __len__(self): return len(self.data)
	def __getitem__(self, key): return self.data[key]
	def __setitem__(self, key, data): self.data[key] = data
	def __delitem__(self, key): del self.data[key]
	def __iter__(self): return iter(self.data)
	def __contains__(self, item): return item in self.data
#endclass

def parse(string): return JSLON().parse(string).data
def stringify(obj, opts = {}): return JSLON(obj).stringify(opts)