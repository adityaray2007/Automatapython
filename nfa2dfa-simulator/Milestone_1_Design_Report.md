# Course Project Design Report — Milestone 1 (M1)

**Evaluation Phase**: Milestone 1 (M1) — Problem Analysis & Project Design (Total: 5 Marks)  
**Evaluation Window**: 2–6 November 2026  
**Academic Course**: Automata Theory & Formal Languages  

---

## Team & Project Metadata

| Field | Details / Student Input |
|---|---|
| **Project Topic & Title** | **Topic 1: NFA → DFA Conversion Simulator (“Subset Lab”)** |
| **Project / Team ID** | `[ _________________________________________________ ]` |
| **Team Member 1 (Lead)** | **Aditya Ray** &nbsp;&nbsp;\|&nbsp;&nbsp; Enrollment No: `[ _________________________ ]` |
| **Team Member 2** | `[ _________________________ ]` &nbsp;&nbsp;\|&nbsp;&nbsp; Enrollment No: `[ _________________________ ]` |
| **Team Member 3** | `[ _________________________ ]` &nbsp;&nbsp;\|&nbsp;&nbsp; Enrollment No: `[ _________________________ ]` |
| **Team Member 4** | `[ _________________________ ]` &nbsp;&nbsp;\|&nbsp;&nbsp; Enrollment No: `[ _________________________ ]` |

---

## Milestone 1 Evaluation Rubric Alignment

| Criterion | Marks | Deliverable & Section Reference |
|---|:---:|---|
| **Problem Definition & Automata Specification** | **1 Mark** | Problem statement, primary/secondary objectives, formal I/O, and mathematical 5-tuple specification (Section 1). |
| **Existing Tools & Feasibility Analysis** | **1 Mark** | Review of existing tools (JFLAP, Automata-lib), limitations, and multi-domain feasibility analysis (Section 2). |
| **Simulator Design & Methodology** | **2 Marks** | Decoupled architecture, system flowchart, module responsibilities, UI wireframe mock-up, and IPO model (Section 3). |
| **Algorithm Selection & Correctness** | **1 Mark** | Rabin-Scott subset construction algorithm, structured pseudocode, and manually solved validation example (Section 4). |
| **TOTAL** | **5 Marks** | **All M1 deliverables comprehensively fulfilled.** |

---

## 1. Problem Definition & Automata Specification (Criterion 1 — 1 Mark)

### 1.1 Problem Statement
Non-Deterministic Finite Automata (NFAs) offer an elegant theoretical mechanism for recognizing regular languages, permitting concurrent multi-path branching and dead-end transitions. However, physical computer architectures, lexical analyzers, and runtime pattern matchers are deterministic systems that cannot pursue multiple execution paths simultaneously. Therefore, every NFA must be converted into an equivalent Deterministic Finite Automaton (DFA).

In academic computer science curricula, the **Subset Construction** (Rabin-Scott powerset construction) algorithm is the foundational bridge between non-deterministic models and deterministic computation. However, students consistently encounter steep learning barriers:
1. **Mental Model Confusion**: Struggling to conceptualize how a single DFA state represents a composite set of NFA states.
2. **State Blowup Visualization**: Failing to predict or track exponential state growth (up to $2^n$ states for an $n$-state NFA).
3. **The Dead/Trap State ($\emptyset$)**: Difficulty understanding why an explicit empty-set trap state is mathematically required to ensure a total transition function.
4. **Equivalence Verification**: Inability to verify whether the constructed DFA accepts the exact same language as the original NFA.

Existing academic software tools frequently execute this conversion as a black-box operation, depriving learners of the incremental, step-by-step mathematical union derivation required for viva examinations.

