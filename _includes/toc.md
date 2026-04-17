{%- comment -%}
Dynamic Table of Contents
Usage: {% include toc.md html=content h_min=2 h_max=3 %}
{%- endcomment -%}

{%- assign html = include.html -%}
{%- assign h_min = include.h_min | default: 2 -%}
{%- assign h_max = include.h_max | default: 3 -%}

{%- capture toc -%}
{%- assign headers = html | split: '<h' -%}
{%- for header in headers offset: 1 -%}
  {%- assign header_parts = header | split: '>' -%}
  {%- assign level = header_parts[0] | slice: 0, 1 | to_integer -%}
  {%- if level >= h_min and level <= h_max -%}
    {%- assign title = header_parts[1] | remove: '</h' | strip_html | strip -%}
    {%- assign id = header_parts[0] | split: 'id="' | last | split: '"' | first -%}
    - [{{ title }}](#{{ id }})
  {%- endif -%}
{%- endfor -%}
{%- endcapture -%}

{{ toc | markdownify }}
