from IPython.display import display, HTML
from lionwebpython.model.node import Node

def _html_for_node(node: Node, role: str = 'root') -> str:
    html = f"<div><p class='role'>{role}</p><p class='nodeid'>{node.get_id()}</p>"
    for property in node.get_classifier().all_properties():
        html += "<p class='property'>"
        html += f"<span class='propertyname'>{property.get_name()}</span> = <span class='propertyvalue'>{node.get_property_value(property=property)}</span><br/>"
        html += "</p>"
    html += "</div>"
    html += "<ul>"
    for containment in node.get_classifier().all_containments():
        for child in node.get_children(containment=containment):
            html += f"""<li onclick="toggleNode(event)">
                    <span class="arrow">▶</span>
                    {_html_for_node(child, containment.get_name())}
                </li>"""
    html += "</ul>"
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
        .tree li div {
            display: inline-block;
            padding: 4px 7px;
            background-color: #f4f4f4;
            border: 1px solid #005bcf;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            color: #333;
            transition: background 0.3s, transform 0.2s;
            min-width: 50pt;
        }
        p.role {
            text-align: center;
            font-style: italic;
            font-size: 8pt;
            color: #888;
        }
        p.nodeid {
            text-align:left;
            font-weight: 600;
            color: #333;
            font-size: 12pt;
        }
        p.property {
            font-size: 9pt;
            font-weight: 200;
            color: black;
            text-align:left;
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
        .tree li div:hover {
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
        <li onclick="toggleNode(event)">
            <span class="arrow">▶</span>
            NODE_DATA

        </li>
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
    """.replace("NODE_DATA", _html_for_node(node))
    display(HTML(html_code))
