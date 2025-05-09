import json
from typing import Optional, Dict, List, Union, Any, Set, Callable

print("<!-- Golia version 0.1.0 -->")


class HTMLNode:
    """Represents a node in an HTML document tree with rendering capabilities.

    This class handles HTML elements (with tags) and text nodes (tag=None), manages
    attributes, child nodes, and provides flexible rendering options including
    inline mode and proper indentation.

    Attributes:
        tag (Optional[str]): The HTML tag name (e.g., 'div', 'span'). None for text nodes.
        content (str): The text content of the node.
        attr (Dict[str, Any]): Dictionary of HTML attributes.
        parent (Optional[HTMLNode]): Reference to parent node.
        children (List[HTMLNode]): List of child nodes.
        is_void (bool): Whether this is a void (self-closing) element.
        is_text_node (bool): Whether this is a text node.
        inline (bool): Whether to render inline (without line breaks).
        _force_inline (bool): Internal flag to force inline rendering.
    """

    # Set of HTML void elements that don't need closing tags
    VOID_ELEMENTS: Set[str] = {
        "meta", "img", "br", "hr", "input", "link", "area", "base", "col",
        "embed", "param", "source", "track", "wbr", "command", "keygen", "menuitem"
    }

    # Elements that should typically render inline by default
    INLINE_ELEMENTS: Set[str] = {
        "span", "a", "strong", "em", "code", "small", "b", "i", "u", "mark",
        "sub", "sup", "time", "data", "label", "abbr", "cite", "q", "samp",
        "var", "kbd", "s", "del", "ins"
    }

    def __init__(
            self,
            tag: Optional[str],
            content: str = "",
            attr: Optional[Dict[str, Any]] = None,
            parent: Optional['HTMLNode'] = None
    ) -> None:
        """Initialize an HTML node.

        Args:
            tag: The HTML tag name. None for text nodes.
            content: Text content for the node. Will be converted to string.
            attr: Dictionary of HTML attributes. None becomes empty dict.
            parent: Parent node reference. None for root nodes.

        Note:
            - Tags ending with underscore (_) will have it removed (e.g., 'del_' -> 'del')
            - Boolean attributes can be set with value=True (e.g., {'disabled': True})
        """
        # Handle Python keyword conflicts (e.g., 'del_' -> 'del')
        self.tag = tag[:-1] if tag and tag.endswith('_') else tag
        self.content = str(content)
        self.attr = attr.copy() if attr else {}
        self.parent = parent
        self.children: List[HTMLNode] = []
        self.is_void = self.tag in self.VOID_ELEMENTS
        self.is_text_node = self.tag is None
        self.inline = self.tag in self.INLINE_ELEMENTS if self.tag else False
        self._force_inline = False

    def add_child(
            self,
            tag: Optional[str],
            content: str = "",
            attr: Optional[Dict[str, Any]] = None
    ) -> 'HTMLNode':
        """Add a child node to this node.

        Args:
            tag: The child node's tag name. None creates a text node.
            content: Text content for the child node.
            attr: Dictionary of HTML attributes for the child.

        Returns:
            The newly created child node.

        Raises:
            TypeError: If content is not string-convertible or attr is not a dict.
        """
        if not isinstance(content, (str, int, float, bool)):
            raise TypeError(f"Content must be string-convertible, got {type(content)}")

        if attr is not None and not isinstance(attr, dict):
            raise TypeError(f"Attributes must be a dictionary, got {type(attr)}")

        if tag is None:  # Text node
            text_node = HTMLNode(None, str(content), parent=self)
            self.children.append(text_node)
            return text_node

        child = HTMLNode(tag, str(content), attr, self)
        self.children.append(child)
        return child

    def _convert_attributes(self) -> str:
        """Convert the attribute dictionary to HTML attribute string.

        Handles special cases:
        - 'klass' -> 'class' (Python keyword workaround)
        - Attributes ending with underscore (_) have it removed
        - Underscores in attribute names are converted to hyphens
        - Boolean attributes render as just the name when True (e.g., 'disabled')
        - Special handling for meta tags with boolean content

        Returns:
            String of HTML attributes ready for insertion into tag.
        """
        converted = {}

        for key, value in self.attr.items():
            # Handle special cases
            if key == 'klass':
                converted['class'] = value
                continue

            # Clean up attribute names
            new_key = key[:-1] if key.endswith('_') else key
            new_key = new_key.replace('_', '-')

            # Handle boolean attributes
            if value is True:
                converted[new_key] = None  # Will render as just the attribute name
            else:
                converted[new_key] = value

        # Special handling for meta tags
        if self.tag == "meta" and 'content' in converted and converted['content'] is True:
            converted['content'] = ''

        # Build attribute string
        attr_parts = []
        for key, value in converted.items():
            if value is None:  # Boolean attribute
                attr_parts.append(key)
            else:
                attr_parts.append(f'{key}="{value}"')

        return ' '.join(attr_parts) if attr_parts else ''

    def render(self, indent_level: int = 0, parent_inline: bool = False) -> str:
        """Render the node and its children as HTML string.

        Args:
            indent_level: Number of tabs to use for indentation.
            parent_inline: Whether parent forces inline rendering.

        Returns:
            Formatted HTML string with proper indentation.
        """
        parts = []
        indent = "\t" * indent_level

        # Text nodes are simple
        if self.is_text_node:
            parts.append(indent + self.content)
            return ''.join(parts)

        # Determine rendering mode
        current_inline = self.inline or self._force_inline or parent_inline

        # Convert attributes
        attr_str = self._convert_attributes()

        # Build opening tag
        parts.append(f"{indent}<{self.tag}")
        if attr_str:
            parts.append(f" {attr_str}")

        # Handle void elements
        if self.is_void:
            parts.append(" />")
            return ''.join(parts)

        parts.append(">")

        # Handle content and children
        children_content = ""
        if self.children:
            if current_inline:  # Inline mode - no indentation
                children_content = ''.join(
                    child.render(0, current_inline)
                    for child in self.children
                )
            else:  # Normal mode with indentation
                children_content = "\n" + "\n".join(
                    child.render(indent_level + 1, current_inline)
                    for child in self.children
                ) + "\n" + indent
        elif self.content:
            children_content = self.content

        parts.append(children_content)
        parts.append(f"</{self.tag}>")

        return ''.join(parts)

    def force_inline(self, recursive: bool = False) -> 'HTMLNode':
        """Force this node and optionally its children to render inline.

        Args:
            recursive: Whether to apply to all descendants.

        Returns:
            self for method chaining.
        """
        self._force_inline = True
        if recursive:
            for child in self.children:
                child.force_inline(True)
        return self

    def validate(self) -> bool:
        """Validate the HTML structure of this node and its children.

        Checks for common HTML structure rules like:
        - Lists (ul/ol) must contain only li elements
        - Table structure requirements
        - etc.

        Returns:
            True if structure is valid, False otherwise.
        """
        # Basic validation rules
        if self.tag in {'ul', 'ol'}:
            # Lists must contain only li elements
            return all(child.tag == 'li' for child in self.children)

        if self.tag == 'table':
            # Tables must have proper structure
            has_header = any(child.tag == 'thead' for child in self.children)
            has_body = any(child.tag == 'tbody' for child in self.children)
            return has_header or has_body

        # Recursively validate children
        return all(child.validate() for child in self.children)

    def __str__(self) -> str:
        """Shortcut for rendering with default indentation."""
        return self.render()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<HTMLNode tag={self.tag!r} children={len(self.children)}>"


def add_vendor_prefixes(properties):
    prefixes = {
        'background-clip': ['-webkit-'],
        'user-select': ['-webkit-', '-moz-', '-ms-'],
        'transition': ['-webkit-'],
        'transform': ['-webkit-'],
        'animation': ['-webkit-']
    }

    new_props = {}
    for prop, value in properties.items():
        new_props[prop] = value
        if prop in prefixes:
            for prefix in prefixes[prop]:
                new_props[f"{prefix}{prop}"] = value
    return new_props