### 1.2 Project Objectives
The objective of this project is to design and develop **“Subset Lab”**, a specialized Python-based interactive visual simulator for **Topic 1: NFA → DFA Conversion**.
- **Interactive Step Playback**: Provide fine-grained controls (Reset, Step Prev, Step Next, Auto-Play) displaying the exact union calculation at each step.
- **Dual-Machine Simultaneous Tracing**: Simulate user-provided strings concurrently across both machines, demonstrating language equivalence via live frontier tracking and agreement badges.
- **Viva-Focused Architectural Purity**: Isolate all automata logic in a pure-Python package (`algorithm/`) with beginner-friendly English comments and zero UI dependencies, enabling students to explain every line during viva defense.
- **Zero Heavy Install Footprint**: Synthesize Graphviz DOT diagrams rendered client-side by modern browsers without requiring native C-binaries or cloud backend services.

### 1.3 System Inputs & Outputs
- **Inputs**:
  - State Set $Q$: Comma-separated list of alphanumeric state identifiers ($|Q| \le 12$).
  - Alphabet $\Sigma$: Comma-separated list of single-character tokens ($\forall a \in \Sigma, |a| = 1; a \notin \{\epsilon, \text{eps}, \lambda\}$).
  - Start State $q_0$: Exactly one initial state from $Q$.
  - Accepting States $F$: Subset of states $F \subseteq Q$.
  - Transition Matrix $\delta_{NFA}$: Target state mappings for each $(q, a) \in Q \times \Sigma$ via multi-select or text.
  - Test Strings $w$: Arbitrary single strings or multi-line batch test suites.
- **Outputs**:
  - Converted DFA: Canonical 5-tuple $(Q_{DFA}, \Sigma, \delta_{DFA}, q_{0,DFA}, F_{DFA})$ with alphabetical aliases ($A, B, C\dots$).
  - Transition Matrices: Dynamic NFA matrix and total DFA matrix with subset membership mappings.
  - Visual State Diagrams: Responsive Graphviz diagrams featuring start arrows, double-circle accepting states, and subset highlight glows.
  - Construction Step Log: Chronological natural language log explaining $\delta(q, a)$ moves and subset unions.
  - Verification Report: Step-by-step state traces and automated agreement validation.

### 1.4 Formal Mathematical Specification
- **Input NFA 5-Tuple**:
  $$M_{NFA} = (Q, \Sigma, \delta, q_0, F)$$
  1. $Q$: Finite set of states, $|Q| \le 12$.
  2. $\Sigma$: Finite alphabet, single characters, strictly excluding $\epsilon$.
  3. $\delta: Q \times \Sigma \to \mathcal{P}(Q)$: Transition function. $\delta(q, a) = \emptyset$ denotes absence of transition.
  4. $q_0 \in Q$: Initial start state.
  5. $F \subseteq Q$: Final/accepting states.

- **Output DFA 5-Tuple**:
  $$M_{DFA} = (Q', \Sigma, \delta', q_0', F')$$
  1. $Q' \subseteq \mathcal{P}(Q)$: Set of reachable subsets of $Q$ ($|Q'| \le 2^{|Q|}$).
  2. $\Sigma$: Identical input alphabet.
  3. $q_0' = \{q_0\}$: DFA initial state (singleton set containing NFA start state).
  4. $\delta': Q' \times \Sigma \to Q'$: Total deterministic transition function defined by:
     $$\delta'(S, a) = \bigcup_{q \in S} \delta(q, a) \quad \forall S \in Q', a \in \Sigma$$
     If $\bigcup_{q \in S} \delta(q, a) = \emptyset$, $\delta'(S, a) = \emptyset$ (the explicit dead/trap state).
  5. $F' = \{S \in Q' \mid S \cap F \neq \emptyset\}$: A DFA subset state is accepting if and only if it contains at least one NFA accepting state.

- **Language Equivalence Guarantee**:
  By structural induction on string length $|w|$, $\hat{\delta}'(q_0', w) = \hat{\delta}(q_0, w)$. Thus, $w \in L(M_{DFA}) \iff \hat{\delta}'(q_0', w) \cap F \neq \emptyset \iff w \in L(M_{NFA})$.

