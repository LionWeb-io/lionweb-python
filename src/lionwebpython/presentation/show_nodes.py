import hashlib
from typing import cast

from IPython.display import HTML, display

from lionwebpython.model.node import Node


def _generate_color_for_text(text: str) -> str:
    """Generate a consistent background color for a given text (e.g., node type)."""
    hash_object = hashlib.md5(text.encode())  # Hash the text
    hex_value = hash_object.hexdigest()[:6]  # Use first 6 characters for color

    # Convert hex to RGB values
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)

    # Ensure colors are lighter by shifting them towards white
    lightness_factor = 0.5  # 0 = no change, 1 = fully white
    r = int(r + (255 - r) * lightness_factor)
    g = int(g + (255 - g) * lightness_factor)
    b = int(b + (255 - b) * lightness_factor)

    # Convert back to hex
    lighter_hex_color = f"#{r:02X}{g:02X}{b:02X}"
    return lighter_hex_color


def _html_for_node(node: Node, role: str = "root") -> str:
    role_color = _generate_color_for_text(role)
    classifier_color = _generate_color_for_text(node.get_classifier().qualified_name())

    html = ""
    if len(node.get_children()) == 0:
        html += """<li><span class='leaf'>🌿</span>"""
    else:
        html += """<li onclick="toggleNode(event)"><span class="arrow">▶</span>"""

    html += "<div class='node'>"
    html += f"<p class='role' style='background-color:{role_color}'>{role}</p>"
    html += f"<p class='type' style='background-color:{classifier_color}'>{node.get_classifier().get_name()}</p>"
    html += "<div class='content'>\n"
    html += f"<p class='nodeid'>{node.get_id()}</p>\n"
    html += """<p class="properties">\n"""
    for property in node.get_classifier().all_properties():
        html += f"<span class='propertyname'>{property.get_name()}</span><span class='equals'>&mapsto;</span>\n"
        html += f"<span class='propertyvalue'>{node.get_property_value(property=property)}</span><br/>\n"
    html += "</p>\n"
    html += "</div>\n"  # close content
    html += "</div>\n"  # close node
    html += "<ul>\n"
    for containment in node.get_classifier().all_containments():
        for child in node.get_children(containment=containment):
            html += _html_for_node(child, cast(str, containment.get_name()))
    html += "</ul>"
    html += "</li>"
    return html


def display_node(node: Node):
    html_code = """
    <style>
        /* Basic styling */
        .tree {
            font-family: Arial, sans-serif;
            font-size: 16px;
            list-style-type: none;
        }

        /* Parent list item */
        .tree li {
            position: relative;
            margin: 3px 0;
            padding-left: 5px;
            display: flex;
            align-items: center;
            gap: 3px; /* Space between arrow and box */
            cursor: pointer;
        }

        /* Node box */
        .tree li div.node {
            display: inline-block;
            padding: 0;
            background-color: #f4f4f4;
            border: 1px solid #005bcf;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            color: #333;
            transition: background 0.3s, transform 0.2s;
            min-width: 50pt;
            display: grid;
            grid-template-columns: 1fr 1fr; /* Two equal columns */
            gap: 0px;
        }
        div.content {
            margin:0;
            padding: 4px;
            grid-column: span 2;
        }

        p.role {
            text-align: center;
            font-size: 8pt;
            color: #333;
            margin:0;
            padding:1px;
            display: inline;
            border-bottom: 1px #333 solid;
            border-right: 1px #333 dashed;
        }
        p.type {
            text-align: center;
            font-size: 8pt;
            color: #333;
            margin:0;
            padding:1px;
            display: inline;
            border-bottom: 1px #333 solid;
        }
        p.nodeid {
            text-align:left;
            font-weight: 600;
            color: #333;
            font-size: 12pt;
            margin:3px 3px;
        }
        p.properties {
            font-size: 9pt;
            font-weight: 200;
            color: black;
            text-align:left;
            margin:3px 3px;
            display: inline-grid;
            grid-template-columns: auto 10px auto 1px;
            gap: 3px; 
            align-items: center;
        }
        span.propertyname {
            text-decoration: underlined;
            color: gray;
        }
        span.propertyvalue {
            font-style: italic;
            color: blue;
        }

        /* Hover effect */
        .tree li div.node:hover {
            background-color: #007bff;
            color: white;
            transform: scale(1.05);
        }

        /* Hide children initially */
        .tree ul {
            display: none;
            list-style-type: none;
            padding-left: 20px;
        }

        /* Arrow styling */
        .arrow {
            display: inline-block;
            width: 12px;
            height: 12px;
            font-size: 14px;
            transition: transform 0.2s ease;
        }
        
        .leaf {
            display: inline-block;
            width: 12px;
            height: 12px;
            font-size: 14px;
        }

        /* Expanded state */
        .expanded > .arrow {
            transform: rotate(90deg);
        }

        /* Show children when expanded */
        .expanded > ul {
            display: block;
        }

        /* Connector lines */
        .tree ul {
            margin-left: 20px;
            border-left: 2px solid #ccc;
            padding-left: 15px;
        }

        .tree li::before {
            content: "";
            position: absolute;
            left: -10px;
            top: 50%;
            width: 10px;
            height: 2px;
            background-color: #ccc;
        }

    </style>

    <ul class="tree">
        NODE_DATA
    </ul>

    <script>
        function toggleNode(event) {
            event.stopPropagation(); // Prevent event bubbling

            // Find the clicked <li> and toggle 'expanded'
            var node = event.target.closest("li"); 

            if (node) {
                node.classList.toggle("expanded");
            }
        }
    </script>
    """.replace(
        "NODE_DATA", _html_for_node(node)
    )
    display(HTML(html_code))
