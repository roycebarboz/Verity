# Verity

Verity triages customer support tickets for CloudOps Inc.: it classifies each ticket, retrieves knowledge-base content, drafts a grounded reply, verifies it, and decides whether to send, escalate, or ask for more information.

## Language

### Tickets

**Ticket complexity**:
The Bouncer's judgement of whether a ticket is a **Simple ticket** or a **Complex ticket**; it decides how many **Retrieval queries** the Librarian writes.
_Avoid_: difficulty, hardness

**Simple ticket**:
A ticket whose answer draws on a single knowledge-base topic, so it gets exactly one **Retrieval query**.

**Complex ticket**:
A ticket whose answer draws on more than one knowledge-base topic, even if the customer only asked one thing, so it gets two or three **Sub-queries**.
_Avoid_: multi-question ticket

### Retrieval

**Retrieval query**:
A search phrase the Librarian writes from a ticket, in documentation language, to look up **Chunks**.
_Avoid_: search query, rewrite

**Sub-query**:
One of several **Retrieval queries** written for a **Complex ticket**, each covering a distinct part of the ticket.

**Chunk**:
A piece of a knowledge-base document that is stored and retrieved as a single unit, tagged with its source document and position.
_Avoid_: passage, snippet

**Fair merge**:
Combining each **Sub-query**'s ranked **Chunks** into the final set by taking turns, rank by rank, so every part of a **Complex ticket** is represented.
_Avoid_: flatten, fusion, merge by score

**Rerank**:
Rescoring the **Chunks** found for a **Retrieval query** against that same query, using a model that reads the query and the chunk together.
