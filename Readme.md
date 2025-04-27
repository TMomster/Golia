# Golia Frontend Code Generator

---

如果您是中文使用者，请阅读[ReadmeCN.md](./ReadmeCN.md)

---

Golia is a frontend code generator designed to simplify the editing of frontend code through the Python language and reduce repetitive work.

If you find any bugs or errors in Golia, please share them with me at any time!

---

### Building Your First Golia Project

Building a Golia project is very simple. It is developed entirely in pure Python, so there is no need to install third-party dependencies.

Write the following code in a Python script:

```python
from golia import *

com.head.title = "Golia Page" # Set the title
com.head.meta("", charset="UTF-8") # Set the character encoding
```

This code generates a simple HTML page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Golia Page</title>
    <meta charset="UTF-8"></meta>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
```

In this code, we create a container `com`, then add a title and content to the container. Finally, we render the content of the container as HTML using the `com.render()` method.

By combining file streams, you can directly write the output HTML to a file:

```python
from golia import *

# This example demonstrates how to write the output to a file, so the design part of the code is omitted
with open("index.html", "w") as f:
    f.write(com.render()) # Write the output to a file
```

Using Golia, you can quickly generate standardized web pages without manually writing HTML tags.

---

### Golia Syntax

Golia refers to various items in a page as elements and containers.

Typically, elements in a page are divided into general elements and container elements.

#### 1. Container Operations

Golia's pages are constructed using containers, which are the basic units of an HTML page and contain multiple HTML elements.

Golia provides a default `com` container implementation, which can be accessed directly using `com`.

```python
com.head.title = "Golia Page"
```

The main role of a container is to divide code responsibilities:

```python
com.meta(charset="UTF-8")
com.head.title = "Golia Page"
com.body.h1 = "Hello World"
com.css.body(margin="0", padding="0")
com.js("alert('Hello')")
```

As shown above, when operating on container elements, it is necessary to specify the target clearly, such as `head` or `body`. This way, the element being operated on can be directly identified by the name following `com`.

For example, in `com.body.h1 = "Hello World"`, no matter what the subsequent call is, we can see that the element belongs to the `body` part through `body`.

Although there is a default container implementation, you can still create a new container using `Container`.

```python
new_com = Container()
```

In this way, we have built a new container `new_com`, which has the same functionality as `com`, equivalent to a new page.

If you want to delete a container, simply use `del`.

```python
del com
```

In terms of principles, `Container` is a wrapper for `Component`, with the following source code in the constructor:

```py
class Container:
    def __init__(self, component: Component):
        self.com = component
        ...
```

If no `Component` is passed when constructing the object, the program will automatically create an instance of `Component`. Therefore, the following two statements have the same effect:

```py
new_com_1 = Container()
new_com_2 = Container(Component())
```

If you need to extend or modify the assembly part between `Component` and `Container`, this process can be decomposed.

#### 2. HTML Element Operations

##### 2.1 Adding Elements

Adding an HTML element to a page is very simple; just use the dot syntax to access element properties.

```python
com.body.p("Hello World")
```

This adds a `p` element to the `body` with the content "Hello World".

In HTML, this is equivalent to:

```html
<body>
    <p>Hello World</p>
</body>
```

##### 2.2 Adding Attributes

If an element has attributes, they can be specified directly as additional parameters when defining the element:

```python
com.body.a("Click me", href="/link", target="_blank")
```

For elements with multiple parameters, the first parameter is the content, and the rest are attributes.

```html
<body>
    <a href="/link" target="_blank">Click me</a>
</body>
```

##### 2.3 Pure Elements

An element that does not contain any attributes is called a void element.

```python
com.body.h1("Hello World")
```

For example, the `h1` element above is a void element.

Assigning values to void elements can be done using a more concise syntax:

```python
com.body.h1("Hello World")  # Default syntax
com.body.h1 = "Hello World" # Void element syntax
```

Both methods produce the same result:

```html
<body>
    <h1>Hello World</h1>
    <h1>Hello World</h1>
</body>
```

However, if a void element has neither content nor attributes, an empty parenthesis must be provided when calling it; otherwise, the tag will not be generated:

```python
com.body.custom_A()
com.body.custom_B
```

```html
<custom_A></custom_A>
```

Here, both `custom_A` and `custom_B` are custom empty elements, but since `custom_B` neither assigns a value nor uses parentheses, it is removed during generation.

##### 2.5 Void Elements

Void elements are those that do not contain any content, such as `img`, `br`, etc.

These elements, which do not contain content, are also known as self-closing elements.

When declaring void elements using Golia, the generated code will automatically recognize them:

```python
com.head.meta(charset="UTF-8")
com.body.img(src="logo.png", alt="Logo")
```

Generated code:

```html
<head>
    <meta charset="UTF-8" />
    <img src="logo.png" alt="Logo" />
</head>
```

If you mistakenly declare a void element as a regular element and set content within it, this content will be excluded in the generated HTML:

```python
com.head.link("Excess content information", rel="stylesheet", href="style.css")
```

Generated code:

```html
<head>
    <link rel="stylesheet" href="style.css" />
