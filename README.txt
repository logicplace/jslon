JavaScript Loose Object Notation
 * Copyright 2011 Wa (logicplace.com)
 * MIT Licensed

=== HOW TO USE ===
Browser: <script type="text/javascript" src="jslon.js"></script>
	Access via global object JSLON
Node.JS: var JSLON = require("jslon");

=== DESCRIPTION ===
This is more akin to how objects can be defined inline in JavaScript than
strict JSON is, however it's even looser in some regards.

It can parse key names with single quotes, double quotes, or no quotes.
Commas between entries in an object or array are not required.

May define strings, numbers, regex, arrays, and objects. Statics ONLY.
Strings may be defined with single or double quotes, or no quotes if it's a
valid JavaScript variable name (only contains a-zA-Z0-9_$ and the first
character isn't a number).
Numbers may be defined in decimal (##), hex (0x##), or octal (0##). You may
also define decimals as floats (#.# or #e#). If a number on either side of the
period is missing it's assumed to be 0. The left number for e is required.

All escape sequences in a string work as they do in normal JavaScript:
*) \n -> 0x0a
*) \t -> 0x09
*) \r -> 0x0d
*) \f -> 0x0c
*) \b -> 0x08
*) \0 - \377 -> Octal char code (note: can always be up to three digits, 
   eg. \0 is the same as \000)
*) \x00 - \xff -> Hex char code
*) \u0000 - \uffff -> Unicode codepoint in hex
*) \. -> . (where . is anything)

Supports comments, both forms.

Supports globals: Infinity, NaN, true, false, null, and undefined

Also does not error on duplicate entries in objects, it silently overrides
previous entries.

Stringify takes in a value (one of those mentioned above) and optionally an
object containing formatting options. By default these options are akin to
valid JSON (however it allows RegExp where strict JSON does not).

Options:
*) quotes: ' or " (default)
*) keyQuotes: true (default)/false
  true if keys are always quoted
*) numBase: 8, 10 (default), or 16
  That is; octal, decimal, or hexadecimal, respectively. This does not affect
   floats, they're always written in decimal.
*) strEscapes: cu (default)
  String containing c(haracter) u(nicode) (he)x(idecimal) o(ctal short) or
   O(ctal long). Valid formatting: /(?=.)c?[oOx]?u?/
  Essentially it regards the order as possibilities based on availability:
  (In order)
  If c is enabled and the character has a \c type escape, use that.
  If o O or x is enabled and the character code is one byte (ie. < 256), use
   the given escape form.
  If u is enabled, use the unicode escape form.
  Otherwise, drop character.
Prettyprint options:
*) entriesPerLine: 0 (default, meaning all), 1+
  How many entries in an Array or Object should be on the same line.
*) openOwnLine: true/false (default)
  Only refers to contents being on a different line as [ or {
  (eg. in a list [1,2,{etc}] it's split at 1 and etc, but not before the {
*) endOwnLine: true/false (default)
  However if in a list, a comma may appear after.
*) keyOwnLine: true/false (default)
  true if value and key are on different lines. Indents the data, as well.
*) spaceAfterKey: true/false (default)
  Prints {"a": "hi"} instead of {"a":"hi"}
*) depth: "\t" (default)
  The whitespace used to increase the depth. (Do not use non-whitespace chars)
*) specific: null (default)
  Object mimicing partial structure of obj, defining the above at specific
   points. Note subchilds must be an options structure with a specific entry
   for the subchild.
  Options are inherited.