class HTML:
    """Manages the structure of an HTML document with head and body sections.

    This class provides methods to build and render the HTML document structure,
    with support for nested elements and context management.

    Attributes:
        head_root (HTMLNode): Root node of the head section.
        body_root (HTMLNode): Root node of the body section.
        current_node (Optional[HTMLNode]): Current working node for nested operations.
    """

    def __init__(self) -> None:
        """Initialize a new HTML document structure."""
        self.head_root = HTMLNode("head")
        self.body_root = HTMLNode("body")
        self.current_node: Optional[HTMLNode] = None

    def add_head_element(
            self,
            tag: str,
            content: str = "",
            attr: Optional[Dict[str, Any]] = None
    ) -> HTMLNode:
        """Add an element to the document head.

        Args:
            tag: The HTML tag name (e.g., 'meta', 'title').
            content: Text content for the element.
            attr: Dictionary of HTML attributes.

        Returns:
            The newly created head element node.

        Example:
            >>> html = HTML()
            >>> html.add_head_element("meta", attr={"charset": "UTF-8"})
            >>> html.add_head_element("title", "My Page")
        """
        return self.head_root.add_child(tag, content, attr)

    def add_body_element(
            self,
            tag: str,
            content: str = "",
            attr: Optional[Dict[str, Any]] = None
    ) -> HTMLNode:
        """Add an element to the document body.

        Args:
            tag: The HTML tag name (e.g., 'div', 'p').
            content: Text content for the element.
            attr: Dictionary of HTML attributes.

        Returns:
            The newly created body element node.

        Note:
            If there's an active nested context (from start_nested_element),
            the new element will be added as a child of the current node.
        """
        parent = self.current_node or self.body_root
        return parent.add_child(tag, content, attr)

    def start_nested_element(
            self,
            tag: str,
            content: str = "",
            attr: Optional[Dict[str, Any]] = None
    ) -> HTMLNode:
        """Begin a nested element context.

        Args:
            tag: The HTML tag name for the new nested element.
            content: Text content for the element.
            attr: Dictionary of HTML attributes.

        Returns:
            The newly created nested element node.

        Note:
            Subsequent elements will be added as children of this node
            until end_nested_element() is called.

        Example:
            >>> with html.start_nested_element("div", attr={"class": "container"}):
            ...     html.add_body_element("p", "This is inside the container")
        """
        parent = self.current_node or self.body_root
        self.current_node = parent.add_child(tag, content, attr)
        return self.current_node

    def end_nested_element(self) -> None:
        """End the current nested element context.

        Returns to the parent element level for subsequent additions.

        Raises:
            RuntimeError: If called when not in a nested context.
        """
        if self.current_node is None:
            raise RuntimeError("Not in a nested element context")
        self.current_node = self.current_node.parent

    def render_head(self, indent_level: int = 1) -> str:
        """Render the head section as HTML.

        Args:
            indent_level: Base indentation level for the head content.

        Returns:
            The rendered HTML string for the head section.
        """
        return "\n".join(
            child.render(indent_level, False)
            for child in self.head_root.children
        )

    def render_body(self, indent_level: int = 1) -> str:
        """Render the body section as HTML.

        Args:
            indent_level: Base indentation level for the body content.

        Returns:
            The rendered HTML string for the body section.
        """
        return "\n".join(
            child.render(indent_level, False)
            for child in self.body_root.children
        )

    def __enter__(self) -> 'HTML':
        """Enable context manager protocol for the HTML object itself."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Clean up context manager."""
        pass

    def clear(self) -> None:
        """Reset the document structure to empty."""
        self.head_root = HTMLNode("head")
        self.body_root = HTMLNode("body")
        self.current_node = None

    def get_current_depth(self) -> int:
        """Get the current nesting depth.

        Returns:
            The number of active nested element contexts (0 means at body root).
        """
        depth = 0
        node = self.current_node
        while node is not None and node != self.body_root:
            depth += 1
            node = node.parent
        return depth

    def validate_structure(self) -> bool:
        """Validate the document structure.

        Checks for common HTML document requirements:
        - Only one title in head
        - Charset meta appears first
        - Body contains valid structure

        Returns:
            True if document structure is valid, False otherwise.
        """
        # Check head structure
        title_count = sum(1 for child in self.head_root.children if child.tag == "title")
        if title_count > 1:
            return False

        # Check body structure
        return all(
            child.validate()
            for child in self.body_root.children
        )