</head>
```

##### 2.6 Long Content Declaration

```python
com.body.p = ("Using Python's features,"
              "you can declare a long string across multiple lines."
              "This allows you to output on the same line,"
              "without worrying about formatting issues.")
```

```html
<p>Using Python's features, you can declare a long string across multiple lines. This allows you to output on the same line, without worrying about formatting issues.</p>
```

##### 2.7 Keyword Conflicts

When setting elements, it is sometimes inevitable to use Python keywords, such as `class`, `del`, etc.

Golia provides a solution by adding an underscore before the keyword:

```python
com.body.class_()
com.body.p("text", class_="text")
```

```html
<class></class>
<p class="text">text</p>
```

---

#### 3. CSS Style Operations

##### 3.1 Unified Style Declaration

Golia's default CSS style declaration uses bracket syntax, which requires the corresponding tag name to be written within brackets:

```python
com.css[".title"](
    color="blue",
    font_size="2em"
)

com.css["a:hover"](
    color="red"
)
```

```html
<style>
    .title {
        color: blue;
        font-size: 2em;
    }
    a:hover {
        color: red;
    }
</style>
```

This declaration method is effective for all selectors, hence it is called unified style declaration, or simply unified declaration.

##### 3.2 Simplified Tag Selector

If you want to declare a tag selector, you can use a syntax similar to HTML elements:

```python
com.css.body(    # Simplified declaration
    margin="0"
)
com.css["body"]( # Unified declaration
    margin="0"
)
```

The above two methods produce the same result.

##### 3.3 Simplified Class Selector

The simplified syntax for class selectors is an extension of the simplified tag selector syntax, mainly by adding an underscore before the identifier:

```python
com.css[".title"]( # Unified declaration
    color="blue",
    font_size="2em"
)
com.css._title(    # Simplified declaration
    color="blue",
    font_size="1.5em"
)
```

##### 3.4 Keyframe Animation Declaration

Using `keyframes` makes it easier to declare keyframe animations.

```python
com.css.keyframes("fade-in")({
    "0%": {"opacity": 0},
    "100%": {"opacity": 1}
})
```

#### 4. JavaScript Script Operations

##### 4.1 js Method

The `js` method allows you to write JavaScript script source code directly.

```python
com.js('alert("Golia")')
```

```html
<script>
    alert("Golia");
</script>
```

#### 4.2 Enhanced Declaration

Golia provides declarative JavaScript methods that can directly generate common logic such as event binding and AJAX requests without manually writing the entire script.

Using the `on_click` method, you can declare a click event:

```python
com.js.on_click("#button", "alert('The button was clicked')")
com.js.on_click(".item", "toggleItem(this)")
```

```html
<script>
    document.querySelector('#button').addEventListener('click', () => { alert('The button was clicked') });
    document.querySelector('.item').addEventListener('click', () => { toggleItem(this) });
</script>
```

Using the `fetch` method to generate data request code, with support for success and error callbacks:

```python
com.js.fetch(
    "/api/data",
    on_success="renderTable(data)",  # Success callback
    on_error="showError(error)"      # Error callback
)
```

```html
<script>
    fetch('/api/data').then(response => response.json()).then(data => renderTable(data)).catch(error => showError(error));
</script>
```

Characteristics of enhanced declaration:

- **Chaining**: All methods can be directly called via `com.js`.
- **Extensibility**: More methods (such as `on_input`, `ajax`, etc.) will be supported in the future.

---

### Advanced Features of Golia

#### 1. Context-Based Nesting

##### 1.1 Basic Syntax

Golia uses the `with` context declaration to handle nested logic, specifying the level of nesting within the `with` block:

```python
with com.body.div() as d:
    d.p = "Golia"
    d.p = "Hello World"
```

```html
<div>
    <p>Golia</p>
    <p>Hello World</p>
</div>
```

In the above declaration, we use `with` to create a context for `com.body.div`, marking the container as `d` using `as`. We can then access the `p` element within the `div` using `d.p`.

This is because `com.body.div` has already declared that the nested element is under `com.body`, so the `p` element declared by `d.p` will inherit its position from the nested context of `d`.

##### 1.2 Multi-level Nesting

You can create new sub-nested contexts within a nested context, forming a multi-level context structure:

```python
with com.body.div() as d:
    d.p = "Outer div"
    with d.div() as d2:
        d2.p = "Inner div"
```

```html
<div>
    <p>Outer div</p>
    <div>
        <p>Inner div</p>
    </div>
</div>
```

Golia allows nesting for any tag and also permits adding attributes to elements at any time:

```python
with com.body.custom_A() as c:
    with c.custom_B(klass="c2") as c2: # Hides the parent identifier `c`
        c2.custom_C()
```

```html
<custom_A>
    <custom_B class="c2">
        <custom_C></custom_C>
    </custom_B>
</custom_A>
```

##### 1.3 Pure Element Nesting

If a nested context is a pure element, the parentheses can be omitted in the `with` declaration:

```python
with com.body.div as d:
    d.p = "Golia"
