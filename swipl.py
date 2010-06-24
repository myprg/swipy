# -*- coding: cp1251 -*-
"""
	Author: Yosifov V. Pavel, 2008

Naming convention:
	atom, pl, ... - Python objects. In object they are Python objects as internal
	attributes of outter object, created, usually, in __init__. More good way
	to use special methods to get some information about object.

	pl_... - SWI-Prolog object, like term_t. You may use it to have full access
	to SWI-Prolog objects (for PlUtils calling, for example).

	PlSomething - typical Python class-name in this module.

	Original PL_* functions exists in Python objects without 'PL_'-prefix.

Validation of types:
	Raise TypeError occurs only for variable which will be tested by
	isinstance(). Other type checking does not supported.

Object manipulations:
	You can construct uninitialise object (see args in __init__()). This object
	is used for _init_from_pl ONLY!
"""

# TODO Все вызовы self.pl.PL_ сделать через вызовы PlUtils и в ней узнавать некоторые методы
# и вызывать их через сигнатуру (прототип)!!! Т.к. есть подозрения что на других
# платформах (не I386) будет сыпаться (неявные преобразования например uint-ов в
# указатели)

from ctypes import *
import types
import sys
from plutils import Caller as DLLCaller

# configuration section

# DLL-name depends on OS.
# ATTANTION: OS NAME MUST BE IN UPPER CASE!
OS_DEPEND_DLL = (
	('','libpl.so'),         # default DLL when OS is unknown, MUST BE FIRST!
	('WIN','libpl.dll'),
	('FREEBSD','libpl.so'),
	('LINUX','libpl.so'),
	)

# end of configuration section


PL_Q_NORMAL = 0x02				# normal usage
PL_Q_NODEBUG = 0x04				# use this one
PL_Q_CATCH_EXCEPTION = 0x08		# handle exceptions in C
PL_Q_PASS_EXCEPTION = 0x10      # pass to parent environment

# TERM TYPE CONSTANTS
PL_VARIABLE = 1
PL_ATOM = 2
PL_INTEGER = 3
PL_FLOAT = 4
PL_STRING = 5
PL_TERM = 6


PL_FUNCTOR = 10
PL_LIST = 11
PL_CHARS = 12
PL_POINTER = 13

PL_CODE_LIST = 14
PL_CHAR_LIST = 15
PL_BOOL = 16
PL_FUNCTOR_CHARS = 17
_PL_PREDICATE_INDICATOR = 18
PL_SHORT = 19
PL_INT = 20
PL_LONG = 21
PL_DOUBLE = 22
PL_NCHARS = 23
PL_UTF8_CHARS = 24
PL_UTF8_STRING = 25
PL_INT64 = 26
PL_NUTF8_CHARS = 27
PL_NUTF8_CODES = 29
PL_NUTF8_STRING = 30
PL_NWCHARS = 31
PL_NWCODES = 32
PL_NWSTRING = 33
PL_MBCHARS = 34
PL_MBCODES = 35
PL_MBSTRING = 36
PL_INTPTR = 37


def term_t_to_integer( pl_term ):
	pass


def safer( f, defval=None ):
	"""Function decorator. Create safe-function from
	unsafe (raised exception). Return defval but exception"""
	def w( *a, **ka ):
		try:
			return f( *a, **ka )
		except:
			return defval
	return w

#--------------------------------- Base error ------------------------------
class PlError( Exception ): pass

#----------------------- Base Prolog object --------------------------------
class PlObject( object ):
	"""SWI-Prolog object in Python representation"""

	def __init__( self, pl ):
		self.pl = pl