class ElementProperty:
    """Descriptor for creating HTML elements with fluent interface.

    This class enables both method call and attribute access patterns for
    element creation, supporting both immediate creation and context managers.

    Attributes:
        container (Container): The parent container instance.
        tag (str): The HTML tag name this property represents.
        target (str): The target section ('head' or 'body').
        parent_node (Optional[HTMLNode]): Specific parent node if provided.
    """

    def __init__(
            self,
            container: 'Container',
            tag: str,
            target: str = "body",
            parent_node: Optional['HTMLNode'] = None
    ) -> None:
        """Initialize the element property.

        Args:
            container: The parent container instance.
            tag: The HTML tag name this property represents.
            target: The target section ('head' or 'body').
            parent_node: Optional specific parent node for all created elements.
        """
        self.container = container
        self.tag = tag
        self.target = target
        self.parent_node = parent_node or (
            self.container._context_stack[-1]
            if self.container._context_stack
            else None
        )

    def __call__(
            self,
            content: str = "",
            **kwargs: Any
    ) -> 'ElementProperty':
        """Create an element immediately.

        Args:
            content: Text content for the element.
            **kwargs: HTML attributes for the element.

        Returns:
            self for method chaining.

        Example:
            >>> div = container.body.div("Hello", class_="greeting")
            >>> div.ln()  # Make it render inline
        """
        parent = self._get_parent()
        self.node = parent.add_child(self.tag, content, kwargs)
        return self

    def __enter__(self) -> 'HTMLProxy':
        """Enter a context manager for nested element creation.

        Returns:
            A new HTMLProxy for the created element.

        Example:
            >>> with container.body.div(class_="container") as div:
            ...     div.p("Nested paragraph")
        """
        if not hasattr(self, 'node') or not self.node:
            self.__call__()  # Create node if not already created

        self.container._context_stack.append(self.node)
        self.container.com.html.current_node = self.node

        return HTMLProxy(
            container=self.container,
            target=self.target,
            current_node=self.node
        )

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context manager."""
        if self.container._context_stack:
            self.container._context_stack.pop()

    def ln(self) -> 'ElementProperty':
        """Set the element to render inline (without line breaks).

        Returns:
            self for method chaining.
        """
        if hasattr(self, 'node') and self.node:
            self.node.inline = True
        return self

    def attr(self, **kwargs: Any) -> 'ElementProperty':
        """Add or modify attributes after creation.

        Args:
            **kwargs: HTML attributes to add/modify.

        Returns:
            self for method chaining.

        Example:
            >>> container.body.div().attr(id="main", class_="container")
        """
        if hasattr(self, 'node') and self.node:
            self.node.attr.update(kwargs)
        return self

    def _get_parent(self) -> 'HTMLNode':
        """Get the appropriate parent node for element creation.

        Returns:
            The parent HTMLNode for new elements.

        Raises:
            RuntimeError: If no valid parent can be found.
        """
        if self.parent_node:
            return self.parent_node

        if self.target == "body":
            if self.container._context_stack:
                return self.container._context_stack[-1]
            return self.container.com.html.body_root

        if self.target == "head":
            return self.container.com.html.head_root

        raise RuntimeError(f"Invalid target section: {self.target}")

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<ElementProperty tag={self.tag!r} "
            f"target={self.target!r} parent={bool(self.parent_node)}>"
        )

    def remove(self, **attrs: Any) -> 'ElementProperty':
        """Delete element created by this attribute."""
        parent = self._get_parent()
        parent.children = [
            child for child in parent.children
            if not (child.tag == self.tag and all(child.attr.get(k) == v for k, v in attrs.items()))
        ]
        return self


class ElementPropertyWithParent(ElementProperty):
    """Specialized ElementProperty with fixed parent node."""

    def __init__(
            self,
            container: 'Container',
            tag: str,
            target: str,
            parent_node: 'HTMLNode'
    ) -> None:
        """Initialize with a specific parent node.

        Args:
            container: The parent container instance.
            tag: The HTML tag name this property represents.
            target: The target section ('head' or 'body').
            parent_node: The fixed parent node for all created elements.
        """
        super().__init__(container, tag, target)
        self.parent_node = parent_node

    def __call__(
            self,
            content: str = "",
            **kwargs: Any
    ) -> 'ElementPropertyWithParent':
        """Create an element under the fixed parent.

        Args:
            content: Text content for the element.
            **kwargs: HTML attributes for the element.

        Returns:
            self for method chaining.
        """
        attr = kwargs if kwargs else None
        self.node = self.parent_node.add_child(self.tag, content, attr)
        return self


class CSS:
    """Manages CSS rules and keyframe animations for a component.

    This class handles both regular CSS rules and @keyframe animations,
    with support for vendor prefixing and clean rendering.

    Attributes:
        rules (List[str]): List of regular CSS rule strings.
        keyframes (List[str]): List of @keyframe animation strings.
    """

    # Properties that need vendor prefixes
    VENDOR_PREFIXED_PROPERTIES = {
        'background-clip': ['-webkit-'],
        'user-select': ['-webkit-', '-moz-', '-ms-'],
        'transition': ['-webkit-'],
        'transform': ['-webkit-'],
        'animation': ['-webkit-'],
        'appearance': ['-webkit-', '-moz-'],
        'backdrop-filter': ['-webkit-'],
        'clip-path': ['-webkit-'],
        'text-size-adjust': ['-webkit-', '-moz-', '-ms-']
    }

    def __init__(self) -> None:
        """Initialize a new CSS manager."""
        self.rules: List[str] = []
        self.keyframes: List[str] = []

    def _convert_property_name(self, name: str) -> str:
        """Convert Python-style property names to CSS format.

        Args:
            name: The property name to convert.

        Returns:
            The converted CSS property name.

        Examples:
            >>> _convert_property_name("font_size") -> "font-size"
            >>> _convert_property_name("_hover") -> ":hover"
        """
        if name.startswith('_'):
            return f":{name[1:]}"  # Convert _hover to :hover
        return name.replace('_', '-')

    def _add_vendor_prefixes(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Add vendor-prefixed versions of properties that need them.

        Args:
            properties: Dictionary of CSS properties.

        Returns:
            New dictionary with vendor-prefixed properties added.
        """
        prefixed_props = properties.copy()

        for prop, value in properties.items():
            if prop in self.VENDOR_PREFIXED_PROPERTIES:
                for prefix in self.VENDOR_PREFIXED_PROPERTIES[prop]:
                    prefixed_props[f"{prefix}{prop}"] = value

        return prefixed_props

    def add_rule(
            self,
            selector: str,
            properties: Dict[str, Any],
            media_query: Optional[str] = None
    ) -> None:
        """Add a CSS rule.

        Args:
            selector: The CSS selector (e.g., ".class", "#id", "element").
            properties: Dictionary of CSS properties.
            media_query: Optional media query wrapper (e.g., "@media (min-width: 800px)").

        Example:
            >>> css.add_rule(".btn", {"color": "red", "padding": "10px"})
            >>> css.add_rule("_hover", {"color": "blue"}, media_query="@media (hover: hover)")
        """
        properties = self._add_vendor_prefixes(properties)
        prop_str = "".join(
            f"    {self._convert_property_name(k)}: {v};\n"
            for k, v in properties.items()
        )

        rule = f"{selector} {{\n{prop_str}}}"

        if media_query:
            rule = f"{media_query} {{\n{rule}\n}}"

        self.rules.append(rule)

    def add_keyframes(
            self,
            name: str,
            frames: Dict[str, Dict[str, Any]],
            vendor_prefix: bool = True
    ) -> None:
        """Add a @keyframes animation.

        Args:
            name: The animation name.
            frames: Dictionary mapping percentages to properties.
            vendor_prefix: Whether to add vendor-prefixed versions.

        Example:
            >>> css.add_keyframes("fade-in", {
            ...     "0_": {"opacity": 0},
            ...     "100_": {"opacity": 1}
            ... })
        """

        def process_frame(percentage: str, props: Dict[str, Any]) -> str:
            prop_str = "".join(
                f"\t{self._convert_property_name(k)}: {v};\n"
                for k, v in props.items()
            )
            return f"    {percentage.replace('_', '')}% {{\n{prop_str}    }}"

        frames_str = "\n".join(
            process_frame(pct, self._add_vendor_prefixes(props))
            for pct, props in frames.items()
        )

        if vendor_prefix:
            self.keyframes.append(f"@keyframes {name} {{\n{frames_str}\n}}")

            for prefix in ['-webkit-', '-moz-', '-o-']:
                self.keyframes.append(
                    f"@{prefix}keyframes {name} {{\n{frames_str}\n}}"
                )
        else:
            self.keyframes.append(f"@keyframes {name} {{\n{frames_str}\n}}")

    def add_font_face(
            self,
            family: str,
            src: str,
            properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a @font-face rule.

        Args:
            family: The font family name.
            src: The font source URL or local name.
            properties: Additional font properties.
        """
        props = {
            "font-family": family,
            "src": src
        }
        if properties:
            props.update(properties)

        self.add_rule("@font-face", props)

    def render(self, minify: bool = False) -> str:
        """Render css with pretty mode."""
        if minify:
            return self._render_minified()
        return self._render_pretty()

    def _render_minified(self) -> str:
        """Minify output."""
        return "".join(rule.replace("\n", "").replace(" ", "")
                       for rule in (self.rules + self.keyframes))

    def _render_pretty(self) -> str:
        """Better ouput."""
        output = []

        if self.rules:
            output.extend(self._indent_rule(rule) for rule in self.rules)

        if self.keyframes:
            output.extend(self._indent_keyframe(kf) for kf in self.keyframes)

        return "\n".join(output)

    def _indent_rule(self, rule: str) -> str:
        """Add indentation to regular CSS rules."""
        lines = rule.splitlines()
        formatted = []
        for line in lines:
            if line.strip().startswith("}"):
                formatted.append("    " + line)
            else:
                formatted.append("    " + line)
        return "\n".join(formatted)

    def _indent_keyframe(self, keyframe: str) -> str:
        """Add indentation to keyframe animations."""
        lines = keyframe.splitlines()
        formatted = ["    " + lines[0]]
        for line in lines[1:-1]:
            formatted.append("        " + line.strip())
        formatted.append("    " + lines[-1])
        return "\n".join(formatted)

    def clear(self) -> None:
        """Clear all CSS rules and keyframes."""
        self.rules.clear()
        self.keyframes.clear()

    def __str__(self) -> str:
        """Render CSS with default formatting."""
        return self.render()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<CSS rules={len(self.rules)} keyframes={len(self.keyframes)}>"


class Component:
    """Core component class that manages HTML, CSS and JavaScript for a UI component.

    This class serves as the central integration point for all aspects of a web component,
    providing methods to build and render the complete component including:
    - HTML structure
    - CSS styles
    - JavaScript behavior

    Attributes:
        html (HTML): HTML document structure manager
        css (CSS): CSS rules and animations manager
        js (List[str]): List of JavaScript code blocks
        head_js (List[str]): JavaScript code blocks for document head
        metadata (Dict[str, Any]): Component metadata
    """

    def __init__(self) -> None:
        """Initialize a new component with empty HTML, CSS and JS."""
        self.html = HTML()
        self.css = CSS()
        self.js: List[str] = []
        self.head_js: List[str] = []
        self.metadata: Dict[str, Any] = {
            'version': '0.2.0',
            'dependencies': [],
            'author': None
        }

    def add_js(
            self,
            js_code: str,
            in_head: bool = False,
            **format_args: Any
    ) -> 'Component':
        """Add JavaScript code to the component.

        Args:
            js_code: The JavaScript code to add
            in_head: Whether to place in document head (True) or body (False)
            **format_args: Format arguments for the JS code (uses str.format())

        Returns:
            self for method chaining

        Example:
            >>> component.add_js("console.log('{message}');", message="Hello")
        """
        if format_args:
            formatted_js = js_code.format(**format_args)
        else:
            formatted_js = js_code
        if in_head:
            self.head_js.append(formatted_js)
        else:
            self.js.append(formatted_js)
        return self

    def add_external_script(
            self,
            src: str,
            async_: bool = False,
            defer: bool = False,
            in_head: bool = False
    ) -> 'Component':
        """Add an external JavaScript file reference.

        Args:
            src: URL of the external script
            async_: Whether to load asynchronously
            defer: Whether to defer loading
            in_head: Whether to place in document head

        Returns:
            self for method chaining
        """
        attrs = {
            'src': src,
            'async': async_ or None,
            'defer': defer or None
        }
        script_tag = self.html.add_head_element if in_head else self.html.add_body_element
        script_tag("script", "", attrs)
        return self

    def add_external_style(self, href: str, media: Optional[str] = None) -> 'Component':
        """Add an external CSS stylesheet reference.

        Args:
            href: URL of the stylesheet
            media: Optional media query for the stylesheet

        Returns:
            self for method chaining
        """
        attrs = {
            'rel': 'stylesheet',
            'href': href,
            'media': media
        }
        self.html.add_head_element("link", "", attrs)
        return self

    def add_metadata(self, key: str, value: Any) -> 'Component':
        """Add component metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            self for method chaining
        """
        self.metadata[key] = value
        return self

    def to_json(self) -> str:
        """Serialize component metadata to JSON.

        Returns:
            JSON string of component metadata
        """
        return json.dumps(self.metadata, indent=2)

    def render(self, minify_css: bool = False) -> str:
        """Render the complete component as HTML document.

        Args:
            minify_css: Whether to minify CSS output

        Returns:
            Complete HTML document string
        """
        head_output = self.html.render_head()
        body_output = self.html.render_body()
        css_output = self.css.render(minify=minify_css)
        head_js_output = "\n\t".join(self.head_js)
        body_js_output = "\n\t".join(self.js)

        parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            head_output,
            f"<style>\n{css_output}\n</style>" if css_output else "",
            f"<script>{head_js_output}</script>" if head_js_output else "",
            "</head>",
            "<body>",
            body_output,
            f"<script>\n\t{body_js_output}\n</script>" if body_js_output else "",
            "</body>",
            "</html>"
        ]

        return "\n".join(filter(None, parts))

    def validate(self) -> bool:
        """Validate the component structure.

        Returns:
            True if component is valid, False otherwise
        """
        return all([
            self.html.validate_structure(),
            not any("</script>" in js for js in self.js),  # Basic XSS check
            not any("</style>" in css for css in self.css.rules)
        ])

    def clear(self) -> None:
        """Reset the component to empty state."""
        self.html.clear()
        self.css.clear()
        self.js.clear()
        self.head_js.clear()
        self.metadata.clear()

    def __str__(self) -> str:
        """Render component with default settings."""
        return self.render()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<Component html_nodes={len(self.html.body_root.children)} "
            f"css_rules={len(self.css.rules)} js_blocks={len(self.js)}>"
        )


class HTMLProxy:
    """Proxy class for fluent HTML element creation and manipulation.

    This class provides a fluent interface for building HTML structures,
    supporting both method chaining and context manager patterns.

    Attributes:
        container (Container): Reference to parent container
        target (str): Target section ('head' or 'body')
        current_node (Optional[HTMLNode]): Current HTML node being manipulated
    """

    def __init__(
            self,
            container: 'Container',
            target: str = "body",
            current_node: Optional[HTMLNode] = None
    ) -> None:
        """Initialize the HTML proxy.

        Args:
            container: Parent container instance
            target: Target section ('head' or 'body')
            current_node: Current HTML node to proxy
        """
        self.container = container
        self.target = target
        self.current_node = current_node or (
            container._context_stack[-1]
            if container._context_stack
            else None
        )
        self._pending_tag: Optional[str] = None  # For __call__ support

    def __getattr__(self, tag: str) -> 'ElementProperty':
        """Dynamically create element properties for any HTML tag.

        Args:
            tag: HTML tag name to create

        Returns:
            ElementProperty for the requested tag

        Example:
            >>> proxy.div  # Returns ElementProperty for div
        """
        return ElementProperty(self.container, tag, self.target, self.current_node)

    def __setattr__(self, name: str, value: Union[str, Dict[str, Any]]) -> None:
        """Handle attribute assignment as HTML element creation (syntax sugar).

    Enables quick element creation without explicit method calls:
    - com.body.p = "content"  # Creates <p>content</p>
    - com.body.a = {"href": "/link", "content": "Click"}  # Creates <a href="/link">Click</a>

    Args:
        name: HTML tag name to create
        value: Either:
            - String content for the element
            - Dictionary of attributes (with optional 'content' key for element content)

    Raises:
        TypeError: If value is neither string nor dictionary
    """
        if name in ["container", "target", "current_node", "_pending_tag"]:
            super().__setattr__(name, value)
        else:
            if isinstance(value, str):
                element = self.__getattr__(name)
                element(value)
            elif isinstance(value, dict):
                element = self.__getattr__(name)
                element(**value)
            else:
                raise TypeError(f"Unsupported value type: {type(value)}")

    def __call__(self, content: str = "", **kwargs: Any) -> 'HTMLProxy':
        """Create an element using the pending tag from __getattr__.

        Args:
            content: Text content for the element
            **kwargs: HTML attributes

        Returns:
            self for method chaining

        Example:
            >>> proxy.div("Hello", class_="greeting")
        """
        if not self._pending_tag:
            raise RuntimeError("No tag pending - use attribute access first")

        element = self.__getattr__(self._pending_tag)
        element(content, **kwargs)
        self._pending_tag = None
        return self

    def __iadd__(self, content: Union[str, int, float]) -> 'HTMLProxy':
        """Add text content to current node using += operator.

        Args:
            content: Text content to add

        Returns:
            self for method chaining

        Example:
            >>> proxy += "Some text"
        """
        if not isinstance(content, (str, int, float)):
            raise TypeError(f"Cannot add content of type {type(content)}")

        if self.current_node:
            self.current_node.add_child(None, str(content))
        return self

    def text(self, content: str) -> 'HTMLProxy':
        """Explicit method to add text content.

        Args:
            content: Text content to add

        Returns:
            self for method chaining

        Example:
            >>> proxy.text("Hello World")
        """
        return self.__iadd__(content)

    def ln(self) -> 'HTMLProxy':
        """Set current context to render inline (without line breaks).

        Returns:
            self for method chaining

        Example:
            >>> proxy.div().ln()  # Will render on one line
        """
        if self.current_node:
            self.current_node._force_inline = True
        return self

    def attr(self, **kwargs: Any) -> 'HTMLProxy':
        """Add/modify attributes on current node.

        Args:
            **kwargs: HTML attributes to set

        Returns:
            self for method chaining

        Example:
            >>> proxy.div().attr(id="main", class_="container")
        """
        if self.current_node:
            self.current_node.attr.update(kwargs)
        return self

    def __enter__(self) -> 'HTMLProxy':
        """Enter context manager, pushing current node to stack.

        Returns:
            self for continued operations

        Example:
            >>> with proxy.div() as div:
            ...     div.p("Nested paragraph")
        """
        if self.current_node:
            self.container._context_stack.append(self.current_node)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager, popping node from stack."""
        if self.container._context_stack:
            self.container._context_stack.pop()

    def parent(self) -> 'HTMLProxy':
        """Get proxy for parent node.

        Returns:
            New HTMLProxy for parent node

        Raises:
            RuntimeError: If no parent exists
        """
        if not self.current_node or not self.current_node.parent:
            raise RuntimeError("No parent node available")

        return HTMLProxy(
            self.container,
            self.target,
            self.current_node.parent
        )

    def root(self) -> 'HTMLProxy':
        """Get proxy for root node (head or body).

        Returns:
            New HTMLProxy for root node
        """
        root_node = (
            self.container.com.html.head_root
            if self.target == "head"
            else self.container.com.html.body_root
        )
        return HTMLProxy(self.container, self.target, root_node)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<HTMLProxy target={self.target!r} "
            f"current_tag={self.current_node.tag if self.current_node else None}>"
        )

    def remove(self, tag: Optional[str] = None, **attrs: Any) -> 'HTMLProxy':
        """Remove element"""
        parent = self.current_node or (
            self.container.com.html.head_root 
            if self.target == "head" 
            else self.container.com.html.body_root
        )
        
        tag_to_remove = tag or self._pending_tag
        
        keep_children = []
        for child in parent.children:
            if not isinstance(child, HTMLNode):
                keep_children.append(child)
                continue
            tag_match = (tag_to_remove is None) or (child.tag == tag_to_remove)
            attrs_match = all(child.attr.get(k) == v for k, v in attrs.items())
            if not (tag_match and attrs_match):
                keep_children.append(child)
        parent.children = keep_children
        return self