```

```html
<div>
    <p>Golia</p>
</div>
```

##### 1.4 Declarations Outside `with`

After declaring a nested context, if its identifier is not overwritten, you can declare elements outside the `with` block:

```python
with com.body.div() as d:
    pass

d.p = 'hello world'
```

```html
<div>
    <p>hello world</p>
</div>
```

Cross-context declarations are also allowed; elements will recognize their bound identifiers:

```python
with com.body.div() as d:
    d.p = "d.p in div D"

with com.body.div() as e:
    d.p = "d.p in div E"
    e.p = "e.p in div E"
```

```html
<div>
    <p>d.p in div D</p>
    <p>d.p in div E</p>
</div>
<div>
    <p>e.p in div E</p>
</div>
```

This syntax simplifies the declaration of child elements, but to ensure the readability and standardization of Golia code, it is recommended to avoid declaring child elements outside the `with` block as much as possible.

##### 1.5 Static Context

When declaring nested contexts for the same element multiple times, they will be parsed as separate, independent nests:

```python
with com.body.div() as d:
    d.p = "div 1"

with com.body.div() as d:
    d.p = "div 2"
```

```html
<div>
    <p>div 1</p>
</div>
<div>
    <p>div 2</p>
</div>
```

This is the behavior for regular element nesting in Golia.

In addition to regular elements, Golia provides some special page elements whose multiple nested declarations will be merged into one:

```python
with com.body as b:
    b.p = "Hello World"

with com.body as c:
    c.p = "Hello Golia"
```

```html
<body>
    <p>Hello World</p>
    <p>Hello Golia</p>
</body>
```

This feature applies to `body` and `head`, which are called "static elements," and their contexts are referred to as "static contexts."

Unlike regular elements, which generate a new tag each time they are declared, static elements behave differently: no matter how many times they are declared, they correspond to only one tag.

When using static contexts, it is not necessary to always declare them with `with`. A simpler approach can be used:

```python
b = com.body
b.p = "Hello World"
```

Since static contexts are bound to the page container, you can directly use them to declare child elements.

If we replace `b` with `com.body`, we will see that this is the same as the `com.body.p` declaration method we introduced at the beginning.

Reviewing the basic element declaration method again, we can see that the default declaration method is actually implemented based on static contexts:

```python
com.body.p = "hello world"
```

The `com.body` and `com.head` we use are the static context elements of the page.

##### 1.6 Simple Nesting

Sometimes, a nested context may contain only one element:

```python
with com.body.div as d:
    d.p = "Hello World"
```

Such nested elements are referred to as simple nests.

Although the `with` syntax provides convenience for complex nesting, in some simple nesting patterns, such as:

```python
with com.body as b:
    with b.big as big:
        with big.strong as strong:
            strong.i = "bold"
```

```html
<big>
    <strong>
        <i>bold</i>
    </strong>
</big>
```

In this multi-level simple nesting, even though we declared several layers of `with` in a row, it was ultimately just to decorate one piece of content. This code appears somewhat cumbersome and redundant.

Therefore, for simple nesting, Golia provides a more concise syntax:

```python
com.body.big().strong().i = "bold"
```

In this way, by using chain syntax, the use of `with` statements can be reduced, making it simpler and faster to declare simple nested elements.

We can also include attributes in nested elements:

```python
com.body.div(klass="div1").div(klass="div2").div(klass="div3").p("paragraph", klass="p1")
```

```html
<div class="div1">
    <div class="div2">
        <div class="div3">
            <p class="p1">paragraph</p>
        </div>
    </div>
</div>
```

Using Python's features, we can organize the code into a more readable form:

```python
(com.body.div(klass="div1").
 div(klass="div2").
 div(klass="div3").
 p("paragraph", klass="p1"))
```

##### 1.7 Append Declarations

Using the `+=` operator, we can append content to an already declared context:

```python
with com.body.p as p:
    p += "Normal text"
    p += "Normal text"
    p += "Normal text"
```

```html
<p>
    Normal text
    Normal text
    Normal text
</p>
```

In this way, we can declare more flexible structures:

```python
with com.body.p as p:
    p += "Normal text"
    with p.del_() as d:
        d += "Strikethrough text"
    p += "Normal text"
```

```html
<p>
    Normal text
    <del>
        Strikethrough text
    </del>
    Normal text
</p>
```

For context elements, Golia provides a line-breaking output method. You just need to call the `ln` method within the context:

```python
with com.body.p as p:
    p += "Normal text"
    with p.del_() as d:
        d += "Strikethrough text"
    p += "Normal text"
    p.ln()
```

```html
<p>Normal text<del>Strikethrough text</del>Normal text</p>
```

You can also line-break for specific contexts:

```python
with com.body.p as p:
    p += "Normal text"
    with p.del_() as d:
        d += "Strikethrough text"
        d.ln()
    p += "Normal text"
```

```html
<p>
    Normal text
    <del>Strikethrough text</del>
    Normal text
</p>
```