#-------------------------------------- Prolog utils -----------------------------------
class PlUtils( DLLCaller, PlObject ):
	"""Utilitary functions. Alternative way to call SWI-Prolog functions.
	Arguments are SWI-Prolog data types (like
	term_t, atom_t) which is accessible in Python classes as:
	'obj.pl_SOMETHING or usual C-types'
	"""
	def __init__( self, pl ):
		_TYPE_CONS = {
		'module_t':c_void_p,
		'atom_t':POINTER(c_uint),
		'predicate_t':c_void_p,
		'record_t':c_void_p,
		'term_t':POINTER(c_uint),
		'qid_t':POINTER(c_uint),
		'control_t':c_void_p,
		'functor_t':POINTER(c_uint),
		}
		_PROTO = {
		'PL_initialise':'->int',
		'PL_halt':'int',
		'PL_new_term_refs':'c_int->term_t',
		'PL_new_term_ref':'void->term_t',
		'PL_copy_term_ref':'term_t->term_t',
		'PL_reset_term_refs':'term_t->void',
		'PL_new_atom':'char_p->atom_t',
		'PL_new_atom_nchars':'c_int,char_p->atom_t',
		'PL_new_atom_wchars':'c_int,c_wchar_p->atom_t',
		'PL_atom_chars':'atom_t->char_p',
		'PL_atom_nchars':'atom_t,c_int_p->char_p',
		'PL_atom_wchars':'atom_t,c_int_p->c_wchar_p',
		'PL_new_functor':'atom_t,c_int->functor_t',
		'PL_functor_name':'functor_t->atom_t',
		'PL_functor_arity':'functor_t->c_int',
		'PL_put_variable':'term_t->void',
		'PL_put_atom':'term_t,atom_t->void',
		'PL_put_atom_chars':'term_t,char_p->void',
		'PL_put_string_chars':'term_t,char_p->void',
		'PL_put_list_chars':'term_t,char_p->void',
		'PL_put_list_codes':'term_t,char_p->void',
		'PL_put_atom_nchars':'term_t,c_int,char_p->void',
		'PL_put_string_nchars':'term_t,c_int,char_p->void',
		'PL_put_list_nchars':'term_t,c_int,char_p->void',
		'PL_put_list_ncodes':'term_t,c_int,char_p->void',
		'PL_put_integer':'term_t,c_long->void',
		'PL_put_pointer':'term_t,c_void_p->void',
		'PL_put_float':'term_t,c_double->void',
		'PL_put_functor':'term_t,functor_t->void',
		'PL_put_list':'term_t->void',
		'PL_put_nil':'term_t->void',
		'PL_is_variable':'term_t->c_int',
		'PL_is_ground':'term_t->c_int',
		'PL_is_atom':'term_t->c_int',
		'PL_is_integer':'term_t->c_int',
		'PL_is_string':'term_t->c_int',
		'PL_is_float':'term_t->c_int',
		'PL_is_rational':'term_t->c_int',
		'PL_is_compound':'term_t->c_int',
		'PL_is_callable':'term_t->c_int',
		'PL_is_functor':'term_t,functor_t->c_int',
		'PL_is_list':'term_t->c_int',
		'PL_is_atomic':'term_t->c_int',
		'PL_is_number':'term_t->c_int',

		}
		PlObject.__init__( self, pl )
		verb = True if __debug__ else False
		DLLCaller.__init__( self, pl, _TYPE_CONS, _PROTO, verbose=verb )

	#def __call__( self, fun ):
	#	"""More usuable interfase. Calling like this:
	#	obj('fun:int,int->int')(2,3)
	#	"""
	#	fun = 'PL_%s'%fun
	#	return DLLCaller.__call__( self, fun )