---

## 2. Existing Tools & Feasibility Analysis (Criterion 2 — 1 Mark)

### 2.1 Review of Existing Tools
1. **JFLAP (Duke University)**:
   - *Strengths*: Comprehensive coverage of automata, grammars, and Turing machines.
   - *Limitations*: Heavy Java Swing desktop application requiring JRE installation; suffers from high-DPI scaling bugs; graph layout requires cumbersome manual dragging; conversion output is dense and lacks natural language explanations.
2. **Computational Automata Libraries (Automata-lib, FAdo)**:
   - *Strengths*: High algorithmic performance, programmatic manipulation.
   - *Limitations*: CLI-only developer packages with zero graphical user interface; conversions execute as instantaneous batch processes without intermediate step visibility.
3. **Web-Based FSM Simulators (FSM Simulator, Cyberzhg)**:
   - *Strengths*: Web-accessible, quick prototyping.
   - *Limitations*: Often merge $\epsilon$-NFA, DFA minimization, and regex into cluttered interfaces; lack structured input validation; do not support dual simultaneous execution or side-by-side agreement testing.

### 2.2 Feature Comparison Matrix

| Feature | JFLAP | Automata-lib | Online FSM Tools | Proposed Subset Lab |
|---|:---:|:---:|:---:|:---:|
| **Platform / Runtime** | Java JRE Desktop | Python CLI | Web JS | **Zero-Install Python + Browser** |
| **Interactive Step Playback** | Clunky | None | None | **Full (Reset, Prev, Play, Next)** |
| **Side-by-Side NFA & DFA** | No (separate windows) | No | No | **Yes (Horizontal 50/50 View)** |
| **Step-by-Step Union Derivations** | Raw matrix only | None | None | **Yes (Natural Language Cards)** |
| **Dual Trace Language Agreement** | No | No | No | **Yes (Frontier Logging & Badge)** |
| **Viva-Ready Pure Codebase** | Complex Java | Library code | Complex JS | **100% Pure Python (`algorithm/`)** |

### 2.3 Multi-Domain Feasibility Analysis
- **Technical Feasibility**: Fully feasible. The system leverages Python ≥ 3.10 and Streamlit ≥ 1.40. Graphviz DOT code is parsed and rendered client-side by the browser via `st.graphviz_chart()`, completely eliminating native Graphviz binaries or C-library dependencies.
- **Pedagogical Feasibility**: Highly feasible. Includes 5 verified textbook presets covering edge cases (such as the 8-state blow-up for "3rd symbol from end is a" and the dead-state trap $\emptyset$). The strict separation of automata math in `algorithm/` gives students confidence in reading and defending the code.
- **Economic Feasibility**: Zero cost. 100% open-source libraries run locally on standard hardware without hosting, cloud GPU, or database fees.

---

## 3. Simulator Design & Methodology (Criterion 3 — 2 Marks)

### 3.1 System Architecture
The simulator enforces strict decoupling between pure computation and interactive presentation:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER (ui/, app.py)                   │
│   • Streamlit Reactive UI Controller (Session State Management)        │
│   • Graphviz DOT Diagram Synthesis with Radial Gradients (graphs.py)   │
│   • Modern Glassmorphism CSS with Aurora Animation (styles.py)         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Calls (Data Only)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  PURE COMPUTATIONAL LOGIC (algorithm/)                 │
│   • models.py: Dataclasses (NFA, DFA, DFAState, ConstructionStep)       │
│   • validate.py: Input Sanitization, Bounds Checking & Error Reporting │
│   • subset_construction.py: BFS Queue Exploration & Alias Mapping      │
│   • simulate.py: Dual-Machine Trace Execution & Frontier Logging       │
│   • explain.py: Natural Language Mathematical Translation              │
│   • examples.py: 5 Verified Textbook Preset Automata                   │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Modular Component Breakdown

