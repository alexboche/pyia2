'''
A collection of useful functions to use in MSAA clients.

Inspired by pyatspi:
http://live.gnome.org/GAP/PythonATSPI

@author: Eitan Isaacson
@copyright: Copyright (c) 2008, Eitan Isaacson
@license: LGPL

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with this library; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
'''

import constants
from ctypes import windll, oledll, POINTER, byref, c_int
from comtypes.automation import VARIANT
from comtypes.gen.Accessibility import IAccessible
from comtypes import COMError, IServiceProvider
from comtypes.client import GetModule, CreateObject
import comtypesClient

from constants import CHILDID_SELF, \
    UNLOCALIZED_ROLE_NAMES, \
    UNLOCALIZED_STATE_NAMES, \
    UNLOCALIZED_IA2_STATE_NAMES

#a = GetModule("ia2.tlb")
#IServiceProvider=comtypesClient.GetModule('ServProv.tlb').IServiceProvider
IA2Lib=comtypesClient.GetModule('ia2.tlb')
IALib=comtypesClient.GetModule('oleacc.dll').IAccessible

def getDesktop():
  desktop_hwnd = windll.user32.GetDesktopWindow()
  desktop_window = accessibleObjectFromWindow(desktop_hwnd)
  for child in desktop_window:
    if child.accRole() == constants.ROLE_SYSTEM_CLIENT:
      return child
  return None

def getForegroundWindow():
  return accessibleObjectFromWindow(
    windll.user32.GetForegroundWindow())

def accessibleObjectFromWindow(hwnd):
  ptr = POINTER(IAccessible)()
  res = oledll.oleacc.AccessibleObjectFromWindow(
    hwnd,0,
    byref(IAccessible._iid_),byref(ptr))
  return ptr

def accessibleObjectFromEvent(event):
  if not windll.user32.IsWindow(event.hwnd):
    return None
  ptr = POINTER(IAccessible)()
  varChild = VARIANT()
  res = windll.oleacc.AccessibleObjectFromEvent(
    event.hwnd, event.object_id, event.child_id,
    byref(ptr), byref(varChild))
  if res == 0:
    child=varChild.value
#    return normalizeIAccessible(ptr, child)
    return ptr.QueryInterface(IAccessible)
  else:
    return None

def accessible2FromAccessible(pacc, child_id):

    if not isinstance(pacc, IAccessible):
        try:
            pacc = pacc.QueryInterface(IAccessible)
        except COMError:
            raise RuntimeError("%s Not an IAccessible"%pacc)

    if child_id==0 and not isinstance(pacc,IA2Lib.IAccessible2):
        try:
#            print("pacc: " + str(pacc))
            s=pacc.QueryInterface(IServiceProvider)
#            print("S: " + str(s))
#            print("_iid_: " + str(IALib._iid_))
#            print("IAccessible2: " + str(IA2Lib.IAccessible2))
            pacc2=s.QueryService(IALib._iid_, IA2Lib.IAccessible2)
            #newPacc=ctypes.POINTER(IA2Lib.IAccessible2)(i)
            if not pacc2:
    #            print ("IA2: %s"%pacc)
                raise ValueError
            else:
#                print ("Got IA2 object: ", pacc2)
                return pacc2

        except Exception as e:
            pass
            # print "ERROR cannot get IA2 object:", str(e)

    return None

def accessibleTableCellFromAccessible(pacc, child_id):

    if not isinstance(pacc, IAccessible):
        try:
            pacc = pacc.QueryInterface(IAccessible)
        except COMError:
            raise RuntimeError("%s Not an IAccessible"%pacc)

    if child_id==0 and not isinstance(pacc,IA2Lib.IAccessibleTableCell):
        try:
#            print("pacc: " + str(pacc))
            s=pacc.QueryInterface(IServiceProvider)
#            print("S: " + str(s))
#            print("_iid_: " + str(IALib._iid_))
#            print("IAccessible2: " + str(IA2Lib.IAccessible2))
            pacc2=s.QueryService(IALib._iid_, IA2Lib.IAccessibleTableCell)
            #newPacc=ctypes.POINTER(IA2Lib.IAccessible2)(i)
            if not pacc2:
    #            print ("IA2: %s"%pacc)
                raise ValueError
            else:
#                print ("Got IA2 object: ", pacc2)
                return pacc2

        except Exception as e:
            print "ERROR cannot get IA2 Table Cell object:", str(e)

    return None

def accessible2RoleName(pacc2):
    role = pacc2.role()

    if not isinstance(role, int):
            # Maybe one of those Mozilla string roles, just return it.
            return role
    
    return UNLOCALIZED_ROLE_NAMES.get(role, 'unknown')

    return str(pacc2.role())

def accessible2States(pacc2):
    states = pacc2.states

    str = ""
    for item in UNLOCALIZED_IA2_STATE_NAMES:
      if item & states:
        str += UNLOCALIZED_IA2_STATE_NAMES[item] + ' '

    return str