#-------------------------------------- Term -----------------------------------
class PlTerm( PlObject ): # ДОПИСАТЬ: =/__int__,__float__ и т.п.
	def __init__( self, pl, num=1 ):
		"""num - number of terms if this is the term vector creation.
		If num == 0 PlTerm will be uninitialised and does not
		allowed to use it without call _init_from_pl()!"""
		if num < 0:
			raise ValueError( 'arg 2 can not be negative')

		super( PlTerm, self ).__init__( pl )
		if num > 0:
			# if num>0 -- init (create SWI-Prolog object. Otherwise
			# PlTerm will be uninitialised!
			self.num = num
			if self.num == 1:
				self.pl_term = self.pl.PL_new_term_ref()
			elif num > 1:
				self.pl_term = self.pl.PL_new_term_refs( self.num )

	def _init_from_pl( self, pl_term ):
		"""Init from SWI-Prolog term handle.
		Use it currefully only if PlTerm was not initialisied in
		constructor (num==0)!"""
		self.num = 1
		self.pl_term = pl_term

	def __len__( self ): return self.num

	def is_vector( self ):
		"""Is this a vector of terms?"""
		return len( self ) != 1

	def __getitem__( self, index ):
		if self.num > 1 and index < len( self ):
			pl_term = self.pl_term + index
			term = PlTerm( self.pl, 0 ) # Not initialise!
			term._init_from_pl( pl_term )
			return term
		else:
			raise IndexError( 'term index out of range' )

	def put_variable( self ):
		"""Put a fresh variable in the term. The new variable
		lives on the global stack. Note that the initial
		variable lives on the local stack and is lost after
		a write to the term-references. After using this
		function, the variable will continue to live"""
		self.pl.PL_put_variable( self.pl_term )

	def put_atom( self, atom ):
		"""Put an atom in the term reference from a handle"""
		self.pl.PL_put_atom( self.pl_term, atom.pl_atom )

	def put_atom_chars( self, chars ):
		"""Put an atom in the term-reference constructed from
		the 0-terminated string. The string itself will never be
		references by Prolog after this function"""
		self.pl.PL_put_atom_chars( self.pl_term, chars )

	def put_string_chars( self, chars ):
		"""Put a zero-terminated string in the term-reference.
		The data will be copied. See also PL_put_string_nchars()"""
		self.pl.PL_put_string_chars( self.pl_term, chars )

	def put_string_nchars( self, len, buf ):
		"""Put a string, represented by a length/start pointer pair
		in the term-reference. The data will be copied. This interface
		can deal with 0-bytes in the string"""
		self.pl.PL_put_string_nchars( self.pl_term, len, c_char_p(buf) )

	def put_list_chars( self, chars ):
		"""Put a list of ASCII values in the term-reference"""
		self.pl.PL_put_list_chars( self.pl_term, chars )

	def put_integer( self, long_numb ):
		"""Put a Prolog integer in the term reference"""
		self.pl.PL_put_integer( self.pl_term, c_long(long_numb) )

	def put_int64( self, int64_numb ):
		"""Put a Prolog integer in the term reference"""
		self.pl.PL_put_int64( self.pl_term, c_longlong(int64_numb) )

	def put_float( self, float_numb ):
		"""Put a floating-point value in the term-reference"""
		self.pl.PL_put_float( self.pl_term, c_double(float_numb) )

	def put_functor( self, functor ):
		"""Create a new compound term from functor and bind
		self.pl_term to this term. All arguments of the term will be variables.
		functor is the Python object PlFunctor, not SWI-Prolog type functor_t!"""
		self.pl.PL_put_functor( self.pl_term, functor.pl_functor )

	def put_list( self ):
		"""Same as put_functor(l, PlFunctor(PlAtom('.'), 2))"""
		self.pl.PL_put_list( self.pl_term )

	def put_nil( self ):
		"""Same as put_atom_chars('[]')"""
		self.pl.PL_put_nil( self.pl_term )

	def put( self, obj ):
		"""Put obj into term. Corresponds to put_*() family methods.
		obj is switcher to choose correct put_*() method, so:
		    PlAtom          put_atom()
		    str             put_string_chars()
		    buffer          put_string_nchars()
		    int             put_integer()
		    long            put_int64()
		    float           put_float()
		    PlFunctor       put_functor()
		    [...]           put_list_chars()
		    (...)           also put_list_chars()
		    []/()           put_nil()
		    <type 'list'>   put_list()
		    <type 'tuple'>  also put_list()
		    None            put_variable()
		"""
		if isinstance( obj, PlAtom ):
			self.put_atom( obj )
		elif isinstance( obj, str ):
			self.put_string_chars( obj )
		elif isinstance( obj, buffer ):
			self.put_string_nchars( len(obj), str(obj) ) # Is this safe???!!!
		elif isinstance( obj, (list,tuple) ):
			# all elements of obj-sequence str()-ed and
			# create from they one string:
			# ['a','bcd','e'] -> 'abcde'
			self.put_list_chars( ''.join([str(el) for el in obj]) )
		elif obj in (list, tuple):
			self.put_list()
		elif isinstance( obj, int ):
			self.put_integer( obj )
		elif isinstance( obj, long ):
			self.put_int64( obj )
		elif isinstance( obj, float ):
			self.put_float( obj )
		elif isinstance( obj, PlFunctor ):
			self.put_functor( obj )
		elif obj == None:
			self.put_variable()
		else:
			raise TypeError('arg 1 has incorrect type')

	def cons_functor( self, f, *a ):
		"""Create a term, whose arguments are filled from variable
		argument list holding the same number of term_t objects
		as the arity of the functor.
		f - may be PlFunctor with correct arity (depends of *a length) or
		string (name of functor), functor will be created in this case.
		a - are the PlTerms after put_*() something to its"""

		if not isinstance( f, (PlFunctor,str) ):
			raise TypeError('arg 1 must be a string or PlFunctor')

		if type( f ) == str:
			f = PlFunctor( self.pl, f, len(a) )
		self.pl.PL_cons_functor( self.pl_term, f, *[t.pl_term for t in a] )

	def cons_functor_v( self, f, a0 ):
		"""Creates a compound term like cons_functor(), but a0 is a PlTerm,
		created with num>1 (so it is the vector).
		The length of this vector should match the number of arguments required
		by the functor.
		Typical use is:
		    a0 = PlTerm(2)
		    a0[0].put_atom( some_atom1 )
            a0[1].put_atom( some_atom2 )
            some_term.cons_functor_v( some_functor, a0 )
		"""

		if not isinstance( f, (PlFunctor,str) ):
			raise TypeError('arg 1 must be a string or PlFunctor')

		if type( f ) == str:
			f = PlFunctor( self.pl, f, len(a) )
		self.pl.PL_cons_functor_v( self.pl_term, f, a0.pl_term )

	def cons_list( self, head, tail, *other_tails ):
		"""Create a list (cons-) cell in self from the head and tail.
		head, tail and *other_tails must be PlTerm.
		If other_tails specified, all will be added.
		self must be list already (use put_nil())"""
		ts = [tail] + other_tails # all tails
		n = len( ts )-1
		while n >= 0:
			self.pl.PL_cons_list( self.pl_term, ts[n], self.pl_term )
			n -= 1

	def term_type( self ):
		"""Obtain the type of a term. Can return any of:
		PL_VARIABLE, PL_ATOM, PL_STRING, PL_INTEGER, PL_FLOAT,
		PL_TERM (not yet implemented).
		Get term data also check of term's type before to read data"""
		return self.pl.PL_term_type( self.pl_term )

	def is_variable( self ):
		"""True if is variable"""
		return bool( self.pl.PL_is_variable( self.pl_term ) )

	def is_ground( self ):
		"""True if is ground (holds no free variables)"""
		return bool( self.pl.PL_is_ground( self.pl_term ) )

	def is_atom( self ):
		"""True if is atom"""
		return bool( self.pl.PL_is_atom( self.pl_term ) )

	def is_string( self ):
		"""True if is string"""
		return bool( self.pl.PL_is_string( self.pl_term ) )

	def is_integer( self ):
		"""True if is integer"""
		return bool( self.pl.PL_is_integer( self.pl_term ) )

	def is_float( self ):
		"""True if is float"""
		return bool( self.pl.PL_is_float( self.pl_term ) )

	def is_compound( self ):
		"""True if is compound"""
		return bool( self.pl.PL_is_compound( self.pl_term ) )

	def is_functor( self, f ):
		"""True if is functor and its functor is f (PlFunctor)"""
		return bool( self.pl.PL_is_functor( self.pl_term, f.pl_functor ) )

	def is_list( self ):
		"""True if is list term with functor ./2 or the atom []"""
		return bool( self.pl.PL_is_list( self.pl_term ) )

	def is_atomic( self ):
		"""True if is atomic (not variable or compound)"""
		return bool( self.pl.PL_is_atomic( self.pl_term ) )

	def is_number( self ):
		"""True if is number (integer or float)"""
		return bool( self.pl.PL_is_number( self.pl_term ) )

	def get_atom( self ):
		"""If self is an atom, return the unique PlAatom. See also
		PL_atom_chars() and PL_new_atom(). If there is no need to access
		the data (characters) of an atom, it is advised to manipulate atoms
		using their handle. As the atom is referenced by self, it will
		live at least as long as self does. If longer live-time is required,
		the atom should be locked using PL_register_atom()"""

		atom = PlAtom( self.pl, None )
		ut = PlUtils( self.pl )
		atom_t = ut.ctype( 'atom_t' )() # create atom_t instance!
		self.pl.PL_get_atom( self.pl_term, byref(atom_t) )
		atom._init_from_pl( atom_t )
		return atom