| Module | Layer | Primary Responsibilities |
|---|---|---|
| `algorithm/models.py` | Pure Logic | Holds clean dataclasses for NFAs, DFAs, states, moves, and conversion results. |
| `algorithm/validate.py` | Pure Logic | Validates raw user text into typed NFA objects; strictly rejects $\epsilon$-tokens. |
| `algorithm/subset_construction.py` | Pure Logic | Implements the core BFS powerset algorithm, alias assignment, and dead-state creation. |
| `algorithm/simulate.py` | Pure Logic | Simulates strings on DFA and logs active NFA frontiers to verify agreement. |
| `algorithm/explain.py` | Pure Logic | Converts raw ConstructionStep transitions into clear English mathematical sentences. |
| `algorithm/examples.py` | Pure Logic | Supplies 5 verified textbook reference NFAs with documented acceptance verdicts. |
| `algorithm/demo.py` | Pure Logic | Terminal runner (`python -m algorithm.demo`) for viva demonstrations without UI. |
| `ui/graphs.py` | UI Support | Synthesizes Graphviz DOT code with start arrows, double circles, and highlight glows. |
| `ui/styles.py` | UI Support | Implements responsive glassmorphism theme, card borders, and table scrolling. |
| `app.py` | UI Controller | Streamlit reactive frontend binding widgets, diagrams, tables, and step controls. |

### 3.3 System Processing Flowchart

```
 [User Input / Preset Chooser]
              │
              ▼
   ┌──────────────────────────────────────────────┐
   │  Input Validation (algorithm/validate.py)    │ ───► Invalid ──► [Display Error Badges]
   └──────────────────────────────────────────────┘
              │ Valid NFA
              ▼
   ┌──────────────────────────────────────────────┐
   │  Live NFA Diagram Synthesis (ui/graphs.py)   │ ───► [Render Live NFA State Machine]
   └──────────────────────────────────────────────┘
              │ Click 'Convert to DFA'
              ▼
   ┌────────────────────────────────────────────────────────┐
   │  Subset Construction Engine (subset_construction.py)   │
   │  1. S₀ = RegisterState(Normalize([q₀])), Enqueue S₀     │
   │  2. While Queue not empty:                             │
   │        Current = Queue.pop_left()                      │
   │        For each a ∈ Σ:                                 │
   │            T = ⋃ δ(q, a) for q ∈ Current.members       │
   │            Target = RegisterState(T)                   │
   │            If Target is new: Enqueue Target            │
   │            Record DFA Edge: Current ──a──► Target      │
   │            Log ConstructionStep & Union details        │
   └────────────────────────────────────────────────────────┘
              │
              ├────────────────────────────────────────┬────────────────────────────────────────┐
              ▼                                        ▼                                        ▼
   [DFA Graph Generator]                   [Step Player Controller]                 [Dual Simulation Engine]
   Renders DFA diagram with                Steps slider (0..N),                     Executes strings on DFA
   focus highlights & path trace           advances graph & step log                & NFA; verifies agreement
```