class ChainBuilder:
    """Chainable builder for HTML elements with fluent interface.

    This class enables method chaining for element creation and manipulation,
    supporting both immediate creation and context manager patterns.

    Attributes:
        proxy (HTMLProxy): The parent HTMLProxy instance
        tag (str): The HTML tag being built
    """

    def __init__(self, proxy: HTMLProxy, tag: str) -> None:
        """Initialize the chain builder.

        Args:
            proxy: Parent HTMLProxy instance
            tag: HTML tag name to build
        """
        self.proxy = proxy
        self.tag = tag
        self._pending_attrs: Optional[Dict[str, Any]] = None

    def __call__(self, content: str = "", **kwargs: Any) -> HTMLProxy:
        """Create the element and return a new proxy for it.

        Args:
            content: Text content for the element
            **kwargs: HTML attributes

        Returns:
            New HTMLProxy for the created element

        Example:
            >>> builder("Hello", class_="greeting")
        """
        # Combine pending attributes from attr() call if any
        attrs = self._pending_attrs or {}
        attrs.update(kwargs)

        # Create the element
        new_node = self.proxy.current_node.add_child(
            self.tag,
            content,
            attrs if attrs else None
        )

        # Reset pending state
        self._pending_attrs = None

        return HTMLProxy(
            container=self.proxy.container,
            target=self.proxy.target,
            current_node=new_node
        )

    def attr(self, **kwargs: Any) -> 'ChainBuilder':
        """Set attributes that will be applied on next __call__.

        Args:
            **kwargs: HTML attributes to set

        Returns:
            self for method chaining

        Example:
            >>> builder.attr(id="main").attr(class_="container")("Content")
        """
        if self._pending_attrs is None:
            self._pending_attrs = {}
        self._pending_attrs.update(kwargs)
        return self

    def ln(self) -> 'ChainBuilder':
        """Mark element to render inline (without line breaks).

        Returns:
            self for method chaining

        Example:
            >>> builder.ln()("Inline content")
        """
        if self.proxy.current_node:
            self.proxy.current_node.inline = True
        return self

    def __enter__(self) -> HTMLProxy:
        """Enter context manager - creates element and returns proxy.

        Returns:
            New HTMLProxy for the created element

        Example:
            >>> with builder.div() as div:
            ...     div.p("Nested content")
        """
        # Create element with any pending attributes
        element = self.__call__(**self._pending_attrs if self._pending_attrs else {})
        self._pending_attrs = None

        # Push to context stack
        self.proxy.container._context_stack.append(element.current_node)
        return element

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager - pops node from stack."""
        if self.proxy.container._context_stack:
            self.proxy.container._context_stack.pop()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<ChainBuilder tag={self.tag!r} pending_attrs={bool(self._pending_attrs)}>"


class CSSProxy:
    """Proxy class for fluent CSS rule creation with selector nesting support.

    Provides a Pythonic interface for defining CSS rules with support for:
    - Regular selectors (classes, IDs, elements)
    - Pseudo-classes and pseudo-elements
    - Media queries
    - Keyframe animations
    - Vendor prefixing

    Attributes:
        container (Container): Parent container instance
        _current_selector (Optional[str]): Current selector for nested rules
        _media_query (Optional[str]): Current media query context
    """

    def __init__(self, container: 'Container') -> None:
        """Initialize the CSS proxy.

        Args:
            container: Parent container instance
        """
        self.container = container
        self._current_selector: Optional[str] = None
        self._media_query: Optional[str] = None
        self._nesting_stack: List[str] = []

    def __getattr__(self, name: str) -> Callable[..., None]:
        """Handle CSS class selectors via attribute access.

        Args:
            name: Attribute name representing selector

        Returns:
            Callable that accepts CSS properties

        Example:
            >>> css.container(width="100%")  # Creates .container rule
        """
        if name.startswith('_'):
            # Handle pseudo-classes and pseudo-elements
            selector = f".{name[1:]}" if not name.startswith('__') else f"::{name[2:]}"
        else:
            # Regular class selector
            selector = f"{name}"

        def add_rule(**properties: Any) -> None:
            self._add_rule(selector, properties)

        return add_rule

    def __getitem__(self, selector: str) -> Callable[..., None]:
        """Handle arbitrary selectors via item access.

        Args:
            selector: CSS selector string

        Returns:
            Callable that accepts CSS properties

        Example:
            >>> css["header > nav"](display="flex")
        """

        def add_rule(**properties: Any) -> None:
            self._add_rule(selector, properties)

        return add_rule

    def _add_rule(self, selector: str, properties: Dict[str, Any]) -> None:
        """Internal method to add CSS rule with current context.

        Args:
            selector: CSS selector
            properties: CSS properties dictionary
        """
        full_selector = self._build_full_selector(selector)
        self.container.com.css.add_rule(
            full_selector,
            properties,
            media_query=self._media_query
        )

    def _build_full_selector(self, selector: str) -> str:
        """Build complete selector with nesting context.

        Args:
            selector: Base selector

        Returns:
            Fully qualified selector with parent selectors
        """
        if not self._nesting_stack:
            return selector

        parent_selectors = [
            s.strip()
            for s in self._nesting_stack[-1].split(',')
        ]

        current_selectors = [
            s.strip()
            for s in selector.split(',')
        ]

        parts = []
        for parent in parent_selectors:
            for current in current_selectors:
                if current.startswith('&'):
                    # Parent reference replacement
                    parts.append(current.replace('&', parent))
                elif current.startswith(':'):
                    # Pseudo-class/element
                    parts.append(f"{parent}{current}")
                else:
                    # Descendant
                    parts.append(f"{parent} {current}")

        return ', '.join(parts)

    def media(self, query: str) -> 'CSSProxy':
        """Create a media query context.

        Args:
            query: Media query string

        Returns:
            New CSSProxy instance with media query context

        Example:
            >>> with css.media("(min-width: 768px)"):
            ...     css.container(width="80%")
        """
        new_proxy = CSSProxy(self.container)
        new_proxy._media_query = query
        new_proxy._nesting_stack = self._nesting_stack.copy()
        return new_proxy

    def nest(self, selector: str) -> 'CSSProxy':
        """Create a nested selector context.

        Args:
            selector: Base selector for nesting

        Returns:
            New CSSProxy instance with nesting context

        Example:
            >>> with css.nest(".container"):
            ...     css.child(background="white")  # Creates .container .child
        """
        new_proxy = CSSProxy(self.container)
        new_proxy._media_query = self._media_query
        new_proxy._nesting_stack = self._nesting_stack + [selector]
        return new_proxy

    def keyframes(self, name: str) -> Callable[..., None]:
        """Define keyframe animations.

        Args:
            name: Animation name

        Returns:
            Callable that accepts frame definitions

        Example:
            >>> css.keyframes("fadeIn")({
            ...     "0_": {"opacity": 0},
            ...     "100_": {"opacity": 1}
            ... })
        """

        def add_keyframes(frames: Dict[str, Dict[str, Any]]) -> None:
            self.container.com.css.add_keyframes(name, frames)

        return add_keyframes

    def font_face(self, **properties: Any) -> None:
        """Define @font-face rule.

        Args:
            **properties: Font properties including required 'font-family' and 'src'

        Example:
            >>> css.font_face(
            ...     font_family="MyFont",
            ...     src="url('myfont.woff2') format('woff2')",
            ...     font_weight="bold"
            ... )
        """
        self.container.com.css.add_font_face(
            family=properties.pop('font_family'),
            src=properties.pop('src'),
            properties=properties
        )

    def __enter__(self) -> 'CSSProxy':
        """Enter context manager - maintains current state."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager - no cleanup needed."""
        pass

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<CSSProxy nesting_depth={len(self._nesting_stack)} "
            f"media_query={self._media_query or 'None'}>"
        )


