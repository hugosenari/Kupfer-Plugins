import gi
import ctypes as pyc
from ctypes import pythonapi
from gi.repository import GObject as GO
pyc.cdll.LoadLibrary('libgobject-2.0.so')
lego = pyc.CDLL('libgobject-2.0.so')
lego.g_type_name.restype = pyc.c_char_p
lego.g_type_name.argtypes = (pyc.c_ulonglong,)
pythonapi.PyCapsule_GetName.restype = pyc.c_char_p
pythonapi.PyCapsule_GetName.argtypes = (pyc.py_object,)
pythonapi.PyCapsule_GetPointer.restype = pyc.c_void_p
pythonapi.PyCapsule_GetPointer.argtypes = (pyc.py_object, pyc.c_char_p)

################################################################################
# GObject
################################################################################


class _PyGObject_Functions(pyc.Structure):
    _fields_ = [
        ('pygobject_register_class',
            pyc.PYFUNCTYPE(pyc.c_void_p)),
        ('pygobject_register_wrapper',
            pyc.PYFUNCTYPE(pyc.c_void_p)),
        ('pygobject_lookup_class',
            pyc.PYFUNCTYPE(pyc.c_void_p)),
        ('pygobject_new',
            pyc.PYFUNCTYPE(pyc.py_object, pyc.c_void_p)),
        ]


def capsule_name(capsule):
    return pythonapi.PyCapsule_GetName(capsule)


def capsule_ptr(capsule):
    name = capsule_name(capsule)
    return pythonapi.PyCapsule_GetPointer(capsule, name)


class _PyGO_CAPI(object):
    '''
    Static class to that create PyObject (object) from GObject (pointer)
    '''
    _api = None

    @classmethod    
    def _set_api(cls):
        addr = capsule_ptr(gi._gobject._PyGObject_API)
        cls._api = _PyGObject_Functions.from_address(addr)        

    @classmethod
    def to_object(cls, addr):
        cls._api or cls._set_api()
        return cls._api.pygobject_new(addr)
################################################################################
# GType
################################################################################
INT, ADDRESS, NONE, NOT_IMPLEMENTED = range(4)

G_PY_INT = {
    (GO.TYPE_BOOLEAN,   pyc.c_bool),
    (GO.TYPE_UNICHAR,   pyc.c_ubyte),
    (GO.TYPE_UCHAR,     pyc.c_ubyte),
    (GO.TYPE_CHAR,      pyc.c_char),
    (GO.TYPE_INT,       pyc.c_int),
    (GO.TYPE_UINT,      pyc.c_uint),
    (GO.TYPE_FLAGS,     pyc.c_uint),
}

G_PY_ADDRESS = {
    (GO.TYPE_LONG,      pyc.c_long),
    (GO.TYPE_DOUBLE,    pyc.c_double),
    (GO.TYPE_ULONG,     pyc.c_ulong),
    (GO.TYPE_INT64,     pyc.c_longlong),
    (GO.TYPE_UINT64,    pyc.c_ulonglong),
    (GO.TYPE_ENUM,      pyc.c_ulonglong),
    (GO.TYPE_FLOAT,     pyc.c_float),
    (GO.TYPE_STRING,    pyc.c_char_p),
    (GO.TYPE_POINTER,   pyc.c_void_p),
    (GO.TYPE_OBJECT,    pyc.c_void_p),
    (GO.TYPE_PYOBJECT,  pyc.py_object),
}

G_PY_NONE = {
    (GO.TYPE_NONE,      None),
    (GO.TYPE_INVALID,   None),
}

G_PY_NOT_IMPLEMENTED = {
    (GO.TYPE_PARAM,     None),
    (GO.TYPE_STRV,      None),
    (GO.TYPE_VARIANT,   None),
    (GO.TYPE_BOXED,     None),
    (GO.TYPE_INTERFACE, None),
}

TYPES_G_PY = G_PY_INT | G_PY_ADDRESS | G_PY_NONE | G_PY_NOT_IMPLEMENTED   

TYPES_ID = { hash(gt): (gt, ct, INT) for gt, ct in G_PY_INT }
_u = TYPES_ID.update
_u({ hash(gt): (gt, ct, ADDRESS) for gt, ct in G_PY_ADDRESS })
_u({ hash(gt): (gt, ct, NONE) for gt, ct in G_PY_NONE })
_u({ hash(gt): (gt, ct, NOT_IMPLEMENTED) for gt, ct in G_PY_NOT_IMPLEMENTED })


def gtype_name_of(gtype_id=0):
    '''
    Return a name of gtype if type is a class
    
    this method use glib/gobjec/gtype.c/g_type_name
    see code
    https://github.com/GNOME/glib/blob/master/gobject/gtype.c#L3787
    '''
    name = lego.g_type_name(hash(gtype_id))
    return name and name.decode('utf-8')


def gtype_and_ctype_of(gtype_id=0):
    '''
    return (GType, ctype) of gtype_id
    May return (None, None, NOT_IMPLEMENTED)
    '''
    _default = (None, None, NOT_IMPLEMENTED)
    g_and_c_type = TYPES_ID.get(hash(gtype_id), _default)
    if not g_and_c_type[0]:
        name = gtype_name_of(gtype_id)
        if name:
            gtype = GO.GType.from_name(name)
            parent_id = hash(gtype.parent)
            parent = TYPES_ID.get(parent_id, _default)
            g_and_c_type = (gtype, pyc.c_void_p, parent[2])
    return g_and_c_type


def from_int(value, gtype_id):
    py_value = value
    types = gtype_and_ctype_of(gtype_id)
    gtype, ctype, ctg = types 
    if gtype and ctype:
        if gtype.is_a(GO.TYPE_OBJECT):
            py_value = _PyGO_CAPI.to_object(value)
        elif gtype.is_a(GO.TYPE_GTYPE):
            py_value = gtype
        elif gtype.is_a(GO.TYPE_STRING):
            py_value = ctype(value).value.decode('utf-8')
        elif ctg == INT:
            py_value = ctype(value).value
        elif ctg == ADDRESS:
            py_value = ctype.from_address(value)
    return py_value, gtype, ctype, ctg


def c_to_py(value, gtype_id):
    return from_int(value, gtype_id)[0] 
