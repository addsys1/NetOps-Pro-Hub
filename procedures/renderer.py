import re


def render_command_template(template_str: str, variables: dict) -> str:
    """
    Remplace les variables {{ nom_var }} dans un template de commandes.
    Approche simple et sécurisée : substitution par regex, sans évaluation de code.
    """
    if not template_str:
        return ''

    def replacer(match):
        var_name = match.group(1).strip()
        return str(variables.get(var_name, match.group(0)))

    return re.sub(r'\{\{\s*(\w+)\s*\}\}', replacer, template_str)
