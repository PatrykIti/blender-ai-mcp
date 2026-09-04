# TASK-121-06-04: Explicit Workflow Rejection Into Guided Manual Build

**Parent:** [TASK-121-06](./TASK-121-06_Guided_Goal_Recovery_And_Reference_Semantics.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

Model-facing `workflow_confirmation` can now explicitly decline a workflow and
continue into `guided_manual_build` instead of forcing the model to improvise
invalid confirmation strings.
