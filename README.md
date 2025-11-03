# Ocelot

**Steps**
- Dynamic Analysis: Identifying Nondeterministic (ND) Variables
- Extracting the Nondeterministic Kernel
- Checking as SMT Satisfiability

---

## 1. Dynamic Analysis: Identifying Nondeterministic (ND) Variables

The purpose of this step is to identify variables in Python algorithms that exhibit nondeterministic behavior across multiple executions. The approach combines AST-level code instrumentation with serialized variable tracing and cross-run comparison.

**Inputs:**  
- Python source code of the target algorithm  
- Arbitrary dataset for execution  

**Outputs:**  
- `trace_run1.pkl`: Serialized variable states from the first execution  
- `trace_run2.pkl`: Serialized variable states from the second execution  
- `nd_report.csv`: Table listing deterministic and nondeterministic variables  
- `diff_log.txt`: Optional log with detailed per-variable value differences  

### 1.1. Initial Instrumentation (Run 1)

In the first run, Ocelot instruments the target algorithm’s source code to capture the state of all relevant variables at runtime.  

#### Steps
1. **Import and dependency analysis**  
   - Ocelot parses the target Python module to identify internal dependencies (e.g., imported functions or helper files).  
   - Each relevant file is queued for instrumentation.

2. **AST traversal and variable detection**  
   - For each line in the AST, assignment nodes (`Assign`, `AugAssign`, etc.) are identified.   
   - Every assigned variable is marked as a *trace target*.

3. **Instrumentation insertion**  
   - Immediately after each assignment, Ocelot injects a function call:
     ```python
     _store_variable(var_name, 'var_name', line_number)
     ```
   - This ensures the value, variable name, and line number are captured right after every assignment.

4. **Helper function injection**  
   - At the top of each instrumented file, Ocelot inserts:
     ```python
     def _store_variable(var, var_name, line_no):
         with open(output_path, 'ab') as f:
             pickle.dump((var_name, line_no, var), f)
     ```
   - The function serializes variable data into a binary log using Python’s Pickle library, ensuring complex data types (NumPy arrays, dicts, lists, etc.) are preserved.

5. **Execution and logging**  
   - The instrumented program is executed once.  
   - All variable traces are collected into an output directory (one file per module or context).

### 1.2. Comparison Phase (Run 2)

In the second run, Ocelot reuses the AST-modification framework but replaces the store calls with comparison calls.

#### Steps
1. **Re-instrumentation**
   - All `_store_variable` calls are replaced with `_compare_to_previous` calls:
     ```python
     _compare_to_previous(var_name, 'var_name', line_number)
     ```
   - The new function retrieves the previously stored variable value from Run 1.

2. **Comparison logic**
   - **Primitive data types** (int, float, str, bool) are compared directly.  
   - **Compound structures** (NumPy arrays, lists, dicts, tuples) are compared recursively:
     - Arrays → element-wise equality.  
     - Dictionaries → key-by-key recursive comparison.  
     - Nested containers → recursive descent to check all elements.

3. **Helper function**
   ```python
   def _compare_to_previous(var, var_name, line_no):
       with open(previous_trace_path, 'rb') as f:
           prev_values = pickle.load(f)
       old_value = find_entry(prev_values, var_name, line_no)
       if not deep_equal(var, old_value):
           log_nd_variable(var_name, line_no)
   ```

4. **Deep equality function**
   - `deep_equal(a, b)` handles:
     - Element-wise NumPy comparison  
     - Recursive dict/list/tuple comparisons  
     - Type mismatches and missing keys

5. **Logging ND results**
   - Each mismatch is logged in a structured CSV or text file:
     ```
     variable_name, file_name, line_number, deterministic_flag
     ```
   - Example:
     ```
     S, _affinity_propagation.py, 81, False
     random_state, _affinity_propagation.py, 512, False
     preference, _affinity_propagation.py, 510, True
     ```

### 1.3. Over-Approximation and Filtering

The dynamic phase captures **all** variables that differ between runs — including:
- Variables that introduce true nondeterminism (e.g., random seeds, uninitialized states).  
- Variables that change as side effects of those nondeterministic sources.

To isolate the true ND sources, Ocelot passes this log to a **taint analysis** module.  
This phase prunes variables that do not affect the algorithm’s final output (e.g., clustering labels).

### 1.4. Output Artifacts

After both runs, the following artifacts are generated:

| File | Description |
|------|--------------|
| `trace_run1.pkl` | Serialized variable states for Run 1 |
| `trace_run2.pkl` | Serialized variable states for Run 2 |
| `nd_report.csv` | Summary table of deterministic vs nondeterministic variables |
| `diff_log.txt` | Optional detailed log of variable differences |