### 3.4 UI Wireframe & Spatial Orientation Mock-up

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  HEADER: Brand Title 'Subset Lab' | Tagline 'Watch an NFA collapse into a DFA.'                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SECTION 1: NFA MASTER CONFIGURATION DECK (Balanced 2-Column Card)                                   │
│  ┌─────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐  │
│  │ Choose Preset NFA Dropdown              │  │ Transition Table δ(state, symbol)                │  │
│  │ [Convert to DFA]   [Reset to Preset]    │  │ Entry Mode: [🔘 Multi-Select | ⚪ Text Input]     │  │
│  │ States Input    | Alphabet Input        │  │ State   | a                | b                   │  │
│  │ Start State     | Accepting Multiselect │  │ q0      | [q0 x, q1 x]     | [q0 x]              │  │
│  └─────────────────────────────────────────┘  └──────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SECTION 2: AUTOMATA SHOWCASE (Side-by-Side Horizontal Parity 50% / 50%)                             │
│  ┌─────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐  │
│  │ 📡 NFA State Diagram                    │  │ 🕸 DFA State Diagram & Construction              │  │
│  │ Inspect DFA State Dropdown (Glow)       │  │ Download DFA (JSON) Button                       │  │
│  │ [Live Graphviz Diagram with Top Margin] │  │ [Live DFA Diagram with Active Edge Focus]        │  │
│  │ Start Arrow, Teal Double Circles        │  │ ⏯ Step Player: [⏮][◀][▶ Play][Next ▶]   [3 / 6] │  │
│  │                                         │  │ Step Slider: ━━━━━●━━━━━━━━━                     │  │
│  │                                         │  │ Construction Log: Step 1: δ(q0,a) ... -> NEW B   │  │
│  └─────────────────────────────────────────┘  └──────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SECTION 3: TRANSITION TABLES (50% / 50%)                                                            │
│  ┌─────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐  │
│  │ 📋 NFA Transition Table                 │  │ 📊 DFA Transition Table (Alias = Subset Mapping) │  │
│  │ State | a        | b                    │  │ State       | a            | b        | Accept?  │  │
│  │ → q0  | q0, q1   | q0                   │  │ → A = {q0}  | B {q0,q1}    | A {q0}   |          │  │
│  └─────────────────────────────────────────┘  └──────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SECTION 4: VERIFICATION & TESTING SUITE (50% / 50%)                                                 │
│  ┌─────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐  │
│  │ 🧪 Single String Verification           │  │ 📑 Batch Test Suite                              │  │
│  │ Input String: [ aab ] [Run Test]        │  │ Batch Strings Textarea (<empty> supported)       │  │
│  │ Verdict Badge: [Accepted]               │  │ [Run Batch Test]                                 │  │
│  │ Agreement Badge: [NFA and DFA agree ✓]  │  │ Batch Table: String | Verdict | Final DFA State  │  │
│  │ Trace Table: Step | Symbol | DFA | NFA  │  │                                                  │  │
│  └─────────────────────────────────────────┘  └──────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.5 Input-Processing-Output (IPO) Workflow Model

| Phase | Input Components | Processing Activities | Output Deliverables |
|---|---|---|---|
| **Input Phase** | Form inputs or Preset selection | String splitting, deduplication, $\epsilon$-token filtering, bounds checks | Validated `NFA` dataclass object or error list |
| **Conversion Phase** | Validated `NFA` dataclass | Powerset BFS exploration, subset normalization, alias assignment ($A, B\dots$), dead state creation | `ConversionResult` (`DFA` + ordered `ConstructionStep` list) |
| **Visualization Phase** | `NFA`, `ConversionResult`, inspected state | DOT string construction with radial fills, double circles, and edge merging | Interactive browser-rendered SVG diagrams |
| **Simulation Phase** | Verification strings $w \in \Sigma^*$ | DFA single-state path traversal; NFA active frontier set accumulation | Verdicts, trace tables, agreement badges |

---

## 4. Algorithm Selection & Correctness (Criterion 4 — 1 Mark)

### 4.1 Algorithm Selection & Justification
The Rabin-Scott Powerset / Subset Construction (Breadth-First Search variant) is selected as the primary algorithmic engine. It is mathematically optimal for educational purposes because:
1. **Reachability Pruning**: Only subsets reachable from $q_0$ are explored, avoiding the construction of useless unreachable subsets.
2. **Deterministic Canonical Ordering**: By indexing NFA states in declaration order, all subsets (e.g. $\{q_0, q_1\}$) are normalized deterministically, ensuring that aliases ($A, B, C\dots$) are completely repeatable across runs.
3. **Total Function Guarantee**: When a state has no outgoing transition on a symbol, the empty set $\emptyset$ is materialized as an explicit dead/trap state, ensuring compliance with the formal DFA definition.

### 4.2 Structured Algorithmic Pseudocode