class JSProxy:
    """Proxy class for fluent JavaScript code generation with DOM and API helpers.

    Provides a Pythonic interface for:
    - DOM manipulation and event handling
    - Fetch API wrappers
    - Animation control
    - State management
    - Custom script injection

    Attributes:
        container (Container): Parent container instance
        _event_handlers (List[str]): Tracked event handlers
        _state_vars (Dict[str, Any]): Tracked state variables
    """

    def __init__(self, container: 'Container') -> None:
        """Initialize the JS proxy.

        Args:
            container: Parent container instance
        """
        self.container = container
        self._event_handlers: List[str] = []
        self._state_vars: Dict[str, str] = {}

    def __call__(self, js_code: str, **format_args: Any) -> 'JSProxy':
        """Directly add JavaScript code.

        Args:
            js_code: JavaScript code to add
            **format_args: Format arguments for the code

        Returns:
            self for method chaining

        Example:
            >>> js("console.log('{message}');", message="Hello")
        """
        formatted = js_code.format(**format_args)
        self.container.com.add_js(formatted)
        return self

    def on(
            self,
            event: str,
            selector: str,
            handler: Union[str, Callable[[], str]],
            options: Optional[Union[Dict[str, Any], str]] = None
    ) -> 'JSProxy':
        """Add event listener to DOM elements.

        Args:
            event: Event type (e.g., 'click', 'mouseenter')
            selector: CSS selector for target elements
            handler: JS code or function returning JS code
            options: Listener options or options object as JS string

        Returns:
            self for method chaining

        Example:
            >>> js.on("click", ".btn", "alert('Clicked!')")
            >>> js.on("submit", "form", handleSubmit, options={"once": True})
        """
        handler_code = handler() if callable(handler) else handler
        options_str = (
            json.dumps(options)
            if isinstance(options, dict)
            else options or 'false'
        )

        code = f"""
        document.querySelectorAll('{selector}').forEach(el => {{
            el.addEventListener('{event}', (e) => {{
                {handler_code}
            }}, {options_str});
        }});"""

        self._event_handlers.append(code)
        self.container.com.add_js(code)
        return self

    def on_click(self, selector: str, handler: Union[str, Callable[[], str]]) -> 'JSProxy':
        """Shortcut for click event listeners.

        Args:
            selector: CSS selector
            handler: JS code or function returning JS code

        Returns:
            self for method chaining
        """
        return self.on('click', selector, handler)

    def on_submit(self, selector: str, handler: Union[str, Callable[[], str]],
                  prevent_default: bool = True) -> 'JSProxy':
        """Shortcut for form submit handlers with preventDefault option.

        Args:
            selector: Form selector
            handler: JS code or function returning JS code
            prevent_default: Whether to call preventDefault()

        Returns:
            self for method chaining
        """
        wrapper = f"e.preventDefault(); {handler}" if prevent_default else handler
        return self.on('submit', selector, wrapper)

    def fetch(
            self,
            url: str,
            config: Optional[Dict[str, Any]] = None,
            on_success: Optional[Union[str, Callable[[], str]]] = None,
            on_error: Optional[Union[str, Callable[[], str]]] = None,
            on_finally: Optional[Union[str, Callable[[], str]]] = None
    ) -> 'JSProxy':
        """Add Fetch API call with handlers.

        Args:
            url: Endpoint URL
            config: Fetch config dictionary
            on_success: Success handler JS code
            on_error: Error handler JS code
            on_finally: Finally handler JS code

        Returns:
            self for method chaining

        Example:
            >>> js.fetch("/api/data",
            ...     {"method": "GET"},
            ...     on_success="console.log(data)",
            ...     on_error="console.error(error)"
            ... )
        """
        config_str = json.dumps(config or {'method': 'GET'})
        success_code = on_success() if callable(on_success) else on_success or ''
        error_code = on_error() if callable(on_error) else on_error or ''
        finally_code = on_finally() if callable(on_finally) else on_finally or ''

        code = f"""
        fetch('{url}', {config_str})
            .then(response => {{
                if (!response.ok) throw new Error('HTTP error ' + response.status);
                return response.json();
            }})"""

        if success_code:
            code += f".then(data => {{ {success_code} }})"
        if error_code:
            code += f".catch(error => {{ {error_code} }})"
        if finally_code:
            code += f".finally(() => {{ {finally_code} }})"

        code += ";"

        self.container.com.add_js(code)
        return self

    def animate(
            self,
            selector: str,
            keyframes: Dict[str, Dict[str, Any]],
            options: Dict[str, Any]
    ) -> 'JSProxy':
        """Add Web Animations API animation.

        Args:
            selector: CSS selector for target elements
            keyframes: Animation keyframes dictionary
            options: Animation options dictionary

        Returns:
            self for method chaining

        Example:
            >>> js.animate(".box",
            ...     {"0_": {"opacity": 0}, "100_": {"opacity": 1}},
            ...     {"duration": 1000}
            ... )
        """
        keyframes_str = json.dumps(keyframes, indent=2).replace('"', '')
        options_str = json.dumps(options, indent=2).replace('"', '')

        code = f"""
        document.querySelectorAll('{selector}').forEach(el => {{
            el.animate({keyframes_str}, {options_str});
        }});"""

        self.container.com.add_js(code)
        return self

    def state(self, initial_value: Any = None, var_name: Optional[str] = None) -> 'JSState':
        """Create managed state variable.

        Args:
            initial_value: Initial state value
            var_name: Optional custom variable name

        Returns:
            JSState helper for state management

        Example:
            >>> counter = js.state(0)
            >>> counter.set(1)
            >>> counter.update("prev => prev + 1")
        """
        name = var_name or f"state_{len(self._state_vars)}"
        if initial_value is not None:
            init_code = f"let {name} = {json.dumps(initial_value)};"
            self.container.com.add_js(init_code)

        self._state_vars[name] = name
        return JSState(self, name)

    def component(self, name: str, definition: str) -> 'JSProxy':
        """Add custom element/component definition.

        Args:
            name: Custom element name (must contain hyphen)
            definition: JS class definition

        Returns:
            self for method chaining

        Example:
            >>> js.component("my-counter", \"\"\"
            ... class extends HTMLElement {
            ...   connectedCallback() {
            ...     this.innerHTML = `<button>Click me</button>`;
            ...   }
            ... }
            ... customElements.define('my-counter', MyCounter);\"\"\")
        """
        if '-' not in name:
            raise ValueError("Custom element name must contain hyphen")

        code = f"""
        class {name.title().replace('-', '')} {definition}
        customElements.define('{name}', {name.title().replace('-', '')});
        """

        self.container.com.add_js(code, in_head=True)
        return self

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<JSProxy events={len(self._event_handlers)} states={len(self._state_vars)}>"