### Example Instrumented Code

**Before instrumentation:**
```python
S += (np.finfo(S.dtype).eps * S + np.finfo(S.dtype).tiny * 100) * random_state.standard_normal(size=(n, n))
```

**After Run 1 instrumentation:**
```python
S += (np.finfo(S.dtype).eps * S + np.finfo(S.dtype).tiny * 100) * random_state.standard_normal(size=(n, n))
_store_variable(S, 'S', 81)
```

**After Run 2 instrumentation:**
```python
S += (np.finfo(S.dtype).eps * S + np.finfo(S.dtype).tiny * 100) * random_state.standard_normal(size=(n, n))
_compare_to_previous(S, 'S', 81)
```

---


## 2. Nondeterministic Kernel Extraction Process

The process integrates dynamic results (ND variables) with static taint analysis using **Pysa**, Meta’s open-source taint analyzer for Python to isolate the *nondeterministic kernel*—the minimal subset of code responsible for propagating nondeterminism from input variables to the final algorithm outputs.

**Inputs:**  
- List of ND variables (from dynamic analysis phase)  
- Target Python source code  

**Outputs:**  
- Annotated source code showing ND propagation paths  
- Taint dependency graph (`taint-output.json`)  
- Function call graph (`call-graph.json`)  
- Extracted nondeterministic kernel summary (`nd_kernel_report.json`)

### 2.1. Defining Sources and Sinks

1. **Sources:**  
   All variables identified as nondeterministic in the previous phase are treated as *taint sources*.  
   Each ND variable is automatically wrapped with a `# taint: source` comment or lightweight model definition for Pysa.

2. **Sinks:**  
   The algorithm’s final outputs—such as `labels_`, `scores_`, or any returned clustering results—are marked as *taint sinks*.  
   These represent the observable outputs potentially affected by nondeterminism.

3. **Automatic model generation:**  
   Ocelot automatically writes a `taint.config` model file for Pysa with entries like:
   ```text
   mymodule._affinity_propagation.S: TaintSource[UserControlled]
   mymodule.fit.labels_: TaintSink[ClusterOutput]
   ```
   This configuration ensures taint propagation begins only from known ND variables and terminates at meaningful outputs.


### 2.2. Running Pysa Analysis

#### Steps

1. **AST and model injection**
   - Ocelot parses the target codebase and injects inline comments or model annotations for ND variables and outputs.
   - The modified project is placed into a temporary directory for static analysis.

2. **Pysa execution**
   - Pysa is invoked as:
     ```bash
     pysa analyze --taint-models taint.config --save-results-to taint_results/
     ```
   - Pysa builds:
     - A **call graph** (`call-graph.json`) showing inter-function dependencies.
     - A **data dependency graph** (`dependency-graph.json`) linking variables and assignments.
     - A **taint output** file (`taint-output.json`) listing all tainted source-to-sink paths.

3. **Filtering irrelevant dependencies**
   - Ocelot filters out edges from external or third-party modules (e.g., NumPy, math, sklearn) to focus analysis on the project’s own files.
   - This avoids noise and ensures the resulting ND kernel represents intrinsic nondeterminism, not library-level randomness.


### 2.3. Parsing and Visualizing the Results

#### Steps
1. **Parse Pysa outputs**
   - The tool reads JSON outputs to locate all function calls, arguments, and return values involved in taint propagation.
   - Example entry:
     ```json
     {
       "source": "S",
       "sink": "labels_",
       "path": ["update_similarity", "fit", "compute_labels"]
     }
     ```

2. **Trace reconstruction**
   - Each propagation path is reconstructed by following edges in the dependency graph.
   - Direct and indirect function calls (including nested class methods) are included.

3. **Code annotation**
   - The original source files are augmented with inline comments marking tainted flows:
     ```python
     S = update_similarity(X)
     # TAINT: propagated from ND variable 'S'
     labels_ = compute_labels(S)
     # TAINT: nondeterminism reaches output
     ```

4. **ND kernel construction**
   - The ND kernel is defined as all functions, classes, and statements appearing on at least one taint path from an ND variable to a clustering output.
   - This kernel is serialized as:
     ```json
     {
       "kernel_functions": ["update_similarity", "compute_labels"],
       "kernel_lines": [81, 512, 523]
     }
     ```


### 2.4. Output Artifacts

| File | Description |
|------|--------------|
| `taint-output.json` | Pysa’s taint propagation results |
| `call-graph.json` | Function-level call relationships |
| `dependency-graph.json` | Variable-level dependencies |
| `nd_kernel_report.json` | Consolidated nondeterministic kernel summary |
| Annotated `.py` files | Original code marked with `# TAINT:` comments |
