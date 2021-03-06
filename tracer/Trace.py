# This file was automatically generated by SWIG (http://www.swig.org).
# Version 1.3.33
#
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _Trace
import new
new_instancemethod = new.instancemethod
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'PySwigObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


hat_Open = _Trace.hat_Open
hat_Close = _Trace.hat_Close
hat_Error = _Trace.hat_Error
hat_ErrorExit = _Trace.hat_ErrorExit
hat_ArithmeticError = _Trace.hat_ArithmeticError
hat_Interrupt = _Trace.hat_Interrupt
hat_Abort = _Trace.hat_Abort
hat_OutputTrace = _Trace.hat_OutputTrace
hat_Hidden = _Trace.hat_Hidden
mkRoot = _Trace.mkRoot
mkModule = _Trace.mkModule
mkSrcPos = _Trace.mkSrcPos
mkResApp1 = _Trace.mkResApp1
mkApp1 = _Trace.mkApp1
mkApp2 = _Trace.mkApp2
mkApp3 = _Trace.mkApp3
mkApp4 = _Trace.mkApp4
mkApp5 = _Trace.mkApp5
mkApp6 = _Trace.mkApp6
mkApp7 = _Trace.mkApp7
mkApp8 = _Trace.mkApp8
mkApp9 = _Trace.mkApp9
mkApp10 = _Trace.mkApp10
mkApp11 = _Trace.mkApp11
mkApp12 = _Trace.mkApp12
mkApp13 = _Trace.mkApp13
mkApp14 = _Trace.mkApp14
mkApp15 = _Trace.mkApp15
mkValueApp1 = _Trace.mkValueApp1
mkValueApp2 = _Trace.mkValueApp2
mkValueApp3 = _Trace.mkValueApp3
mkValueApp4 = _Trace.mkValueApp4
mkValueApp5 = _Trace.mkValueApp5
mkValueApp6 = _Trace.mkValueApp6
mkValueApp7 = _Trace.mkValueApp7
mkValueApp8 = _Trace.mkValueApp8
mkValueApp9 = _Trace.mkValueApp9
mkValueApp10 = _Trace.mkValueApp10
mkValueApp11 = _Trace.mkValueApp11
mkValueApp12 = _Trace.mkValueApp12
mkValueApp13 = _Trace.mkValueApp13
mkValueApp14 = _Trace.mkValueApp14
mkValueApp15 = _Trace.mkValueApp15
mkChar = _Trace.mkChar
mkInt = _Trace.mkInt
mkInteger = _Trace.mkInteger
mkRat = _Trace.mkRat
mkRational = _Trace.mkRational
mkFloat = _Trace.mkFloat
mkDouble = _Trace.mkDouble
mkValueUse = _Trace.mkValueUse
mkConstUse = _Trace.mkConstUse
mkConstDef = _Trace.mkConstDef
mkGuard = _Trace.mkGuard
mkCase = _Trace.mkCase
mkIf = _Trace.mkIf
mkFieldUpdate1 = _Trace.mkFieldUpdate1
mkFieldUpdate2 = _Trace.mkFieldUpdate2
mkFieldUpdate3 = _Trace.mkFieldUpdate3
mkFieldUpdate4 = _Trace.mkFieldUpdate4
mkFieldUpdate5 = _Trace.mkFieldUpdate5
mkFieldUpdate6 = _Trace.mkFieldUpdate6
mkFieldUpdate7 = _Trace.mkFieldUpdate7
mkFieldUpdate8 = _Trace.mkFieldUpdate8
mkFieldUpdate9 = _Trace.mkFieldUpdate9
mkFieldUpdate10 = _Trace.mkFieldUpdate10
mkProjection = _Trace.mkProjection
mkHidden = _Trace.mkHidden
mkForward = _Trace.mkForward
mkDoStmt = _Trace.mkDoStmt
mkLambda = _Trace.mkLambda
mkDoLambda = _Trace.mkDoLambda
mkVariable = _Trace.mkVariable
mkConstructor = _Trace.mkConstructor
mkConstructorWFields = _Trace.mkConstructorWFields
mkAbstract = _Trace.mkAbstract
mkListCons = _Trace.mkListCons
recordChild = _Trace.recordChild
entResult = _Trace.entResult
entForward = _Trace.entForward
resResult = _Trace.resResult
resForward = _Trace.resForward
hat_enter = _Trace.hat_enter
hat_reduce = _Trace.hat_reduce
hat_topStack = _Trace.hat_topStack
hat_dumpBuffer = _Trace.hat_dumpBuffer
hat_dumpStack = _Trace.hat_dumpStack