class JSState:
    """Helper class for managed JavaScript state."""

    def __init__(self, proxy: JSProxy, name: str) -> None:
        """Initialize with proxy and variable name."""
        self.proxy = proxy
        self.name = name

    def get(self) -> str:
        """Get the state variable name for use in JS code.

        Returns:
            JS variable name string
        """
        return self.name

    def set(self, value: Any) -> 'JSState':
        """Set state value.

        Args:
            value: New state value

        Returns:
            self for method chaining
        """
        self.proxy(f"{self.name} = {json.dumps(value)};")
        return self

    def update(self, updater: str) -> 'JSState':
        """Update state with transformation function.

        Args:
            updater: JS function expression (e.g., "prev => prev + 1")

        Returns:
            self for method chaining
        """
        self.proxy(f"{self.name} = {updater}({self.name});")
        return self

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<JSState {self.name}>"


class MetaProxy:
    """Proxy class for fluent HTML meta tag management with common presets.

    Provides both generic meta tag creation and shortcuts for common meta tags:
    - Viewport
    - Charset
    - Open Graph
    - Twitter Cards
    - SEO descriptions
    - HTTP-equiv headers

    Attributes:
        container (Container): Parent container instance
    """

    def __init__(self, container: 'Container') -> None:
        """Initialize the meta proxy.

        Args:
            container: Parent container instance
        """
        self.container = container

    def __call__(self, **kwargs: Any) -> 'MetaProxy':
        """Create a generic meta tag.

        Args:
            **kwargs: Meta tag attributes

        Returns:
            self for method chaining

        Example:
            >>> meta(name="description", content="Page description")
        """
        # Special handling for boolean attributes
        processed_attrs = {
            k: ('' if v is True else v)
            for k, v in kwargs.items()
        }
        self.container.com.html.add_head_element("meta", "", processed_attrs)
        return self

    def viewport(self, content: str = "width=device-width, initial-scale=1.0") -> 'MetaProxy':
        """Set viewport meta tag.

        Args:
            content: Viewport content string

        Returns:
            self for method chaining

        Example:
            >>> meta.viewport()  # Default
            >>> meta.viewport("width=1200")  # Custom
        """
        return self(name="viewport", content=content)

    def charset(self, encoding: str = "UTF-8") -> 'MetaProxy':
        """Set charset meta tag.

        Args:
            encoding: Character encoding

        Returns:
            self for method chaining

        Example:
            >>> meta.charset()  # Default UTF-8
        """
        return self(charset=encoding)

    def description(self, content: str) -> 'MetaProxy':
        """Set page description meta tag.

        Args:
            content: Description content

        Returns:
            self for method chaining

        Example:
            >>> meta.description("My page description")
        """
        return self(name="description", content=content)

    def keywords(self, *keywords: str) -> 'MetaProxy':
        """Set keywords meta tag from multiple arguments.

        Args:
            *keywords: Variadic keyword arguments

        Returns:
            self for method chaining

        Example:
            >>> meta.keywords("python", "web", "development")
        """
        return self(name="keywords", content=", ".join(keywords))

    def http_equiv(self, equiv: str, content: str) -> 'MetaProxy':
        """Set http-equiv meta tag.

        Args:
            equiv: http-equiv value (e.g., "X-UA-Compatible")
            content: Associated content

        Returns:
            self for method chaining

        Example:
            >>> meta.http_equiv("X-UA-Compatible", "IE=edge")
        """
        return self(http_equiv=equiv, content=content)

    def og(self, property_name: str, content: str) -> 'MetaProxy':
        """Set Open Graph protocol meta tag.

        Args:
            property_name: OG property name (e.g., "title", "image")
            content: Property content

        Returns:
            self for method chaining

        Example:
            >>> meta.og("title", "My Page Title")
        """
        return self(property=f"og:{property_name}", content=content)

    def twitter(self, name: str, content: str) -> 'MetaProxy':
        """Set Twitter Card meta tag.

        Args:
            name: Twitter property name (e.g., "card", "title")
            content: Property content

        Returns:
            self for method chaining

        Example:
            >>> meta.twitter("card", "summary_large_image")
        """
        return self(name=f"twitter:{name}", content=content)

    def refresh(self, seconds: int, url: Optional[str] = None) -> 'MetaProxy':
        """Set refresh meta tag.

        Args:
            seconds: Number of seconds before refresh
            url: Optional URL to redirect to

        Returns:
            self for method chaining

        Example:
            >>> meta.refresh(5)  # Refresh after 5 seconds
            >>> meta.refresh(0, "https://example.com")  # Immediate redirect
        """
        content = f"{seconds}" if url is None else f"{seconds};url={url}"
        return self(http_equiv="refresh", content=content)

    def author(self, name: str) -> 'MetaProxy':
        """Set author meta tag.

        Args:
            name: Author name

        Returns:
            self for method chaining

        Example:
            >>> meta.author("John Doe")
        """
        return self(name="author", content=name)

    def robots(self, content: str = "index, follow") -> 'MetaProxy':
        """Set robots meta tag.

        Args:
            content: Robots directives

        Returns:
            self for method chaining

        Example:
            >>> meta.robots()  # Default allow indexing
            >>> meta.robots("noindex")  # Disallow indexing
        """
        return self(name="robots", content=content)

    def theme_color(self, color: str) -> 'MetaProxy':
        """Set theme-color meta tag.

        Args:
            color: CSS color value

        Returns:
            self for method chaining

        Example:
            >>> meta.theme_color("#4285f4")
        """
        return self(name="theme-color", content=color)

    def verification(self, service: str, content: str) -> 'MetaProxy':
        """Set site verification meta tag.

        Args:
            service: Verification service (google, bing, etc.)
            content: Verification code

        Returns:
            self for method chaining

        Example:
            >>> meta.verification("google", "ABC123")
        """
        return self(name=f"{service}-site-verification", content=content)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<MetaProxy>"


