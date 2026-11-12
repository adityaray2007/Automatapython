# Subset Lab (Python): NFA → DFA Conversion Simulator

An educational, interactive web simulator for Automata Theory (**Topic 1: NFA → DFA Conversion**). Built with **Python 3**, **Streamlit**, and **Graphviz DOT**, designed specifically for university students to explore subset construction and confidently explain every line of code during viva examinations.

---

## 1. What It Is & Key Features

**Subset Lab** visualizes the deterministic collapse of Non-Deterministic Finite Automata (NFA) into Deterministic Finite Automata (DFA) using the classic **subset construction** algorithm (Rabin-Scott powerset construction).

- **Pure-Logic Architecture**: 100% pure Python automata engine in `algorithm/` with zero UI dependencies, written at a clean beginner level with extensive English comments.
- **Side-by-Side DFA & Construction View**: Watch the DFA state diagram and step-by-step subset construction progress side-by-side in real time without scrolling.
- **Flexible Transition Entry**: Choose target states from a clean multi-select dropdown or type arbitrary state names directly.
- **Custom / Blank NFA Mode**: Start from scratch with a blank canvas or choose from verified textbook presets.
- **Interactive Step Player**: Step forward, backward, reset, or auto-play through construction transitions one symbol at a time.
- **Dual Live Diagrams**: Browser-rendered Graphviz state machines for both NFA and DFA with automatic edge merging and start/accept state indicators.
- **Subset Inspector**: Select any DFA state to highlight its constituent NFA member states directly on the NFA diagram.
- **Synchronized Transition Tables**: Real-time transition matrices mapping DFA aliases ($A, B, C\dots$) to exact NFA subsets.
- **Equivalence Verification**: Run single strings or batch suites across both machines simultaneously to verify identical acceptance verdicts and view complete step-by-step state traces.
- **Zero Heavy Dependencies**: Graphviz DOT is rendered client-side by Streamlit without requiring system Graphviz binaries or C-extensions.

---

## 2. Setup & Execution

### Prerequisites
- Python ≥ 3.10 (3.11, 3.12, or 3.14 supported).

### Step 1: Create Virtual Environment
```bash
# Navigate to the project directory
cd nfa2dfa-simulator

# Create virtual environment
python3 -m venv .venv
```

### Step 2: Install Dependencies
Always invoke the virtual environment's Python directly:
```bash
# macOS / Linux:
.venv/bin/python -m pip install -r requirements.txt

# Windows (Command Prompt / PowerShell):
.venv\Scripts\python -m pip install -r requirements.txt
```

### Step 3: Run the Web Application
```bash
# macOS / Linux:
.venv/bin/python -m streamlit run app.py

# Windows:
.venv\Scripts\python -m streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### Step 4: Run the Complete Test Suite
```bash
# macOS / Linux:
.venv/bin/python -m pytest

# Windows:
.venv\Scripts\python -m pytest
```

### Step 5: Run Full Automated Verification
```bash
# macOS / Linux:
.venv/bin/python scripts/verify.py

# Windows:
.venv\Scripts\python scripts\verify.py
```

### Step 6: Viva Terminal Demo (No UI Needed)
To demonstrate the algorithm in terminal during viva:
```bash
# Run default example (Ends with "ab")
.venv/bin/python -m algorithm.demo