```python
Algorithm: SubsetConstruction(NFA M = (Q, Σ, δ, q₀, F))
Returns:   DFA M' = (Q', Σ, δ', q₀', F'), StepsLog

1.   OrderMap = {state: index for index, state in enumerate(M.states)}
2.   function Normalize(states):
3.       return sorted(unique(states), key=lambda s: OrderMap[s])
4.
5.   function SetID(members):
6.       if len(members) == 0: return "∅"
7.       return "{" + join(members, ",") + "}"
8.
9.   Known = {}             // Map of SetID -> DFAState
10.  DFAStates = []         // Ordered list of discovered DFA states
11.  DFATransitions = {}    // Map of from_id -> {symbol -> target_id}
12.  StepsLog = []          // Construction step audit log
13.
14.  function Register(members):
15.      sid = SetID(members)
16.      if sid in Known: return Known[sid]
17.      alias = AliasFor(len(DFAStates))   // 0->A, 1->B, 25->Z, 26->A1...
18.      is_accepting = any(m in M.accepts for m in members)
19.      is_dead = (len(members) == 0)
20.      state = DFAState(id=sid, alias=alias, members=members, is_accepting, is_dead)
21.      Known[sid] = state
22.      DFAStates.append(state)
23.      DFATransitions[sid] = {}
24.      return state
25.
26.  // Step 1: Start state initialization
27.  start_state = Register(Normalize([M.start]))
28.  start_state.is_start = True
29.  Queue = FIFOQueue([start_state])
30.
31.  // Step 2: Breadth-first exploration
32.  while Queue is not empty:
33.      Current = Queue.pop_left()
34.      for each symbol in M.alphabet:
35.          moves = []
36.          for q in Current.members:
37.              targets = Normalize(M.transitions.get(q, {}).get(symbol, []))
38.              moves.append(MoveDetail(state=q, targets=targets))
39.          
40.          // Compute Union: T = ⋃ δ(q, symbol)
41.          result_members = Normalize(union of all move.targets)
42.          seen_count = len(Known)
43.          target_state = Register(result_members)
44.          is_new = (len(Known) > seen_count)
45.          if is_new:
46.              Queue.push(target_state)
47.          
48.          DFATransitions[Current.id][symbol] = target_state.id
49.          StepsLog.append(ConstructionStep(Current, symbol, moves, result_members, target_state, is_new))
50.
51.  dfa = DFA(alphabet=M.alphabet, states=DFAStates, transitions=DFATransitions,
52.            start=start_state.id, accepts=[s.id for s in DFAStates if s.is_accepting])
53.  return dfa, StepsLog
```

### 4.3 Manually Solved Validation Example (Ends with "ab")
To verify correctness, the algorithm is manually calculated on the classic textbook problem:
- **Problem**: Construct an equivalent DFA for the NFA recognizing all strings over $\Sigma = \{a, b\}$ ending in `"ab"`.
- **NFA Formal Definition**:
  - $Q = \{q_0, q_1, q_2\}$
  - $\Sigma = \{a, b\}$
  - $q_0 = q_0$
  - $F = \{q_2\}$
  - Transitions: $\delta(q_0, a) = \{q_0, q_1\}$, $\delta(q_0, b) = \{q_0\}$, $\delta(q_1, b) = \{q_2\}$; all other transitions are $\emptyset$.

#### Step-by-Step Manual Construction Trace Table

