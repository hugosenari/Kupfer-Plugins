import unittest
import ctypes as pyc
from gi.repository import GObject as GO
from folks.go import _PyGO_CAPI, capsule_ptr, gtype_name_of, \
    gtype_and_ctype_of, c_to_py, INT, ADDRESS


class KillerTofu(GO.GObject):
    __gtype_name__ = "KillerTofu"
    value = 0

    @GO.Property(type=int)
    def prop(self):
        return self.value

    @prop.setter
    def prop(self, value):
        self.value = value
 

class Test_PyGO_CAPI(unittest.TestCase):

    def test_pyobj_from_addr(self):
        py_instance = KillerTofu()
        py_instance.prop = 25
        pypointer = capsule_ptr(py_instance.__gpointer__)
        new_pyinstance = _PyGO_CAPI.to_object(pypointer)
        self.assertEqual(25, new_pyinstance.prop)


class TestGTypeNameOf(unittest.TestCase):
    
    def test_gtype_name_of_my_type(self):
        name = gtype_name_of(KillerTofu.__gtype__)
        self.assertEqual("KillerTofu", name)
        
    def test_gtype_name_of_known_type(self):
        name = gtype_name_of(GO.TYPE_BOOLEAN)
        self.assertEqual("gboolean", name)


class TestGTypeAndCTypeOf(unittest.TestCase):
    
    def test_gtype_and_ctype_of_my_type(self):
        gtype, ctype, ctg = gtype_and_ctype_of(KillerTofu.__gtype__)
        self.assertEqual(KillerTofu.__gtype__, gtype)
        self.assertEqual(pyc.c_void_p, ctype)
        self.assertEqual(ADDRESS, ctg)
        
    def test_gtype_and_ctype_of_known_type(self):
        gtype, ctype, ctg = gtype_and_ctype_of(GO.TYPE_BOOLEAN)
        self.assertEqual(GO.TYPE_BOOLEAN, gtype)
        self.assertEqual(pyc.c_bool, ctype)
        self.assertEqual(INT, ctg)


class TestCToPy(unittest.TestCase):
    
    def test_c_to_py_of_my_type(self):
        py_instance = KillerTofu()
        py_instance.prop = 25
        pypointer = capsule_ptr(py_instance.__gpointer__)
        new_pyinstance = c_to_py(pypointer, KillerTofu.__gtype__)
        self.assertEqual(25, new_pyinstance.prop)
        
    def test_c_to_py_of_false_type(self):
        result = c_to_py(0, GO.TYPE_BOOLEAN)
        self.assertFalse(result)
        
    def test_c_to_py_of_true_type(self):
        result = c_to_py(1, GO.TYPE_BOOLEAN)
        self.assertTrue(result)
        
    def test_c_to_py_of_char_type(self):
        result = c_to_py(ord(b'a'), GO.TYPE_CHAR)
        self.assertEqual(b'a', result)
        
    def test_c_to_py_of_g_type(self):
        result = c_to_py(hash(GO.TYPE_GTYPE), GO.TYPE_GTYPE)
        self.assertEqual(GO.TYPE_GTYPE, result)
        
#     def test_c_to_py_of_str_type(self):
#         char_p = pyc.c_char_p(b'abcd\0')
#         ptr = pyc.addressof(char_p)
#         char_pp = pyc.c_char_p.from_address(ptr)
#         print(ptr, char_p, char_pp, hash(b'abcd\0'))
#         result = c_to_py(ptr, GO.TYPE_STRING)
#         self.assertEqual(b'abcd', result.value)