#------------------------------------- atom -----------------------------------
class PlAtom( PlObject ):

	def __init__( self, pl, chars ):
		"""chars like 'xxx'. If chars is None, not created SWI-Prolog
		object but you must call _init_from_pl()"""
		super( PlAtom, self ).__init__( pl )
		if chars != None:
			self.chars = chars
			if type( chars ) == unicode:
				self.pl_atom = self.pl.PL_new_atom_wchars( len( self.chars), self.chars )
			else:
				self.pl_atom = self.pl.PL_new_atom_nchars( len( self.chars), self.chars )

	def _init_from_pl( self, pl_atom ):
		"""Init from SWI-Prolog atom handle. Use it if not initialised only"""
		self.pl.PL_atom_chars.restype = c_char_p
		self.chars = self.pl.PL_atom_chars( pl_atom ) # MAY BE GARBAGE COLLECTED?!!! UNICODE???
		self.pl_atom = pl_atom

	def __repr__( self ):
		"""String representation"""
		self.pl.PL_atom_chars.restype = c_char_p
		return self.pl.PL_atom_chars( self.pl_atom )

#----------------------------- Functor -----------------------------------------
class PlFunctor( PlObject ):
	def __init__( self, pl, name, arity ):
		"""Create functor from name (PlAtom) or string (atom will be
		created automatically) with arity"""
		super( PlFunctor, self ).__init__( pl )
		if not isinstance( name, (PlAtom, str) ):
			raise ValueError( 'arg 2 must be PlAtom or string' )
		if type( name ) == str:
			self.name = PlAtom( self.pl, name )
		else:
			self.name = name # PlAtom, not atom_t!
		self.arity = arity
		self.pl_functor = self.pl.PL_new_functor( self.name.pl_atom, arity )

