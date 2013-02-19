pydependschecker
================

A pure-python dependency graph generator and checker

Checks hierarchical dependency graphs in the form [(int_id, [dependency_int_ids])].

Creates a flattened dependency graph from supplied list of dependencies,
Checks for:
  Circular dependencies,
  Self dependencies,
  Common dependency root (non-dependants),
  Missing (unsatisfied) dependencies.

The resultant graph can then have a mapping
applied (in the form {int_id: objN}) and the resultant graph returned: [obj1:[obj2, obj3], obj1:[obj2, obj5]].

Alternatively you can use the DependencyChecker instance to act as a psudo generator
by using the next(), recycle() and satisfy() methods.