# Or run any specific preset (e.g. contains-101, third-from-last-a):
.venv/bin/python -m algorithm.demo contains-101
```

---

## 3. Project Structure

```
nfa2dfa-simulator/
├─ app.py                       ← Thin Streamlit UI layer; handles widgets and layout
├─ requirements.txt             ← Pinning streamlit>=1.40 and pytest>=8
├─ pytest.ini                   ← Pytest testpaths and pythonpath configuration
├─ README.md                    ← Complete project documentation, viva guide & test sheet
├─ .streamlit/config.toml        ← Local theme and privacy configuration
├─ scripts/verify.py            ← 1-command verification (compiler, pytest, server smoke test)
├─ algorithm/                   ← PURE LOGIC — The viva core (no UI imports allowed!)
│  ├─ __init__.py               ← Package marker
│  ├─ models.py                 ← Pure dataclasses: NFA, DFA, DFAState, ConstructionStep
│  ├─ validate.py               ← Input parser and validator with user-friendly errors
│  ├─ subset_construction.py    ← THE core subset construction algorithm
│  ├─ simulate.py               ← Trace simulation of strings on NFA and DFA
│  ├─ explain.py                ← Human-readable English descriptions of construction steps
│  ├─ examples.py               ← 5 preset textbook NFAs with verified test cases
│  └─ demo.py                   ← Terminal runner to display conversion steps without UI
├─ ui/                          ← Presentation support modules
│  ├─ __init__.py               ← Package marker
│  ├─ graphs.py                 ← Graphviz DOT generator for NFA and DFA diagrams
│  └─ styles.py                 ← Modern glassmorphism CSS theme with responsive wrapping
└─ tests/                       ← Comprehensive test suite (unit, purity & UI)
   ├─ test_subset.py            ← Mathematical unit tests for subset construction
   ├─ test_simulate.py          ← Simulation verification and NFA/DFA language agreement
   ├─ test_validate.py          ← Validation rules and epsilon-transition rejection
   ├─ test_examples.py          ← Consistency of the 5 textbook presets
   ├─ test_explain.py           ← Natural language step explanation tests
   ├─ test_graphs.py            ← DOT graph generation and visual styling tests
   ├─ test_purity.py            ← Architectural purity guard (ensures algorithm/ has no UI code)
   └─ test_app.py               ← End-to-end headless UI tests via Streamlit AppTest