class FormProxy:
    """Proxy class for fluent HTML form creation with validation and submission handling.

    Provides specialized methods for:
    - Form creation with common attributes
    - Input field generation with types
    - Form validation patterns
    - Submission handling
    - CSRF protection

    Attributes:
        container (Container): Parent container instance
        _current_form (Optional[HTMLNode]): Currently active form node
    """

    def __init__(self, container: 'Container') -> None:
        """Initialize the form proxy.

        Args:
            container: Parent container instance
        """
        self.container = container
        self._current_form: Optional[HTMLNode] = None
        self._field_names: List[str] = []

    def __call__(self, **kwargs: Any) -> 'HTMLProxy':
        """Create a form with standard attributes.

        Args:
            **kwargs: Form attributes (action, method, etc.)

        Returns:
            HTMLProxy for the created form

        Example:
            >>> form(action="/submit", method="POST")
        """
        attrs = {
            'method': 'POST',  # Default method
            **kwargs
        }
        self._current_form = self.container.com.html.add_body_element("form", "", attrs)
        self._field_names = []
        return self.container.body.current(form=self._current_form)

    def input_field(
            self,
            name: str,
            type_: str = "text",
            label: Optional[str] = None,
            **kwargs: Any
    ) -> 'FormProxy':
        """Create a form input field with optional label.

        Args:
            name: Field name attribute
            type_: Input type (text, email, password, etc.)
            label: Optional label text
            **kwargs: Additional input attributes

        Returns:
            self for method chaining

        Example:
            >>> form.input_field("username", label="Username")
            >>> form.input_field("password", type_="password", required=True)
        """
        if self._current_form is None:
            self()  # Auto-create form if none exists

        if label:
            self._current_form.add_child("label", label, {"for": name})

        attrs = {
            "name": name,
            "type": type_,
            "id": name,
            **kwargs
        }
        self._current_form.add_child("input", "", attrs)
        self._field_names.append(name)
        return self

    def text_input(self, name: str, **kwargs: Any) -> 'FormProxy':
        """Shortcut for text input field.

        Args:
            name: Field name
            **kwargs: Additional attributes

        Returns:
            self for method chaining
        """
        return self.input_field(name, "text", **kwargs)

    def email_input(self, name: str, **kwargs: Any) -> 'FormProxy':
        """Shortcut for email input field with validation.

        Args:
            name: Field name
            **kwargs: Additional attributes

        Returns:
            self for method chaining
        """
        return self.input_field(name, "email", **kwargs)

    def password_input(self, name: str, **kwargs: Any) -> 'FormProxy':
        """Shortcut for password input field.

        Args:
            name: Field name
            **kwargs: Additional attributes

        Returns:
            self for method chaining
        """
        return self.input_field(name, "password", **kwargs)

    def number_input(self, name: str, **kwargs: Any) -> 'FormProxy':
        """Shortcut for number input field.

        Args:
            name: Field name
            **kwargs: Additional attributes

        Returns:
            self for method chaining
        """
        return self.input_field(name, "number", **kwargs)

    def checkbox(self, name: str, label: str, **kwargs: Any) -> 'FormProxy':
        """Create a checkbox input with label.

        Args:
            name: Field name
            label: Label text
            **kwargs: Additional attributes

        Returns:
            self for method chaining
        """
        if self._current_form is None:
            self()

        div = self._current_form.add_child("div", "", {"class": "checkbox"})
        attrs = {
            "type": "checkbox",
            "name": name,
            "id": name,
            "value": "on",
            **kwargs
        }
        div.add_child("input", "", attrs)
        div.add_child("label", label, {"for": name})
        self._field_names.append(name)
        return self

    def select(
            self,
            name: str,
            options: Dict[str, str],
            label: Optional[str] = None,
            **kwargs: Any
    ) -> 'FormProxy':
        """Create a select dropdown with options.

        Args:
            name: Field name
            options: Dictionary of {value: display_text}
            label: Optional label text
            **kwargs: Additional attributes

        Returns:
            self for method chaining
        """
        if self._current_form is None:
            self()

        if label:
            self._current_form.add_child("label", label, {"for": name})

        select = self._current_form.add_child("select", "", {"name": name, "id": name, **kwargs})
        for value, text in options.items():
            select.add_child("option", text, {"value": value})

        self._field_names.append(name)
        return self

    def textarea(
            self,
            name: str,
            label: Optional[str] = None,
            **kwargs: Any
    ) -> 'FormProxy':
        """Create a textarea field.

        Args:
            name: Field name
            label: Optional label text
            **kwargs: Additional attributes

        Returns:
            self for method chaining
        """
        if self._current_form is None:
            self()

        if label:
            self._current_form.add_child("label", label, {"for": name})

        self._current_form.add_child("textarea", "", {"name": name, "id": name, **kwargs})
        self._field_names.append(name)
        return self

    def submit(self, text: str = "Submit", **kwargs: Any) -> 'FormProxy':
        """Add a submit button to the form.

        Args:
            text: Button text
            **kwargs: Additional attributes

        Returns:
            self for method chaining
        """
        if self._current_form is None:
            self()

        self._current_form.add_child("button", text, {"type": "submit", **kwargs})
        return self

    def csrf_token(self, token: str) -> 'FormProxy':
        """Add a CSRF token hidden input.

        Args:
            token: CSRF token value

        Returns:
            self for method chaining
        """
        if self._current_form is None:
            self()

        self._current_form.add_child("input", "", {
            "type": "hidden",
            "name": "_csrf",
            "value": token
        })
        return self

    def validate(self, rules: Dict[str, Dict[str, Any]]) -> 'FormProxy':
        """Add client-side validation rules via data attributes.

        Args:
            rules: Dictionary mapping field names to validation rules

        Returns:
            self for method chaining

        Example:
            >>> form.validate({
            ...     "email": {"required": True, "type": "email"},
            ...     "password": {"min_length": 8}
            ... })
        """
        if self._current_form is None:
            return self

        for field_name, field_rules in rules.items():
            if field_name not in self._field_names:
                continue

            for node in self._current_form.children:
                if isinstance(node, HTMLNode) and node.attr.get('name') == field_name:
                    for rule, value in field_rules.items():
                        node.attr[f'data-validate-{rule}'] = str(value).lower()
        return self

    def handle_submit(self, handler: str) -> 'FormProxy':
        """Add JavaScript form submission handler.

        Args:
            handler: JavaScript code to handle form submission

        Returns:
            self for method chaining
        """
        if self._current_form is None:
            return self

        form_id = self._current_form.attr.get('id', f'form_{id(self._current_form)}')
        js_code = f"""
        document.querySelector('#{form_id}').addEventListener('submit', async (e) => {{
            e.preventDefault();
            {handler}
        }});
        """
        self.container.com.add_js(js_code)
        return self

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        form_id = self._current_form.attr.get('id') if self._current_form else None
        return f"<FormProxy fields={len(self._field_names)} form_id={form_id}>"