#---------------------------- Factory of all above classes -----------------------------------
def TermCons( cls, pl ):
	"""Create class factory with pre-applied 1st argument (SWI-Prolog library)"""
	def cons( *a, **kw ):
		return cls( pl, *a, **kw )
	return cons

#-------------------------------------- SWI ------------------------------------
class PlEngine:
	Q_FLAGS = PL_Q_CATCH_EXCEPTION # flags of query execution. Exceptions depends on they

	def __init__( self, *args ):
		this_os = sys.platform.upper()
		ARG0 = [dll for os,dll in OS_DEPEND_DLL if (os and os in this_os)] \
			or OS_DEPEND_DLL[0]
		ARG0 = ARG0[0]
		self.pl = None
		try:
			self.dll = CDLL( ARG0 )
			self.pl = PlUtils( self.dll )
		except:
			raise PlError( 'DLL \'%s\' not found'%ARG0 )
		pl_args = [ARG0, '-q'] + list( args ) + [c_char_p()]
		Argv = c_char_p * len( pl_args )
		pl_args_count = len( pl_args ) - 1 # without terminated NULL
		pl_args = Argv( *pl_args )
		# initialisation of SWI PL
		if not self.pl.PL_initialise( pl_args_count, byref( pl_args ) ):
			self.pl.PL_halt(0)
			raise PlError( 'Initialise error' )
		else:
			# Factories. For example, if term=='PlAtom', then PlEngine will
			# has field 'Atom' which create PlAtom object with pre-setted
			# SWI-Prolog library ('obj.pl')
			for term in ('PlUtils','PlTerm','PlAtom','PlFunctor'):
				# cutting 'Pl' in begining of term. All factories will be
				# available without 'Pl' prefix
				setattr( self, term[2:], TermCons( globals()[term], self.pl ) )

	def __del__( self ):
		if self.pl:
			self.pl.PL_halt(0)

	def __scope( self, t ):
		"""split module and term-string:
		t -> module (|'user'), term"""
		tp = t.split( ':' )
		if len( tp ) > 1:
			# specified module name too
			mod = tp[0]
			term = tp[1]
		else:
			mod = 'user'
			term = t
		return (mod, term)

def _test():
	"""Test --------------------------------------------------------
	>>> pleng = PlEngine()
	>>> t = pleng.Term( 3 )
	>>> t[0].pl_term-t[1].pl_term == t[1].pl_term - t[2].pl_term == -1
	True
	>>> ut = pleng.pl
	>>> f = pleng.Functor( 'yoga', 3 )
	>>> #ut( 'PL_atom_chars:->char_p' )( ut('PL_functor_name')(f.pl_functor) )
	#'yoga'
	>>> ut.PL_atom_chars( ut.PL_functor_name(f.pl_functor) )
	'yoga'
	>>> ut('PL_functor_arity')( f.pl_functor )
	3
	>>> t.put([])
	>>> t.is_list()
	True
	>>> t.put( 'yoga' )
	>>> t.is_string()
	True
	>>> t.put( None )
	>>> t.is_variable()
	True
	>>> del t
	>>> a = pleng.Atom( 'hello' )
	>>> t = pleng.Term()
	>>> t.put( a )
	>>> a1 = t.get_atom()
	>>> ut('PL_atom_chars:->char_p')(a1.pl_atom)
	'hello'
	>>> del a
	>>> a = pleng.Atom( u'hello' )
	>>> t.put( a )
	>>> a1 = t.get_atom()
	>>> ut('PL_atom_chars:->char_p')(a1.pl_atom)
	'hello'
	"""
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()

#t.cons_functor( 'animal', 'hello', 20 )
