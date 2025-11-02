import logging
import re
import numexpr as ne
from langchain.tools import tool


# Deterministic behavior for agents
ne.set_num_threads(1)

# Module logger
logger = logging.getLogger(__name__)


@tool("calculator")
def calculator(expression: str) -> str:
    """
    Evaluate mathematical expressions safely using numexpr.

    The expression should be a direct numeric calculation,
    written in standard Python-style math syntax.

    Returns:
        The numeric result as a string, or an error message if invalid.
    """
    if not isinstance(expression, str) or not expression.strip():
        return "Error: expression must be a non-empty string."

    # Helpers: normalize and validate expression before evaluation
    def _normalize(expr: str) -> str:
        # Strip currency symbols and thousands separators
        expr = expr.replace("$", "")
        expr = expr.replace(",", "")
        # Normalize unicode operators
        expr = expr.replace("−", "-")  # unicode minus
        expr = expr.replace("×", "*")
        expr = expr.replace("·", "*")
        expr = expr.replace("÷", "/")
        # Power operator caret to Python
        expr = re.sub(r"\^", "**", expr)
        # Convert percentages like 12.5% -> (12.5/100)
        expr = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", expr)
        # Collapse whitespace
        expr = re.sub(r"\s+", " ", expr).strip()
        return expr

    def _validate(expr: str) -> str | None:
        # Hard limits to prevent pathological expressions
        if len(expr) > 2000:
            return "expression is too long"
        # Simple parenthesis depth check
        depth = 0
        max_depth = 0
        for ch in expr:
            if ch == "(":
                depth += 1
                max_depth = max(max_depth, depth)
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return "unbalanced parentheses"
        if depth != 0:
            return "unbalanced parentheses"
        if max_depth > 64:
            return "expression nesting too deep"

        # Allowed tokens: digits, operators, parentheses, dot, spaces
        # After normalization, reject any remaining letters (variables/functions)
        # to avoid evaluating names; numexpr supports some functions, but we keep
        # this tool focused on pure numeric arithmetic for safety.
        if re.search(r"[A-Za-z_]", expr):
            return "expression contains names; please provide a plain numeric expression " "(resolve variables first)"
        # Basic character whitelist
        if re.search(r"[^0-9\s\(\)\.\+\-\*/%]", expr):
            return "expression contains invalid characters"
        return None

    try:
        expr_norm = _normalize(expression)
        err = _validate(expr_norm)
        if err:
            logger.warning("[calculator] rejected expression | reason=%s | expression=%s", err, expression)
            return f"Error: {err}"

        logger.info("[calculator] evaluating: %s", expr_norm)
        result = ne.evaluate(expr_norm)
        logger.info("[calculator] result: %s", result)
        return str(result)

    except Exception as e:
        logger.exception("[calculator] error while evaluating expression")
        return f"Error: {type(e).__name__}: {e}"
