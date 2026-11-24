"""
Algebra & Linear Equations Knowledge Graph DAG Loader
Defines 42 interconnected skill nodes spanning Grade 6 Foundations through Algebra 1,
with strict prerequisite dependency edges forming a Directed Acyclic Graph (DAG).
"""

from typing import Dict, List, Any

# Complete 42-Node Knowledge Graph Ontology for Algebra & Linear Equations
ALGEBRA_DAG_NODES: List[Dict[str, Any]] = [
    # --- Group 1: Grade 6-7 Foundational Number Operations (10 Nodes) ---
    {
        "id": "MATH-NUM-NEG-ADD",
        "name": "Adding Negative Numbers",
        "grade_level": "Grade 7",
        "domain": "Number System",
        "description": "Rules for adding integers with same and differing signs."
    },
    {
        "id": "MATH-NUM-NEG-SUB",
        "name": "Subtracting Negative Numbers",
        "grade_level": "Grade 7",
        "domain": "Number System",
        "description": "Recognizing double negatives as positive addition: a - (-b) = a + b."
    },
    {
        "id": "MATH-NUM-NEG-MULT",
        "name": "Multiplying Negative Integers",
        "grade_level": "Grade 7",
        "domain": "Number System",
        "description": "Sign rules for integer multiplication: negative times negative is positive."
    },
    {
        "id": "MATH-NUM-NEG-DIV",
        "name": "Dividing Negative Integers",
        "grade_level": "Grade 7",
        "domain": "Number System",
        "description": "Division of signed integers and sign determination of fractions."
    },
    {
        "id": "MATH-NUM-FRAC-SIMP",
        "name": "Simplifying Fractions",
        "grade_level": "Grade 6",
        "domain": "Number System",
        "description": "Dividing numerator and denominator by greatest common divisor."
    },
    {
        "id": "MATH-NUM-FRAC-MULT",
        "name": "Multiplying Fractions",
        "grade_level": "Grade 6",
        "domain": "Number System",
        "description": "Multiplying numerators and denominators directly."
    },
    {
        "id": "MATH-NUM-FRAC-DIV",
        "name": "Dividing Fractions & Reciprocals",
        "grade_level": "Grade 6",
        "domain": "Number System",
        "description": "Inverting divisor and multiplying by the reciprocal."
    },
    {
        "id": "MATH-NUM-FRAC-ADD",
        "name": "Adding Fractions with Common Denominators",
        "grade_level": "Grade 6",
        "domain": "Number System",
        "description": "Finding LCM common denominators to combine fractional terms."
    },
    {
        "id": "MATH-NUM-ORDER-OPS",
        "name": "Order of Operations (PEMDAS)",
        "grade_level": "Grade 6",
        "domain": "Expressions",
        "description": "Parentheses, exponents, multiplication/division, addition/subtraction precedence."
    },
    {
        "id": "MATH-NUM-ABS",
        "name": "Absolute Value & Number Line Distance",
        "grade_level": "Grade 6",
        "domain": "Number System",
        "description": "Magnitude of numbers independent of sign direction."
    },

    # --- Group 2: Grade 7-8 Algebraic Expressions & Properties (9 Nodes) ---
    {
        "id": "MATH-ALG-VARS",
        "name": "Variables as Unknown Quantities",
        "grade_level": "Grade 6",
        "domain": "Expressions",
        "description": "Understanding letters representing variable numbers in algebraic statements."
    },
    {
        "id": "MATH-ALG-TERMS-COMB",
        "name": "Combining Like Terms (Single Variable)",
        "grade_level": "Grade 7",
        "domain": "Expressions",
        "description": "Adding/subtracting coefficients of identical variable terms: 3x + 5x = 8x."
    },
    {
        "id": "MATH-ALG-TERMS-MULTIVAR",
        "name": "Combining Like Terms (Multi-Variable)",
        "grade_level": "Grade 8",
        "domain": "Expressions",
        "description": "Grouping terms with differing variables and constants: 4x + 2y - x + 5."
    },
    {
        "id": "MATH-ALG-DISTRIB-POS",
        "name": "Distributive Property (Positive Factors)",
        "grade_level": "Grade 7",
        "domain": "Expressions",
        "description": "Expanding terms over binomials: a(b + c) = ab + ac."
    },
    {
        "id": "MATH-ALG-DISTRIB-NEG",
        "name": "Distributive Property (Negative Factors)",
        "grade_level": "Grade 7",
        "domain": "Expressions",
        "description": "Distributing negative constants with sign inversions: -3(x - 4) = -3x + 12."
    },
    {
        "id": "MATH-ALG-DISTRIB-FRAC",
        "name": "Distributive Property (Fractional Multipliers)",
        "grade_level": "Grade 8",
        "domain": "Expressions",
        "description": "Distributing fractions across binomial terms: 1/2(4x - 6) = 2x - 3."
    },
    {
        "id": "MATH-ALG-ADD-INV",
        "name": "Additive Inverse Property",
        "grade_level": "Grade 7",
        "domain": "Expressions",
        "description": "Using opposite operations (+ to -) to create zero pairs."
    },
    {
        "id": "MATH-ALG-MULT-INV",
        "name": "Multiplicative Inverse Property",
        "grade_level": "Grade 7",
        "domain": "Expressions",
        "description": "Multiplying by reciprocal to isolate coefficient of 1: (1/a) * ax = x."
    },
    {
        "id": "MATH-ALG-EVAL-EXPR",
        "name": "Evaluating Algebraic Expressions",
        "grade_level": "Grade 6",
        "domain": "Expressions",
        "description": "Substituting numerical values into algebraic variables."
    },

    # --- Group 3: One-Step & Two-Step Linear Equations (8 Nodes) ---
    {
        "id": "MATH-EQ-SCALE-BALANCE",
        "name": "Equation as a Balanced Scale",
        "grade_level": "Grade 6",
        "domain": "Equations",
        "description": "Core principle: whatever operation is applied to one side must be applied to the other."
    },
    {
        "id": "MATH-EQ-1STEP-ADD",
        "name": "One-Step Linear Equations (Addition/Subtraction)",
        "grade_level": "Grade 6",
        "domain": "Equations",
        "description": "Solving equations of form x + a = b or x - a = b."
    },
    {
        "id": "MATH-EQ-1STEP-MULT",
        "name": "One-Step Linear Equations (Multiplication)",
        "grade_level": "Grade 6",
        "domain": "Equations",
        "description": "Solving equations of form ax = b by dividing both sides by a."
    },
    {
        "id": "MATH-EQ-1STEP-DIV",
        "name": "One-Step Linear Equations (Division)",
        "grade_level": "Grade 6",
        "domain": "Equations",
        "description": "Solving equations of form x/a = b by multiplying both sides by a."
    },
    {
        "id": "MATH-EQ-1STEP-NEG",
        "name": "One-Step Equations with Negative Coefficients",
        "grade_level": "Grade 7",
        "domain": "Equations",
        "description": "Isolating variable when coefficient is negative: -x = 5 -> x = -5."
    },
    {
        "id": "MATH-EQ-2STEP-BASIC",
        "name": "Two-Step Linear Equations (Basic ax + b = c)",
        "grade_level": "Grade 7",
        "domain": "Equations",
        "description": "Isolating constant term first via addition/subtraction, then isolating variable coefficient."
    },
    {
        "id": "MATH-EQ-2STEP-FRAC",
        "name": "Two-Step Linear Equations with Fractions",
        "grade_level": "Grade 7",
        "domain": "Equations",
        "description": "Solving (x/a) + b = c or (ax + b)/c = d."
    },
    {
        "id": "MATH-EQ-2STEP-DEC",
        "name": "Two-Step Linear Equations with Decimals",
        "grade_level": "Grade 7",
        "domain": "Equations",
        "description": "Solving two-step linear equations containing decimal coefficients."
    },

    # --- Group 4: Multi-Step & Advanced Linear Equations (6 Nodes) ---
    {
        "id": "MATH-EQ-MULTISTEP-PAREN",
        "name": "Linear Equations with Parentheses",
        "grade_level": "Grade 8",
        "domain": "Equations",
        "description": "Solving equations requiring distribution before isolation: a(x + b) = c."
    },
    {
        "id": "MATH-EQ-MULTISTEP-BOTH-SIDES",
        "name": "Variables on Both Sides of the Equation",
        "grade_level": "Grade 8",
        "domain": "Equations",
        "description": "Moving variable terms to one side and constants to the other: ax + b = cx + d."
    },
    {
        "id": "MATH-EQ-MULTISTEP-COMPLEX",
        "name": "Complex Multi-Step Linear Equations",
        "grade_level": "Grade 8 / Alg 1",
        "domain": "Equations",
        "description": "Combining distribution, like terms, and variables on both sides: a(x + b) + cx = d(x - e)."
    },
    {
        "id": "MATH-EQ-MULTISTEP-FRAC-CLEAR",
        "name": "Clearing Fractions in Linear Equations",
        "grade_level": "Algebra 1",
        "domain": "Equations",
        "description": "Multiplying entire equation by the Least Common Multiple (LCM) of denominators."
    },
    {
        "id": "MATH-EQ-NUM-SOLUTIONS",
        "name": "Determining Number of Solutions",
        "grade_level": "Grade 8",
        "domain": "Equations",
        "description": "Distinguishing one solution (x = a), no solution (0 = 5), and infinitely many (5 = 5)."
    },
    {
        "id": "MATH-EQ-LITERAL-ISOLATE",
        "name": "Rearranging Formulas & Literal Equations",
        "grade_level": "Algebra 1",
        "domain": "Equations",
        "description": "Solving for a target variable in multi-variable geometric or physics formulas."
    },

    # --- Group 5: Word Problems & Mathematical Modeling (5 Nodes) ---
    {
        "id": "MATH-WORD-DEF-VAR",
        "name": "Defining Variables from Word Problems",
        "grade_level": "Grade 6",
        "domain": "Modeling",
        "description": "Identifying the unknown quantity in prose and assigning a variable."
    },
    {
        "id": "MATH-WORD-RATE-SETUP",
        "name": "Linear Word Problems: Fixed Cost & Unit Rate",
        "grade_level": "Grade 7 / Alg 1",
        "domain": "Modeling",
        "description": "Translating real-world scenarios into slope-intercept form: Total = (rate * x) + fee."
    },
    {
        "id": "MATH-WORD-GEOM-PERIM",
        "name": "Geometric Linear Equation Word Problems",
        "grade_level": "Grade 7 / Alg 1",
        "domain": "Modeling",
        "description": "Setting up equations for perimeter, complementary angles, and rectangle dimensions."
    },
    {
        "id": "MATH-WORD-CONSEC-INT",
        "name": "Consecutive Integer Word Problems",
        "grade_level": "Grade 8 / Alg 1",
        "domain": "Modeling",
        "description": "Expressing consecutive numbers algebraically: x, x+1, x+2."
    },
    {
        "id": "MATH-WORD-MULTI-SCENARIO",
        "name": "Comparing Two Rate Scenarios (Both Sides)",
        "grade_level": "Grade 8 / Alg 1",
        "domain": "Modeling",
        "description": "Modeling break-even points: Company A (ax + b) vs Company B (cx + d)."
    },

    # --- Group 6: Inequalities & Graphing Connections (4 Nodes) ---
    {
        "id": "MATH-INEQ-1STEP",
        "name": "One-Step Linear Inequalities (Sign Flipping)",
        "grade_level": "Grade 7",
        "domain": "Inequalities",
        "description": "Reversing inequality direction when multiplying or dividing by a negative number."
    },
    {
        "id": "MATH-INEQ-2STEP",
        "name": "Two-Step Linear Inequalities",
        "grade_level": "Grade 7 / Alg 1",
        "domain": "Inequalities",
        "description": "Solving and graphing solutions to ax + b > c on a number line."
    },
    {
        "id": "MATH-GRAPH-SLOPE-INTERCEPT",
        "name": "Connecting Linear Equations to Graphs (y = mx + b)",
        "grade_level": "Grade 8 / Alg 1",
        "domain": "Functions",
        "description": "Visualizing linear equation solutions as line intercepts and slope rates."
    },
    {
        "id": "MATH-GRAPH-POINT-SLOPE",
        "name": "Point-Slope Form Transformations",
        "grade_level": "Algebra 1",
        "domain": "Functions",
        "description": "Manipulating y - y1 = m(x - x1) into standard and slope-intercept form."
    }
]