| Step # | Current DFA State $S$ | Symbol $a$ | Individual Moves $\delta(q, a)$ | Computed Union $T$ | Resulting State & Status |
|:---:|:---:|:---:|---|:---:|---|
| **1** | $A = \{q_0\}$ | $a$ | $\delta(q_0, a) = \{q_0, q_1\}$ | $\{q_0, q_1\}$ | **NEW State $B$** |
| **2** | $A = \{q_0\}$ | $b$ | $\delta(q_0, b) = \{q_0\}$ | $\{q_0\}$ | **Existing State $A$** |
| **3** | $B = \{q_0, q_1\}$ | $a$ | $\delta(q_0, a) = \{q_0, q_1\}, \delta(q_1, a) = \emptyset$ | $\{q_0, q_1\}$ | **Existing State $B$** |
| **4** | $B = \{q_0, q_1\}$ | $b$ | $\delta(q_0, b) = \{q_0\}, \delta(q_1, b) = \{q_2\}$ | $\{q_0, q_2\}$ | **NEW State $C$ (Accepting\*)** |
| **5** | $C = \{q_0, q_2\}$ | $a$ | $\delta(q_0, a) = \{q_0, q_1\}, \delta(q_2, a) = \emptyset$ | $\{q_0, q_1\}$ | **Existing State $B$** |
| **6** | $C = \{q_0, q_2\}$ | $b$ | $\delta(q_0, b) = \{q_0\}, \delta(q_2, b) = \emptyset$ | $\{q_0\}$ | **Existing State $A$** |

#### Resulting DFA Transition Matrix

| DFA State | Subset Members | on Input $a$ | on Input $b$ | Accepting Status |
|:---:|:---:|:---:|:---:|:---:|
| $\rightarrow A$ (Start) | $\{q_0\}$ | $B\ \{q_0, q_1\}$ | $A\ \{q_0\}$ | Non-Accepting |
| $B$ | $\{q_0, q_1\}$ | $B\ \{q_0, q_1\}$ | $C\ \{q_0, q_2\}$ | Non-Accepting |
| $* C$ (Accepting) | $\{q_0, q_2\}$ | $B\ \{q_0, q_1\}$ | $A\ \{q_0\}$ | **Accepting ($q_2 \in C$)** |

#### Manual String Verification & Dual-Machine Language Agreement
- **Test String `ab`**:
  - DFA Path: $A \xrightarrow{a} B \xrightarrow{b} C$ (Accepting) $\implies$ **ACCEPTED**
  - NFA Frontier: $[q_0] \xrightarrow{a} [q_0, q_1] \xrightarrow{b} [q_0, q_2]$ (contains $q_2$) $\implies$ **ACCEPTED**
  - **Verdict**: NFA and DFA agree $\checkmark$
- **Test String `aab`**:
  - DFA Path: $A \xrightarrow{a} B \xrightarrow{a} B \xrightarrow{b} C$ (Accepting) $\implies$ **ACCEPTED**
  - NFA Frontier: $[q_0] \xrightarrow{a} [q_0, q_1] \xrightarrow{a} [q_0, q_1] \xrightarrow{b} [q_0, q_2]$ $\implies$ **ACCEPTED**
  - **Verdict**: NFA and DFA agree $\checkmark$
- **Test String `abb`**:
  - DFA Path: $A \xrightarrow{a} B \xrightarrow{b} C \xrightarrow{b} A$ (Non-accepting) $\implies$ **REJECTED**
  - NFA Frontier: $[q_0] \xrightarrow{a} [q_0, q_1] \xrightarrow{b} [q_0, q_2] \xrightarrow{b} [q_0]$ (no $q_2$) $\implies$ **REJECTED**
  - **Verdict**: NFA and DFA agree $\checkmark$
- **Test String $\epsilon$ (Empty)**:
  - DFA State: $A$ (Non-accepting) $\implies$ **REJECTED**
  - NFA Frontier: $[q_0]$ ($q_0 \notin F$) $\implies$ **REJECTED**
  - **Verdict**: NFA and DFA agree $\checkmark$

---

## 5. Conclusion & Transition to Milestone 2

All theoretical objectives, formal specifications, architecture models, algorithm pseudocode, and manual validations for **Milestone 1 (5 Marks)** are fulfilled. 

In **Milestone 2 (Implementation & Verification)**, the implementation is connected to the interactive Streamlit dashboard (`app.py`), the dual-machine Graphviz renderer (`ui/graphs.py`), and the automated 59-test verification suite (`scripts/verify.py`).