class Container:
    """Central container class that orchestrates all component building capabilities.

    This class serves as the main entry point for:
    - HTML structure generation
    - CSS styling
    - JavaScript behavior
    - Meta tag management
    - Form building

    Attributes:
        com (Component): The underlying component instance
        _context_stack (List[HTMLNode]): Stack for nested element contexts
        head (HTMLProxy): Proxy for head section operations
        body (HTMLProxy): Proxy for body section operations
        css (CSSProxy): Proxy for CSS operations
        js (JSProxy): Proxy for JavaScript operations
        meta (MetaProxy): Proxy for meta tag operations
        form (FormProxy): Proxy for form building operations
    """

    def __init__(self, component: Optional[Component] = None) -> None:
        """Initialize the container with all proxies.

        Args:
            component: Optional existing component to wrap
        """
        self.com = component if component else Component()
        self._context_stack: List['HTMLNode'] = []

        # Initialize all proxies
        self.head = HTMLProxy(self, "head", self.com.html.head_root)
        self.body = HTMLProxy(self, "body", self.com.html.body_root)
        self.css = CSSProxy(self)
        self.js = JSProxy(self)
        self.meta = MetaProxy(self)
        self.form = FormProxy(self)

    def render(self, minify_css: bool = False) -> str:
        """Render the complete component to HTML.

        Args:
            minify_css: Whether to minify CSS output

        Returns:
            Complete HTML document string
        """
        return self.com.render(minify_css=minify_css)

    def add_component(self, component: 'Component') -> 'Container':
        """Merge another component into this container.

        Args:
            component: Component to merge

        Returns:
            self for method chaining
        """
        # Merge HTML
        for child in component.html.head_root.children:
            self.com.html.head_root.children.append(child)
        for child in component.html.body_root.children:
            self.com.html.body_root.children.append(child)

        # Merge CSS
        self.com.css.rules.extend(component.css.rules)
        self.com.css.keyframes.extend(component.css.keyframes)

        # Merge JS
        self.com.js.extend(component.js)
        self.com.head_js.extend(component.head_js)

        return self

    def clear(self) -> None:
        """Reset the container to empty state."""
        self.com = Component()
        self._context_stack.clear()

        # Reinitialize proxies
        self.head = HTMLProxy(self, "head", self.com.html.head_root)
        self.body = HTMLProxy(self, "body", self.com.html.body_root)
        self.css = CSSProxy(self)
        self.js = JSProxy(self)
        self.meta = MetaProxy(self)
        self.form = FormProxy(self)

    def current_context(self) -> Optional['HTMLNode']:
        """Get the current nesting context node.

        Returns:
            Current HTMLNode if in nested context, None otherwise
        """
        return self._context_stack[-1] if self._context_stack else None

    def push_context(self, node: 'HTMLNode') -> None:
        """Push a node onto the context stack.

        Args:
            node: Node to push
        """
        self._context_stack.append(node)

    def pop_context(self) -> None:
        """Pop a node from the context stack."""
        if self._context_stack:
            self._context_stack.pop()

    def __enter__(self) -> 'Container':
        """Enable container as context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Clean up context manager."""
        pass

    def __str__(self) -> str:
        """Render component with default settings."""
        return self.render()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"<Container html_nodes={len(self.com.html.body_root.children)} "
            f"css_rules={len(self.com.css.rules)} js_blocks={len(self.com.js)}>"
        )

    def save_to_file(self, filename: str, minify_css: bool = False) -> None:
        """Render and save the component to a file.

        Args:
            filename: Path to output file
            minify_css: Whether to minify CSS output
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.render(minify_css=minify_css))

    def to_dict(self) -> Dict[str, Any]:
        """Convert component to serializable dictionary.

        Returns:
            Dictionary representation of the component
        """
        return {
            'html': {
                'head': [child.to_dict() for child in self.com.html.head_root.children],
                'body': [child.to_dict() for child in self.com.html.body_root.children]
            },
            'css': {
                'rules': self.com.css.rules,
                'keyframes': self.com.css.keyframes
            },
            'js': {
                'head': self.com.head_js,
                'body': self.com.js
            },
            'metadata': self.com.metadata
        }


com = Container()
