"""Call some external (DLL) function via ctypes protocol
"""
from warnings import warn
import ctypes

class Caller:
	"""Utilitary functions. Alternative way to call any functions
	from Prolog dynamic loadable library.
	Arguments are Prolog engine internal data types (like
	term_t, atom_t in SWI-Prolog)
	"""
	def __init__( self, dll, types_table={}, proto_table={}, verbose=False ):
		"""dll is some loaded DLL by ctypes.
		types_table is map like:
		{'xxx_t':POINTER(c_uint), ...}.
		proto_table is map like:
		{'fun1':'int,int->int', ...}.
		If verbose==True when call without prototype will warning
		"""
		_TYPE_CONS = {
		'char':ctypes.c_char,
		'byte':ctypes.c_byte,
		'ubyte':ctypes.c_ubyte,
		'short':ctypes.c_short,
		'ushort':ctypes.c_ushort,
		'int':ctypes.c_int,
		'uint':ctypes.c_uint,
		'long':ctypes.c_long,
		'ulong':ctypes.c_ulong,
		'longlong':ctypes.c_longlong, # for int64 too
		'int64':ctypes.c_longlong,
		'ulonglong':ctypes.c_ulonglong, # for uint64 too
		'uint64':ctypes.c_ulonglong,
		'float':ctypes.c_float,
		'double':ctypes.c_double,
		'void_p':ctypes.c_void_p,
		'char_p':ctypes.c_char_p,
		'int_p':ctypes.POINTER(ctypes.c_int),
		'uint_p':ctypes.POINTER(ctypes.c_uint),
		}

		self.types_table = _TYPE_CONS
		self.types_table.update( types_table )

		self.proto_table = {}
		self.proto_table.update( proto_table )
		self.dll = dll # ctype DLL

		if verbose:
			self.__call_without_prototype = self.__verbose_call_without_prototype
		else:
			self.__call_without_prototype = self.__quiet_call_without_prototype

	def ctype( self, type_name ):
		"""Return ctype constructor for type_name. type_name
		is string, any of 'char', 'byte', etc. and Prolog internal
		types"""
		return self.types_table[type_name]

	def ptr( self, ctype ):
		"""Return C pointer (ctypes.POINTER) for given
		type constructor"""
		return ctypes.POINTER( ctype )

	def __get_fun( self, fun ):
		"""Will call function of dynamic load library.
		fun is string like:
		'something_fun:int,int->float' OR
		'something_fun->int' OR
		'something_fun:int,int' OR
		'something_fun'.

		SPACES NOT ALLOWED!
		"""
		fun = fun.split( ':' )
		funname = fun[0]
		#funname = 'PL_%s'%fun[0]
		proto = fun[1] if len(fun)>1 else ''
		def wrap( *a ):
			"""proto is string like:
			'int,float->int' (return int, expect int and float) OR
			'->int' (return int) OR
			'int,float' (expect int,float).

			SPACES NOT ALLOWED!
			"""
			fun = getattr( self.dll, funname ) # function from library
			if proto:
				# if proto is used, prepare result type and arguments
				synt = proto.split('->')
				restype = synt[1] if len(synt)==2 else None
				argtypes = synt[0]
				# set restype if it was specified
				if restype: restype = self.types_table.get( restype, None )
				# set argtypes if it was specified
				if argtypes:
					argtypes = argtypes.split( ',' )
					argtypes = [self.types_table.get(t,None) for t in argtypes]
					# filtering all None/unknown types!
					if None in argtypes:
						argtypes = None
				# if restype and argtypes True (there aren't invalid types names) -
				# specified to function prototype. It make possible to
				# igore unknown data types
				if restype:
					fun.restype = restype
				if argtypes:
					fun.argtypes = argtypes
			return fun( *a )
		return wrap

	def __call__( self, fun ):
		"""More usuable interfase. Calling like this:
		obj('fun:int,int->int')(2,3) OR
		obj('fun')(2,3)

        NOT USE PROTOYPES TABLE BUT USE TYPES FOR ALL CASTINGS IF fun INCLUDE TYPES INFO!
		"""
		return self.__get_fun( fun )

	def __quiet_call_without_prototype( self, attr ):
		"""Call without warning"""
		return getattr( self.dll, attr )

	def __verbose_call_without_prototype( self, attr ):
		"""Call with warning message"""
		warn( 'Call of \'%s\' without prototype'%attr )
		return getattr( self.dll, attr )

	def __getattr__( self, attr ):
		"""Get implicit attribute which can be function with
		known prototype (see __init__()"""
		if self.proto_table.has_key( attr ):
			proto = self.proto_table[attr]
			if proto:
				fun = '%s:%s'%(attr,self.proto_table[attr])
			else:
				fun = attr
			return self.__get_fun( fun )
		else:
			return self.__call_without_prototype( attr )
