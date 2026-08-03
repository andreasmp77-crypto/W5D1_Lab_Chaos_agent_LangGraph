# W5D1_Lab_Chaos_agent_LangGraph
- Week 5 / Day 1
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-03
---
## Comparison: LangChain chaos agent vs LangGraph structured workflow

In my previous lab, the LangChain agent behaved like a free-thinking assistant: it could decide dynamically which step to take next. Sometimes it called a tool first, sometimes it asked a clarifying question, and sometimes it jumped straight to an answer. This made the system flexible and creative, but the exact order of operations was not predictable. It was also harder to see “what happened under the hood” and to prove that the final answer was correct, because the reasoning path depended on the LLM’s decisions at runtime rather than a fixed process.

In this lab, the LangGraph workflow is deliberately more rigid. I define a structured pipeline up front:
```
intake → validate → investigate → resolve → close
```
with a single conditional branch after validation that can route to a rejection path instead of investigation. The LLM only fills in the content inside each node, but it does not decide the path. This makes the system less “free-form,” but much easier to visualize and trace:

The workflow_path in the shared state shows exactly which nodes ran, in order, for each complaint.

Each node’s outputs (category, validation_passed, investigation_notes, resolution, closure_message) provide a clear chain of thought from input to final result.

This difference matters in real-world contexts like GDPR or regulatory audits: with the structured LangGraph approach, I can prove how a complaint was processed, which checks were applied, and how the final answer was derived. With a more free-form LangChain agent, I get more flexibility but less predictable, less transparent workflows, which makes formal evidence and traceability harder.

---

## Ful Output

Please open output.md or run `python test_visualize.py`

---


## Code or workflow
```
=== Workflow Graph (ASCII) ===
            +-----------+           
            | __start__ |           
            +-----------+           
                  *                 
                  *                 
                  *                 
              +--------+            
              | intake |            
              +--------+            
                  *                 
                  *                 
                  *                 
            +----------+            
            | validate |            
            +----------+            
            ...        ...          
           .              .         
         ..                ...      
+-------------+               .     
| investigate |               .     
+-------------+               .     
        *                     .     
        *                     .     
        *                     .     
  +---------+                 .     
  | resolve |                 .     
  +---------+                 .     
        *                     .     
        *                     .     
        *                     .     
   +-------+            +--------+  
   | close |            | reject |  
   +-------+            +--------+  
            ***        ***          
               *      *             
                **  **              
             +---------+            
             | __end__ |            
             +---------+            
```

## Query, Retrieved or tool evidence, Final output

### Valid complaint

```
Complaint: The Downside Up portal opens at different times each day. How do I predict when?

[INTAKE] Processing complaint...
[INTAKE] Categorized as: portal

[VALIDATION] Validating complaint...
[VALIDATION] Category OK: True, Nonsense: False
[VALIDATION] Passed: True

[INVESTIGATION] Investigating complaint...
[INVESTIGATION] Notes recorded.

[RESOLUTION] Generating resolution...
[RESOLUTION] Resolution generated.

[CLOSURE] Creating closure message...
[CLOSURE] Closure message saved.
Execution path: intake -> validate -> investigate -> resolve -> close

Node outputs:
  [INTAKE]      category:           portal
  [VALIDATION]  validation_passed:  True
  [INVESTIGATE] investigation_notes:
**Investigation Note: Downside Up Portal Opening Times**

**Complaint Overview:**  
A user has reported that the Downside Up portal opens at different times each day and is seeking a way to predict its opening.

**Potential Causes:**  
1. **Scheduled Maintenance:** The portal may be undergoing maintenance or updates that are not consistently scheduled according to a fixed timetable. This could lead to variations in opening times.
   
2. **Server Load and Traffic Management:** The opening times might be influenced by server load or traffic management protocols to optimize performance during peak usage hours. If the system anticipates high traffic, it may delay opening until capacity is better managed.

3. **Time Zone Discrepancies:** Depending on how opening times are communicated (for instance, if they are based on a specific time zone), users may experience variations if they are in different time zones or if there is no clear time zone specified.

4. **Configuration Errors:** There could be configuration settings within the portal system that are not set correctly, causing inconsistencies in the portal’s availability schedule.

**Next Steps:**  
To address the issue, it would be beneficial to check the portal’s maintenance schedule, analyze server traffic patterns, ensure clearcommunication regarding time zones, and review configuration settings for any discrepancies. This analysis will help in understanding the operational fluctuations and potentially lead to a more predictable opening schedule for users.
  [RESOLUTION]  resolution:
To address the concern regarding the inconsistent opening times of the Downside Up portal, we will first review the maintenance schedule to identify any planned downtimes. Additionally, we will monitor server traffic patterns to better understand how these might affectopening times. Finally, we will ensure that the portal communicates its operating hours clearly, including specific time zones, to help users anticipate when the portal will be available. Please stay tuned for updates as we work to implement these measures.
  [CLOSURE/REJECT] status: closed
  [CLOSURE/REJECT] closure_message:
Your complaint regarding the inconsistent opening times of the Downside Up portal has been processed and we are taking steps to ensuremore predictable access in the future.
```

---

### Invalid complaint
```
==============================
Complaint: This is not a valid complaint about something random

[INTAKE] Processing complaint...
[INTAKE] Categorized as: other

[VALIDATION] Validating complaint...
[VALIDATION] Category OK: True, Nonsense: True
[VALIDATION] Passed: False

[REJECT] Complaint rejected by validation.
[REJECT] Closure message recorded.
Execution path: intake -> validate -> reject

Node outputs:
  [INTAKE]      category:           other
  [VALIDATION]  validation_passed:  False
  [INVESTIGATE] investigation_notes:
None
  [RESOLUTION]  resolution:
None
  [CLOSURE/REJECT] status: rejected
  [CLOSURE/REJECT] closure_message:
Your Downside Up complaint could not be processed.

    Complaint: This is not a valid complaint about something random

    Reason: The complaint did not meet validation rules
    (category or coherence). Please check the guidelines
    and submit a clearer, relevant complaint.
```

## Failure or limitation.