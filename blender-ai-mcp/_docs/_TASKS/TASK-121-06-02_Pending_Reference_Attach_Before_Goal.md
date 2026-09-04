# TASK-121-06-02: Pending Reference Attach Before Goal

**Parent:** [TASK-121-06](./TASK-121-06_Guided_Goal_Recovery_And_Reference_Semantics.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

`reference_images(action="attach")` can now stage pending references before an
active goal exists, and the next `router_set_goal(...)` adoption retargets them
onto that goal automatically.