# Strict Prerequisite Edges forming the Directed Acyclic Graph (DAG)
# Format: (Target Skill, Prerequisite Skill It Requires)
ALGEBRA_DAG_EDGES = [
    # Integer foundational chains
    ("MATH-NUM-NEG-SUB", "MATH-NUM-NEG-ADD"),
    ("MATH-NUM-NEG-DIV", "MATH-NUM-NEG-MULT"),
    ("MATH-NUM-FRAC-DIV", "MATH-NUM-FRAC-MULT"),
    ("MATH-NUM-FRAC-ADD", "MATH-NUM-FRAC-SIMP"),

    # Algebraic expression prerequisites
    ("MATH-ALG-TERMS-COMB", "MATH-ALG-VARS"),
    ("MATH-ALG-TERMS-COMB", "MATH-NUM-NEG-ADD"),
    ("MATH-ALG-TERMS-MULTIVAR", "MATH-ALG-TERMS-COMB"),
    ("MATH-ALG-DISTRIB-POS", "MATH-ALG-VARS"),
    ("MATH-ALG-DISTRIB-POS", "MATH-NUM-ORDER-OPS"),
    ("MATH-ALG-DISTRIB-NEG", "MATH-ALG-DISTRIB-POS"),
    ("MATH-ALG-DISTRIB-NEG", "MATH-NUM-NEG-MULT"),
    ("MATH-ALG-DISTRIB-FRAC", "MATH-ALG-DISTRIB-POS"),
    ("MATH-ALG-DISTRIB-FRAC", "MATH-NUM-FRAC-MULT"),
    ("MATH-ALG-ADD-INV", "MATH-NUM-NEG-ADD"),
    ("MATH-ALG-MULT-INV", "MATH-NUM-FRAC-DIV"),

    # One-step equations
    ("MATH-EQ-1STEP-ADD", "MATH-EQ-SCALE-BALANCE"),
    ("MATH-EQ-1STEP-ADD", "MATH-ALG-ADD-INV"),
    ("MATH-EQ-1STEP-MULT", "MATH-EQ-SCALE-BALANCE"),
    ("MATH-EQ-1STEP-MULT", "MATH-ALG-MULT-INV"),
    ("MATH-EQ-1STEP-DIV", "MATH-EQ-1STEP-MULT"),
    ("MATH-EQ-1STEP-NEG", "MATH-EQ-1STEP-MULT"),
    ("MATH-EQ-1STEP-NEG", "MATH-NUM-NEG-DIV"),

    # Two-step equations
    ("MATH-EQ-2STEP-BASIC", "MATH-EQ-1STEP-ADD"),
    ("MATH-EQ-2STEP-BASIC", "MATH-EQ-1STEP-MULT"),
    ("MATH-EQ-2STEP-FRAC", "MATH-EQ-2STEP-BASIC"),
    ("MATH-EQ-2STEP-FRAC", "MATH-NUM-FRAC-MULT"),
    ("MATH-EQ-2STEP-DEC", "MATH-EQ-2STEP-BASIC"),

    # Multi-step equations
    ("MATH-EQ-MULTISTEP-PAREN", "MATH-EQ-2STEP-BASIC"),
    ("MATH-EQ-MULTISTEP-PAREN", "MATH-ALG-DISTRIB-NEG"),
    ("MATH-EQ-MULTISTEP-BOTH-SIDES", "MATH-EQ-2STEP-BASIC"),
    ("MATH-EQ-MULTISTEP-BOTH-SIDES", "MATH-ALG-TERMS-COMB"),
    ("MATH-EQ-MULTISTEP-COMPLEX", "MATH-EQ-MULTISTEP-PAREN"),
    ("MATH-EQ-MULTISTEP-COMPLEX", "MATH-EQ-MULTISTEP-BOTH-SIDES"),
    ("MATH-EQ-MULTISTEP-FRAC-CLEAR", "MATH-EQ-MULTISTEP-COMPLEX"),
    ("MATH-EQ-MULTISTEP-FRAC-CLEAR", "MATH-NUM-FRAC-ADD"),
    ("MATH-EQ-NUM-SOLUTIONS", "MATH-EQ-MULTISTEP-BOTH-SIDES"),
    ("MATH-EQ-LITERAL-ISOLATE", "MATH-EQ-MULTISTEP-COMPLEX"),

    # Word problems
    ("MATH-WORD-RATE-SETUP", "MATH-WORD-DEF-VAR"),
    ("MATH-WORD-RATE-SETUP", "MATH-EQ-2STEP-BASIC"),
    ("MATH-WORD-GEOM-PERIM", "MATH-WORD-DEF-VAR"),
    ("MATH-WORD-GEOM-PERIM", "MATH-ALG-TERMS-COMB"),
    ("MATH-WORD-GEOM-PERIM", "MATH-EQ-2STEP-BASIC"),
    ("MATH-WORD-CONSEC-INT", "MATH-WORD-DEF-VAR"),
    ("MATH-WORD-CONSEC-INT", "MATH-ALG-TERMS-COMB"),
    ("MATH-WORD-MULTI-SCENARIO", "MATH-WORD-RATE-SETUP"),
    ("MATH-WORD-MULTI-SCENARIO", "MATH-EQ-MULTISTEP-BOTH-SIDES"),

    # Inequalities & Functions
    ("MATH-INEQ-1STEP", "MATH-EQ-1STEP-MULT"),
    ("MATH-INEQ-1STEP", "MATH-NUM-NEG-DIV"),
    ("MATH-INEQ-2STEP", "MATH-INEQ-1STEP"),
    ("MATH-INEQ-2STEP", "MATH-EQ-2STEP-BASIC"),
    ("MATH-GRAPH-SLOPE-INTERCEPT", "MATH-EQ-2STEP-BASIC"),
    ("MATH-GRAPH-SLOPE-INTERCEPT", "MATH-EQ-LITERAL-ISOLATE"),
    ("MATH-GRAPH-POINT-SLOPE", "MATH-GRAPH-SLOPE-INTERCEPT")
]

def get_algebra_dag():
    """Returns nodes dict and adjacency lists for downstream traversal engines."""
    nodes_by_id = {n["id"]: n for n in ALGEBRA_DAG_NODES}
    prereq_graph = {n["id"]: [] for n in ALGEBRA_DAG_NODES}
    dependent_graph = {n["id"]: [] for n in ALGEBRA_DAG_NODES}

    for target, prereq in ALGEBRA_DAG_EDGES:
        if target in prereq_graph and prereq in nodes_by_id:
            prereq_graph[target].append(prereq)
            dependent_graph[prereq].append(target)

    return {
        "nodes": nodes_by_id,
        "prerequisites_of": prereq_graph,
        "dependents_of": dependent_graph,
        "total_nodes": len(nodes_by_id),
        "total_edges": len(ALGEBRA_DAG_EDGES)
    }

if __name__ == "__main__":
    dag = get_algebra_dag()
    print(f"Loaded Algebra DAG with {dag['total_nodes']} skill nodes and {dag['total_edges']} prerequisite edges.")