```

---

## 4. "Explain It in a Viva"

### 4.1 Subset Construction in 7 Plain-English Steps
1. **DFA States are Sets of NFA States**: Because an NFA can be in multiple states simultaneously (or die on dead-end paths), each single state in the DFA represents a specific *subset* of NFA states.
2. **Start with the Start Subset**: The DFA start state is simply $\{q_0\}$, where $q_0$ is the NFA start state.
3. **Queue Unvisited Subsets**: Put the initial DFA state into a worklist / FIFO queue.
4. **Compute Transitions**: For the current DFA state subset $S$ and for each alphabet symbol $a \in \Sigma$:
   - For every NFA state $q \in S$, look up its transition $\delta_{NFA}(q, a)$.
5. **Take the Union**: Combine all reached NFA states into a single target set:
   $$T = \bigcup_{q \in S} \delta_{NFA}(q, a)$$
6. **Register or Reuse**:
   - If $T$ is empty, it becomes the dead/trap state $\emptyset$.
   - If $T$ has not been seen before, assign it a new alias ($A, B, C\dots$) and add it to the queue for future processing.
   - Add the deterministic edge $S \xrightarrow{a} T$ to the DFA.
7. **Mark Accepting States**: Any DFA state $S$ is marked accepting if **at least one** of its constituent NFA states is an NFA accepting state ($S \cap F_{NFA} \neq \emptyset$).

---

### 4.2 Worked Example: Ends with "ab"
Consider the textbook NFA over $\Sigma = \{a, b\}$:
- States: $\{q_0, q_1, q_2\}$, Start: $q_0$, Accepting: $\{q_2\}$.
- $\delta(q_0, a) = \{q_0, q_1\}$, $\delta(q_0, b) = \{q_0\}$
- $\delta(q_1, b) = \{q_2\}$
- All other transitions empty.

#### Construction Table Derivation:
1. **Start state $A = \{q_0\}$**:
   - On $a$: $\delta(q_0, a) = \{q_0, q_1\} \implies \text{NEW state } B = \{q_0, q_1\}$.
   - On $b$: $\delta(q_0, b) = \{q_0\} \implies \text{existing state } A$.
2. **Process $B = \{q_0, q_1\}$**:
   - On $a$: $\delta(q_0, a) \cup \delta(q_1, a) = \{q_0, q_1\} \cup \emptyset = \{q_0, q_1\} \implies \text{existing state } B$.
   - On $b$: $\delta(q_0, b) \cup \delta(q_1, b) = \{q_0\} \cup \{q_2\} = \{q_0, q_2\} \implies \text{NEW state } C = \{q_0, q_2\}$.
3. **Process $C = \{q_0, q_2\}$** (Accepting because $q_2 \in C$):
   - On $a$: $\delta(q_0, a) \cup \delta(q_2, a) = \{q_0, q_1\} \cup \emptyset = \{q_0, q_1\} \implies \text{existing state } B$.
   - On $b$: $\delta(q_0, b) \cup \delta(q_2, b) = \{q_0\} \cup \emptyset = \{q_0\} \implies \text{existing state } A$.

**Final DFA Table**:
| DFA State | Subset | on $a$ | on $b$ | Accepting? |
|:---:|:---:|:---:|:---:|:---:|
| $\rightarrow A$ | $\{q_0\}$ | $B\ \{q_0, q_1\}$ | $A\ \{q_0\}$ | No |
| $B$ | $\{q_0, q_1\}$ | $B\ \{q_0, q_1\}$ | $C\ \{q_0, q_2\}$ | No |
| $* C$ | $\{q_0, q_2\}$ | $B\ \{q_0, q_1\}$ | $A\ \{q_0\}$ | **Yes (contains $q_2$)** |

---

### 4.3 Key Theoretical Questions & Viva Answers

**Q1: Why can a DFA have up to $2^n$ states for an $n$-state NFA?**
> *Answer:* An NFA with $n$ states has $2^n$ possible subsets (the power set $\mathcal{P}(Q)$). While many subsets are often unreachable in practice, languages like *"the $k$-th symbol from the end is $a$"* require keeping track of all possible histories over the last $k$ symbols, forcing the DFA to realize all $2^k$ distinct states.

**Q2: What is the dead state $\emptyset$ and why is it needed?**
> *Answer:* An NFA is permitted to have missing transitions, where branches simply die. A DFA, by mathematical definition, must have a total transition function ($\delta: Q \times \Sigma \to Q$ is defined for every pair). When the union of targets is empty ($\emptyset$), the DFA transitions to the dead state $\emptyset$, which traps and loops back to itself on every alphabet symbol.

**Q3: Why is a DFA state accepting if ANY member is accepting?**
> *Answer:* Non-determinism means the NFA accepts a string if there exists *at least one* valid computational path that ends in an accepting state. Since the DFA tracks all simultaneously reachable paths in its subset, reaching a subset that contains any accepting state guarantees that at least one NFA path succeeded.

**Q4: How does the string testing agree badge prove equivalence?**
> *Answer:* The NFA simulation maintains the active frontier set of all states reachable after consuming each prefix. The DFA moves between single subset states. If the subset state of the DFA after reading prefix $w$ is identical to the NFA's active frontier, and their acceptance decisions match across all test strings, both machines recognize the exact same language.

---

## 5. Walkthrough of `algorithm/subset_construction.py`

- `set_id(members: list[str]) -> str`:
  Converts a list of NFA state names into a standard string representation. Empty list returns `"∅"`, and `["q0", "q1"]` returns `"{q0,q1}"`.
- `alias_for(index: int) -> str`:
  Generates user-friendly names for DFA states ($0 \to A, 1 \to B, \dots, 25 \to Z, 26 \to A1$).
- `subset_construction(nfa: NFA) -> ConversionResult`:
  1. Records the declared NFA state order in an `order` map to ensure all subsets are deduplicated and sorted deterministically.
  2. `register(members)`: Helper that checks if a subset was already discovered; if not, instantiates a `DFAState` and assigns its alias and acceptance status.
  3. Initializes the DFA start state with `[nfa.start]`.
  4. Maintains a BFS `deque` queue of DFA states.
  5. In each iteration, pops `current`, iterates over all alphabet symbols, computes `MoveDetail` for each constituent NFA state, computes the union `result_members`, and records the step in `steps`.
  6. Returns a `ConversionResult` containing the complete `DFA` and the full history of `ConstructionStep` objects.

---

## 6. Manual Test Sheet

| # | Preset | Expected DFA states | Should ACCEPT | Should REJECT |
|---|---|---|---|---|
| 1 | Ends with “ab” | 3 | `ab`, `aab`, `bab`, `abab` | `abb`, `a`, `ba`, empty |
| 2 | 3rd symbol from the end is “a” | 8 | `abb`, `aab`, `aaa`, `babb`, `bbabb` | `baa`, `bab`, `bbb`, `ab`, empty |
| 3 | Contains substring “101” | 6 | `101`, `0101`, `11011`, `1010` | `1001`, `100`, `0110`, `11`, empty |
| 4 | Starts with 0 (dead state ∅) | 3 (includes ∅) | `0`, `01`, `0110` | `1`, `10`, empty |
| 5 | a* (accepts empty) | 2 (includes ∅) | empty (use `<empty>` in the batch box), `a`, `aaa` | `b`, `ab`, `ba` |

### Exercise 6 — Manual Custom Test ("Contains aa")
Type this NFA yourself into the editor or choose **Exercise 6** from the presets:
- **States**: `q0, q1, q2`
- **Alphabet**: `a, b`
- **Start**: `q0`
- **Accepting**: `q2`
- **Transitions**:
  - $\delta(q_0, a) =$ `q0, q1`
  - $\delta(q_0, b) =$ `q0`
  - $\delta(q_1, a) =$ `q2`
  - $\delta(q_2, a) =$ `q2`
  - $\delta(q_2, b) =$ `q2`
  - All other cells empty.
- **Expected DFA**: **4 DFA states**:
  - $A = \{q_0\}$
  - $B = \{q_0, q_1\}$
  - $C = \{q_0, q_1, q_2\}^*$ (Accepting)
  - $D = \{q_0, q_2\}^*$ (Accepting)
- **Edges**: $A \xrightarrow{a} B, A \xrightarrow{b} A, B \xrightarrow{a} C, B \xrightarrow{b} A, C \xrightarrow{a} C, C \xrightarrow{b} D, D \xrightarrow{a} C, D \xrightarrow{b} D$.
- **Accept**: `aa`, `baab`, `bbaa`.
- **Reject**: `abab`, `aba`, `b`, `<empty>`.

### Error-Handling Checks (App Will Not Crash)
- **Duplicate states**: `q0, q0` $\to$ Convert $\to$ Error: `"State names must be unique."`
- **Epsilon in alphabet**: `a, ε` (or `eps`, `lambda`) $\to$ Convert $\to$ Error: `"ε-transitions are not supported here — this simulator handles plain NFAs only."`
- **Unknown transition target**: Cell containing `q9` $\to$ Error: `"δ(...) points to unknown state "q9""`
- **Exceeding state limit**: 13 states $\to$ Error: `"At most 12 states are supported."`
- **Invalid symbol**: In Preset 1, test string `abc` $\to$ **Rejected** + Warning: `'Symbol "c" is not in the alphabet.'`
- **Editor invalidation**: After Convert, editing any field marks previous results stale and disables test buttons until Convert is clicked again.
- **Step player**: Reset shows only start state; Next advances one step; Play auto-advances.

---

## 7. Limitations & Design Boundaries
1. **Plain NFAs Only**: Does not support $\epsilon$-transitions (Topic 1 focuses strictly on NFA $\to$ DFA; $\epsilon$-NFA $\to$ NFA is a separate topic).
2. **Maximum 12 States**: Prevents memory and visualization overload from exponential state blow-up ($2^{12} = 4096$).
3. **Inspector Replaces Hover**: Due to web framework sandbox constraints, subset member highlighting is activated via the "Inspect DFA state" dropdown rather than mouse hover events.
