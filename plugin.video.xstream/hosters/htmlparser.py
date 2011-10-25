# -*- coding: iso-8859-15 -*-

from urllib import quote, quote_plus
import re

ElementClassesOfInterest = { "input": ["type", "name", "id", "value"], "img": ["name", "id", "src"] }

def getvalue( haystack, field ):			# return the value in haystack: '... field=value ...'
	lower = haystack.lower().replace(">", " ")
	p = lower.find( field+"=" )
	if p > -1:
		p += len( field )+1
	else:
		return ""
	if haystack[p] == '"':			# " ist Trennzeichen
		p += 1
		q = lower.find( '"', p )
	elif haystack[p] == "'":			# ' ist Trennzeichen
		p += 1
		q = lower.find( "'", p )
	else:					# Keine Gänsefüßchen, Leerzeichen trennt zum nächsten Feldnamen
		q = lower.find( " ", p )
	return haystack[p:q]

class Element:				# Form method parse stores it's elements as array of Element classes
	def __init__(self, HTML):
		p = HTML.find("<")+1
		if p == -1:
			return None
		q = HTML.find(" ", p)
		self.Class = HTML[p:q].lower()
		if self.Class in ElementClassesOfInterest.keys():
			for field in ElementClassesOfInterest[ self.Class ]:
				self.__dict__[ field ] = getvalue( HTML, field )

class Form:				# Robot method parse() stores results as array of Form classes
	def __init__(self, HTML=None):
		if HTML is not None:
			self.parse( HTML )
		else:
			self.name = self.id = self.action = self.method = ""

	def parse(self, HTML):
		self.name   = getvalue( HTML, "name" )
		self.id	    = getvalue( HTML, "id" )
		self.action = getvalue( HTML, "action" )
		self.method = getvalue( HTML, "method" )

		lower = HTML.lower()	# mit ">"
		for Class in ElementClassesOfInterest.keys():
			self.__dict__[ Class ] = []
			starter = "<"+Class+" "
			p = lower.find( starter )
			while ( p > -1 ):
				q = lower.find( ">", p )
				self.__dict__[ Class ].append( Element(HTML[p:q]) )
				p = lower.find( starter, q )

	def getElement(self, name=None, ID=None):
		if name is not None:
			for Class in ElementClassesOfInterest.keys():
				for element in self.__dict__[ Class ]:
					if element.name == name:
						return element
		elif ID is not None:
			for Class in ElementClassesOfInterest.keys():
				for element in self.__dict__[ Class ]:
					if element.id == ID:
						return element
		return None

	def POSTdict(self):
		result = {}
		for i in self.input:
			result[ i.name ] = quote_plus( i.value ) #.replace(" ", "+")
		return result

	def POSTline(self):
		result = ""
		for i in self.input:
			result += i.name+"="+quote_plus( i.value )+"&"
		return result.rstrip("&")

def between(haystack, before, after, occurence=1):
	start = 0
	for i in range(1, occurence):
		start = haystack.find(before, start)+1
	p = haystack.find(before, start)+len(before)
	q = haystack.find(after, p)
	return haystack[p:q]

def convert_to_base(number, base):
	currentbase = base
	while number >= currentbase:
		currentbase = currentbase * base
	result = ""
	while currentbase > 1:
		currentbase = int(currentbase/base)
		d = int(number/currentbase)
		number -= d*currentbase
		if d < 10:
			result += str(d)
		else:
			result += chr(ord('a')+d-10)
	return result

class Eval:
	def __init__(self, source):
		self.source = source

	def __str__(self):
		return self.source

	def unpack(self):
		p = self.source.find("('", self.source.find("return p"))+2
		q = self.source.find("',", p)
		P = self.source[p:q]						# input
		q += 2
		r = self.source.find(",", q)
		A = int(self.source[q:r])					# base to convert to
		r += 1
		s = self.source.find(",'", r)
		C = int(self.source[r:s])					# magic number
		s += 2
		t = self.source.find("'.split", s)
		K = self.source[s:t].split("|")					# replacement dictionary
		return P,A,C,K

	def deobfuscate(self):
#		function(p,a,c,k,e,d) {
#			while(c--):
#				if(k[c]):
#					p=p.replace(new RegExp('\\b'+c.toString(a)+'\\b','g'),k[c]);
#			return p
#			}
		code, base, number, dictionary = self.unpack()

		while number >= 0:
			if number < len(dictionary):
				before = convert_to_base(number, base)
				after = dictionary[number]
				code = re.sub(r'\b'+before+r'\b', after, code)
			number -= 1
		return code

class HTML:
	def __init__(self, HTML):
		self.string = HTML
		self.forms = None

	def debug(self, msg):
		print msg

	def __str__(self):
		return self.string

	def lower(self):
		return self.string.lower()

	def find(self, needle, start_at=0):
		return self.string.find(needle, start_at)

	def parse(self):
		if self.forms is not None:
			return
		self.forms = []

		self.debug("Searching document for forms ...")
		lower = self.lower()
		p = lower.find("<form")						# find form
		while ( p > -1 ):
			if lower[p+5] == " " or lower[p+5] == ">":		# is it "<form " or "<form>" ?
				q = lower.find("</form>", p)+7			# find end of form
				if q == -1:
					q = len(lower)				# if end not found, copy until end of file
				self.forms.append( Form(self.string[p:q]) )
			else:
				q = p+1
			p = lower.find("<form", q)

		self.debug("Found "+str(len(self.forms))+" forms.")

	def find_form(self, name=None, ID=None, action=None):			# return specified form
		if self.forms is None:
			self.parse()						# parse, if not parsed already
		if name is not None:
			for form in self.forms:
				if form.name == name:				# get form by name
					return form
		elif ID is not None:
			for form in self.forms:
				if form.id == ID:				# get form by ID
					return form
		elif action is not None:
			for form in self.forms:
				if form.action == action:			# get form by action
					return form
		elif len(self.forms) > 0:					# if no parameters are given, return the first form
			return self.forms[0]
		return None

	def find_eval(self, occurence=1):
		return Eval("eval("+between(self.string, "eval(", "</script>", occurence).strip())

	def save(self, filename=None):
		if filename is None:
			filename = "robot.html"
		open(filename,"w").write(self.string)

