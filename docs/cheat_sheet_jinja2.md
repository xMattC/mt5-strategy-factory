
# Jinja2 Cheat Sheet

## Variables
```jinja
{{ variable }}
{{ user.name }}
{{ items[0] }}
```

## Filters
```jinja
{{ name|lower }}
{{ list|length }}
{{ price|round(2) }}
{{ date|date('Y-m-d') }}
```

## Expressions
```jinja
{{ 2 + 2 }}
{{ total / count }}
```

## Comments
```jinja
{# This is a comment #}
```

## If / Else / Elif
```jinja
{% if user.is_admin %}
  Hello, admin!
{% elif user.is_active %}
  Hello, active user!
{% else %}
  Please log in.
{% endif %}
```

## For Loops
```jinja
{% for item in items %}
  - {{ item }}
{% endfor %}
```
- `{{ loop.index }}` — 1-based index
- `{{ loop.index0 }}` — 0-based index
- `{{ loop.first }}` — True if first loop

## Set Variables
```jinja
{% set total = price * quantity %}
{{ total }}
```

## Includes
```jinja
{% include "header.html" %}
```

## Extends (Inheritance)
```jinja
{% extends "base.html" %}
```

### Blocks
```jinja
{% block content %}
  Your content here.
{% endblock %}
```

## Macros (Reusable Templates)
```jinja
{% macro input(name, value='', type='text') %}
  <input type="{{ type }}" name="{{ name }}" value="{{ value }}">
{% endmacro %}

{{ input('username') }}
```

## Import Macros
```jinja
{% import "macros.html" as macros %}
{{ macros.input('email') }}
```

## With
```jinja
{% with foo='bar' %}
  {{ foo }}
{% endwith %}
```

## Whitespace Control
```jinja
{{- variable -}}
{% -%}  ... {%- %}
```
- Removes whitespace around the tag.

---

## Useful Filters (Just a Few)
- `length`: `{{ list|length }}`
- `join`: `{{ list|join(', ') }}`
- `replace`: `{{ string|replace('a', 'b') }}`
- `default`: `{{ value|default('N/A') }}`

---

## Quick Examples

### Loop with Condition
```jinja
{% for item in items if item.active %}
  {{ item.name }}
{% endfor %}
```

### Chaining Filters
```jinja
{{ text|replace('\n', '<br>')|safe }}
```

### Safe Output (no escaping)
```jinja
{{ html|safe }}
```

---

## Pro Tips
- All Python built-in types (lists, dicts, etc.) work inside templates.
- Filters and tests: `{% if user is defined %}` or `{% if foo is none %}`
- You can nest templates with `{% extends %}` and `{% block %}` for layouts.