def accessibleRelationFromAccessible2(pacc2):

    if isinstance(pacc2,IA2Lib.IAccessible2):
        out = "Relation info:"
        try:
            out +=  "  Number(" + str(pacc2.nRelations) + ")\n\r "

        except Exception as e:
            print "ERROR cannot get IA2 nRelation:", str(e)

        try:
            for i in range (pacc2.nRelations):
              out +=  "[Type: " + pacc2.relation(i).relationType + "; "
              out +=  "Targets(" + str(pacc2.relation(i).nTargets) + ") "
              for j in range(pacc2.relation(i).nTargets):
                t = pacc2.relation(i).target(j)
                s=t.QueryInterface(IServiceProvider)
                oa2=s.QueryService(IALib._iid_, IA2Lib.IAccessible2)

                out += "'" + str(oa2) + "'"

              out += "]"

            return out

        except Exception as e:
            print "ERROR cannot get IA2 relation:", str(e)

    return "None"    

def findDescendant(acc, pred, breadth_first=False):
  '''
  Searches for a descendant node satisfying the given predicate starting at
  this node. The search is performed in depth-first order by default or
  in breadth first order if breadth_first is True. For example,

  my_win = findDescendant(lambda x: x.name == 'My Window')

  will search all descendants of x until one is located with the name 'My
  Window' or all nodes are exausted. Calls L{_findDescendantDepth} or
  L{_findDescendantBreadth} to start the recursive search.

  @param acc: Root accessible of the search
  @type acc: Accessibility.Accessible
  @param pred: Search predicate returning True if accessible matches the
  search criteria or False otherwise
  @type pred: callable
  @param breadth_first: Search breadth first (True) or depth first (False)?
  @type breadth_first: boolean
  @return: Accessible matching the criteria or None if not found
  @rtype: Accessibility.Accessible or None
  '''
  if breadth_first:
    return _findDescendantBreadth(acc, pred)

  for child in acc:
    try:
      ret = _findDescendantDepth(acc, pred)
    except Exception:
      ret = None
    if ret is not None: return ret

def _findDescendantBreadth(acc, pred):
  '''
  Internal function for locating one descendant. Called by L{findDescendant} to
  start the search.

  @param acc: Root accessible of the search
  @type acc: Accessibility.Accessible
  @param pred: Search predicate returning True if accessible matches the
  search criteria or False otherwise
  @type pred: callable
  @return: Matching node or None to keep searching
  @rtype: Accessibility.Accessible or None
  '''
  for child in acc:
    try:
      if pred(child): return child
    except Exception:
      pass
  for child in acc:
    try:
      ret = _findDescendantBreadth(child, pred)
    except Exception:
      ret = None
    if ret is not None: return ret

def _findDescendantDepth(acc, pred):
  '''
  Internal function for locating one descendant. Called by L{findDescendant} to
  start the search.

  @param acc: Root accessible of the search
  @type acc: Accessibility.Accessible
  @param pred: Search predicate returning True if accessible matches the
  search criteria or False otherwise
  @type pred: callable
  @return: Matching node or None to keep searching
  @rtype: Accessibility.Accessible or None
  '''
  try:
    if pred(acc): return acc
  except Exception:
    pass
  for child in acc:
    try:
      ret = _findDescendantDepth(child, pred)
    except Exception:
      ret = None
    if ret is not None: return ret

def findAllDescendants(acc, pred):
  '''
  Searches for all descendant nodes satisfying the given predicate starting at
  this node. Does an in-order traversal. For example,

  pred = lambda x: x.getRole() == pyatspi.ROLE_PUSH_BUTTON
  buttons = pyatspi.findAllDescendants(node, pred)

  will locate all push button descendants of node.

  @param acc: Root accessible of the search
  @type acc: Accessibility.Accessible
  @param pred: Search predicate returning True if accessible matches the
      search criteria or False otherwise
  @type pred: callable
  @return: All nodes matching the search criteria
  @rtype: list
  '''
  matches = []
  _findAllDescendants(acc, pred, matches)
  return matches

def _findAllDescendants(acc, pred, matches):
  '''
  Internal method for collecting all descendants. Reuses the same matches
  list so a new one does not need to be built on each recursive step.
  '''
  for child in acc:
    try:
      if pred(child): matches.append(child)
    except Exception:
      pass
    _findAllDescendants(child, pred, matches)

def findAncestor(acc, pred):
    if acc is None:
        # guard against bad start condition
        return None
    while 1:
        try:
            parent = acc.accParent.QueryInterface(IAccessible)
        except:
            parent = None
        if parent is None:
            # stop if there is no parent and we haven't returned yet
            return None
        try:
            if pred(parent): return parent
        except Exception:
            pass
        # move to the parent
        acc = parent

def printSubtree(acc, indent=0):
  print '%s%s' % (indent*' ', unicode(acc).encode('cp1252', 'ignore'))
  for child in acc:
    try:
      printSubtree(child, indent+1)
    except:
      pass

def windowFromAccessibleObject(acc):
  hwnd = c_int()
  try:
    res = windll.oleacc.WindowFromAccessibleObject(acc, byref(hwnd))
  except:
    res = 0
  if res == 0:
    return hwnd.value
  else:
    return 0

def getWindowThreadProcessID(hwnd):
  processID = c_int()
  threadID = windll.user32.GetWindowThreadProcessId(hwnd,byref(processID))
  return (processID.value, threadID)

def getAccessibleThreadProcessID(acc):
  hwnd = windowFromAccessibleObject(acc)
  return getWindowThreadProcessID(hwnd)
