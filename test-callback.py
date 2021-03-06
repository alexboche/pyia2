import pyia2
from pyia2.constants import CHILDID_SELF, \
    UNLOCALIZED_ROLE_NAMES, \
    UNLOCALIZED_STATE_NAMES
from pyia2.utils import IA2Lib

def event_cb(event):
#    print(event)
    ao = pyia2.accessibleObjectFromEvent(event)
    print("\nMSAA ROLE: " + ao.accRoleName())

    try:
        print("NAME: " + ao.accName(CHILDID_SELF))
    except:
        print("NAME: undefined")

    try:
        print("VALUE: " + ao.accValue(CHILDID_SELF))
    except:
        print("VALUE: undefined")

    try:
        print("DESCRIPTION: " + ao.accDescription(CHILDID_SELF))
    except:
        print("DESCRITPION: undefined")

    try:
        print("PARENT: " + str(ao.accParent))
    except:
        print("PARENT: undefined")

    try:
        print("CHILD: " + str(ao.accChild(0)))
    except:
        print("CHILD: undefined")

    try:
        print("CHILD COUNT: " + str(ao.accChildCount))
    except:
        print("CHILD COUNT: undefined")

    try:
        print("LAST CHILD: " + str(ao.accChild(ao.accChildCount-1)))
    except:
        print("LAST CHILD: undefined")

    try:
        print("MSAA STATE: " + str(ao.accState(CHILDID_SELF)))
    except:
        print("MSAA STATE: undefined")

    try:
        print("MSAA STATE(SET): " + str(ao.accStateSet(CHILDID_SELF)))
    except:
        print("MSAA STATE(SET): undefined")

    try:
        print("MSAA ROWINDEX: " + str(ao.rowindex))
    except:
        print("MSAA ROWINDEX: undefined")



    ao2 = pyia2.accessible2FromAccessible(ao, CHILDID_SELF)
    if isinstance(ao2, IA2Lib.IAccessible2):
#        print("IAccessible2 Values: %s"%ao)

        print('\n---- IAccessibleTableCell -----')

        try:
            ia2_role = str(ao2.role())
            print("IA2 ROLE(int): " + ia2_role);
        except:
            print("IA2 ROLE(int): undefined")

        try:
            ia2_role = pyia2.accessible2RoleName(ao2)
            print("IA2 ROLE: " + ia2_role);
        except:
            print("IA2 ROLE: undefined")

        try:
            print("IA2 STATES(bits): " + str(ao2.states))
        except:
            print("IA2 STATES(bits): undefined")

        try:
            print("IA2 STATES: " + pyia2.accessible2States(ao2))
        except:
            print("IA2 STATES: undefined")

        try:
            y = pyia2.accessibleRelationFromAccessible2(ao2)
            print("IA2 RELATIONS: " + str(y))
        except:
            print("IA2 RELATIONS: undefined")

        try:
            print("UNIQUE ID: " + str(ao2.uniqueID))
        except:
            print("UNIQUE ID: undefined")

        try:
            print("ATTRIBUTES: " + str(ao2.attributes))
        except:
            print("ATTRIBUTES: undefined")

        try:
            print("GROUP POSITION: " + str(ao2.groupPosition))
        except:
            print("GROUP POSITION: undefined")

    aot = pyia2.accessibleTableCellFromAccessible(ao, CHILDID_SELF)
    if isinstance(aot, IA2Lib.IAccessibleTableCell):

        print('\n---- IAccessibleTableCell -----')
        try:
            print("IA2 ROWINDEX: " + str(aot.rowIndex))
        except:
            print("IA2 ROWINDEX: undefined")

        try:
            print("IA2 COLINDEX: " + str(aot.columnIndex))
        except:
            print("IA2 COLINDEX: undefined")

        try:
            print("IA2 ISSELECTED: " + str(aot.isSelected()))
        except:
            print("IA2 ISSELECTED: undefined")

    else:
        print "Not IA2 Object"


print("This program monitors document and focus changes events for MSAA and IAccessible2 and provides information about the event.")
event_id = pyia2.IA2_EVENT_DOCUMENT_LOAD_COMPLETE
pyia2.Registry.registerEventListener(event_cb, event_id )

event_id = pyia2.EVENT_OBJECT_FOCUS
pyia2.Registry.registerEventListener(event_cb, event_id )

pyia2.Registry.start()
