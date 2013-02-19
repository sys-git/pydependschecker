pydependschecker
================

A pure-python dependency graph generator and checker

Checks hierarchical dependency graphs in the form [(int_id, [dependency_int_ids])].

Creates a dependency graph from supplied list of dependencies, checks for circular and self dependencies, checks for
common dependency root (non-dependants), checks for missing dependencies. The resultant graph can then have a mapping
applied (in the form {int_id: objN}) and the resultant graph returned: [obj1:[obj2, obj3], obj4:[obj5]].
