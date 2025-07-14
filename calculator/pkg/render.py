def render(expression, result):
    if isinstance(result, float) and result.is_integer():
        result_str = str(int(result))
    else:
        result_str = str(result)

    box_width = max(len(expression), len(result_str)) + 4
    lines = []
    lines.append("┌" + "─" * box_width + "┐")
    lines.append("│  " + expression + " " * (box_width - len(expression) - 2) + "│")
    lines.append("│" + " " * box_width + "│")
    lines.append("│  =" + " " * (box_width - 3) + "│")
    lines.append("│" + " " * box_width + "│")
    lines.append("│  " + result_str + " " * (box_width - len(result_str) - 2) + "│")
    lines.append("└" + "─" * box_width + "┘")
    return "\n".join(lines)
