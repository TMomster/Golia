# Golia 前端代码生成器

---

English speaker are advised to read the [Readme.md](./Readme.md) file.

---

Golia 是一个前端代码生成器，旨在通过 Python 语言简化前端代码的编辑，减少重复性工作。

如果您发现了 Golia 存在的 bug 与错误，请您随时指出！

---

### 构建第一个 Golia 项目

Golia 项目的构建十分简单，它是基于完全纯 Python 语言开发的，因此不必安装第三方依赖。

在一个 Python 脚本中编写以下代码：

```python
from golia import *

com.head.title = "Golia Page" # 设置标题
com.head.meta("", charset="UTF-8") # 设置字符集

com.body.h1 = "Hello World" # 设置 h1

print(com.render()) # 输出 HTML
```

通过这段代码可以生成一个简单的 HTML 页面：

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

这段代码中，我们创建了一个容器 `com`，然后向容器中添加了标题和内容。最后，通过 `com.render()` 方法将容器中的内容渲染为 HTML。

通过配合使用文件流，您可以将输出的 HTML 直接写入文件中：

```python
from golia import *

# 本例是演示如何将输出写入文件，所以省略设计部分的代码
with open("index.html", "w") as f:
    f.write(com.render()) # 将输出写入文件
```

通过使用 Golia 可以快速生成规范的网页，而无需手动编写 HTML 标签。

---

### Golia 的语法

页面中各种各样的目标，Golia 将其统称为元素和容器。

通常，页面中的元素又分为一般元素和容器元素。

#### 1. Container 容器操作

Golia 的页面是基于容器构建的，容器是 HTML 页面的基本单元，它包含多个 HTML 元素。

Golia 提供了默认的 com 容器实现，通过使用 com 即可访问。

```python
com.head.title = "Golia Page"
```

Container 的作用主要是对代码职责进行划分：

```python
com.meta(charset="UTF-8")
com.head.title = "Golia Page"
com.body.h1 = "Hello World"
com.css.body(margin="0", padding="0")
com.js("alert('Hello')")
```

如上所示，当我们针对 Container 元素操作时，需要明确指定 head、body 等目标。这样，通过对 com 之后的名称就可以直接看出操作的元素属于哪个部分。

例如 `com.body.h1 = "Hello World"` ，无论之后的调用是什么，我们通过 body 就可以看出该元素属于 body 部分。

尽管有默认的容器实现，您仍然可以通过 Container 来创建新的容器。

```python
new_com = Container()
```

像这样，我们就构建了一个新的容器 new_com，它与 com 的功能完全一致，相当于一个新的页面。

如果要删除一个容器，只需要使用 del 即可。

```python
del com
```

在原理层面，Container 是对 Component 的封装，在构造器中有如下源代码：

```py
class Container:
    def __init__(self, component: Component):
        self.com = component
        ...
```

如果在构建对象时没有传入 Component，程序会自动创建 Component 的实例，所以下面的两个语句是相同的作用：

```py
new_com_1 = Container()
new_com_2 = Container(Component())
```

如果您需要对 Component 到 Container 之间的组装部分进行扩展修改，那么这段过程是可以拆解的。

#### 2. HTML 元素操作

##### 2.1 添加元素

在页面中添加一个 HTML 元素十分简单，只需要使用 `.` 即可。

```python
com.body.p("Hello World")
```

这样就可以在 body 中添加一个 p 元素，内容是 Hello World。

在 HTML 中等价于这样的定义：

```html
<body>
    <p>Hello World</p>
</body>
```

##### 2.2 添加属性

如果元素包含属性，在定义时可以直接以额外参数的形式进行编写：

```python
com.body.a("Click me", href="/link", target="_blank") 
```

对于多参数的元素，第一个参数是内容，其余的参数是属性。

```html
<body>
    <a href="/link" target="_blank">Click me</a>
</body>
```

##### 2.3 纯粹元素

如果一个元素不包含任何属性，就称为一个纯粹元素。

```python
com.body.h1("Hello World")
```

例如上示的 h1 元素，就是一个纯粹元素。

为纯粹元素赋值，可以使用更简洁的语法：

```python
com.body.h1("Hello World")  # 默认语法
com.body.h1 = "Hello World" # 纯粹元素语法
```

两种写法生成的结果是一致的：

```html
<body>
    <h1>Hello World</h1>
    <h1>Hello World</h1>
</body>
```

但是，如果纯粹元素既没有内容也没有属性，在调用时必须提供一个空括号，否则标签不会生成：

```python
com.body.custom_A()
com.body.custom_B
```

```html
<custom_A></custom_A>
```

这里的 `custom_A` 和 `custom_B` 都是自定义空元素，但是由于 `custom_B` 既不赋值也没有使用括号，所以在生成时被移除了。

##### 2.5 void 元素

void 元素是指不包含任何内容的元素，例如 img、br 等。

这些元素不包含内容，也被称为自闭合元素。

使用 Golia 声明 void 元素时，生成的代码中会自动进行识别：

```python
com.head.meta(charset="UTF-8")
com.body.img(src="logo.png", alt="Logo")
```

生成的代码：

```html
<head>
    <meta charset="UTF-8" />
    <img src="logo.png" alt="Logo" />
</head>
```

如果您误将 void 元素声明为普通元素，在元素中设置了内容，这些内容会在生成的 HTML 中被排除：

```python
com.head.link("多余的内容信息", rel="stylesheet", href="style.css")
```

生成的代码：

```html
<head>
    <link rel="stylesheet" href="style.css" />
</head>
```

##### 2.6 长内容声明

```python
com.body.p = ("利用 Python 的特性，"
              "您可以将一个长字符串分行声明。"
              "这样就可以在同一行输出，"
              "而不必担心影响格式。")
```

```html
<p>利用 Python 的特性，您可以将一个长字符串分行声明。这样就可以在同一行输出，而不必担心影响格式。</p>
```

##### 2.7 关键字冲突

在设置元素时，有时会不可避免地使用到 Python 的关键字，例如 class、del 等。

Golia 提供了一种解决方案，即在关键字前面添加一个下划线：

```python
com.body.class_()
com.body.p("text", class_="text")
```

```html
<class></class>
<p class="text">text</p>
```

#### 3. CSS 样式操作

##### 3.1 统一样式声明

Golia 默认的 CSS 样式声明是方括号语法，需要将相应的标签名写在方括号内：

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
        font_size: 2em;
    }
    a:hover {
        color: red;
    }
</style>
```

这种声明方式对所有选择器都有效，因此称为统一样式声明，也可以简称为统一声明。

##### 3.2 简化的标签选择器

如果要声明一个标签选择器，可以使用类似 HTML 元素的语法：

```py
com.css.body(    # 简化声明
    margin="0"
)
com.css["body"]( # 统一声明
    margin="0"
)
```

上示的两种写法生成的结果是相同的。

##### 3.3 简化的类选择器

类选择器的简化语法是在标签选择器的简化语法基础上拓展的，主要是在标识符之前添加了一个下划线：

```python
com.css[".title"]( # 统一声明
    color="blue",
    font_size="2em"
)
com.css._title(    # 简化声明
    color="blue",
    font_size="1.5em"
)
```

##### 3.4 关键帧动画声明

使用 keyframes 可以更方便地声明关键帧动画。

```python
com.css.keyframes("fade-in")({
    "0_": {"opacity": 0},
    "100_": {"opacity": 1}
})
```

#### 4. Javascript 脚本操作

##### 4.1 js 方法

通过 js 方法可以写入 js 脚本源码。

```python
com.js('alert("Golia")')
```

```html
<script>
    alert("In head")
</script>
```

从完整页面的生成结果中可以看出，通过 in_head 参数，可以将脚本插入 head 部分。

##### 4.2 增强式声明

Golia 提供声明式的 JavaScript 方法，可直接生成事件绑定、AJAX 请求等常见逻辑，无需手动编写完整脚本。

通过 `on_click` 方法，可以声明一个点击事件：

```python
com.js.on_click("#button", "alert('按钮被点击了')")
com.js.on_click(".item", "toggleItem(this)")
```

```html
<script>
    document.querySelector('#button').addEventListener('click', () => { alert('按钮被点击了') });
    document.querySelector('.item').addEventListener('click', () => { toggleItem(this) });
</script>
```

通过 fetch 方法生成数据请求代码，支持成功/失败回调：

```python
com.js.fetch(
    "/api/data",
    on_success="renderTable(data)",  # 成功回调
    on_error="showError(error)"      # 失败回调
)
```

```html
<script>
    fetch('/api/data').then(response => response.json()).then(data => renderTable(data)).catch(error => showError(error));
</script>
```

增强式声明的特性：

链式调用：所有方法均可通过 com.js 直接调用。

自动闭合：脚本默认插入到 <body> 末尾，若需插入到 <head> 可通过 in_head=True 参数控制。

扩展性：未来将支持更多方法（如 on_input、ajax 等）。

---

### Golia 的高级特性

#### 1. 基于上下文的嵌套

##### 1.1 基本语法

Golia 采用 with 上下文声明来处理嵌套的逻辑，在 with 中声明嵌套的级别：

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

在上示的声明中，我们通过 with 对 com.body.div 构建了上下文，通过 as 将容器标记为 d，然后就可以通过 d.p 访问到 div 元素下的 p 元素。

这是因为 com.body.div 已经声明了嵌套元素位于 com.body 下，所以 d.p 所声明的 p 元素会从 d 嵌套中继承元素的位置。

##### 1.2 多级嵌套

您可以在一个嵌套中建立新的子集嵌套，从而构成一个多级别的上下文结构：

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

Golia 允许对任何标签进行嵌套，也可以随时对元素添加属性：

```python
with com.body.custom_A() as c:
    with c.custom_B(klass="c2") as c2: # 隐藏父级的标识符 c
        c2.custom_C()
```

```html
<custom_A>
    <custom_B class="c2">
        <custom_C></custom_C>
    </custom_B>
</custom_A>
```

##### 1.3 纯粹元素嵌套

如果一个嵌套是纯粹元素，在 with 声明时可以省略括号：

```python
with com.body.div as d:
    d.p = "Golia"
```

```html
<div>
    <p>Golia</p>
</div>
```

##### 1.4 with 外的声明

声明了一个嵌套以后，如果它的标识符没有被覆盖，则可以在 with 外声明元素：

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

跨上下文的声明也是允许的，元素会对绑定的标识符进行识别：

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

这种语法使得子级元素的声明更简便，但为了保障 Golia 代码的可读性与规范性，应尽量避免在 with 以外声明子级元素。

##### 1.5 静态上下文

当我们多次声明一个元素的嵌套时，会被解析为几个相互独立的嵌套：

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

这是 Golia 对普通元素嵌套的行为。

除普通元素外，Golia 还提供了一些特殊的页面元素，它们的多次嵌套声明会被合并为一个：

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

这种特性适用于 body 和 head，它们被称为“静态元素”，它们的上下文也就称为“静态上下文”。

与一般元素的区别在于，一般的元素在每次声明时都会生成一个新的标签，而静态元素则相反，无论多少次声明都只对应一个标签。

静态上下文在使用时不必总是使用 with 声明，可以用更简单的方式来实现：

```python
b = com.body
b.p = "Hello World"
```

因为静态上下文是与页面容器绑定的，所以您可以直接使用它们来声明子级元素。

如果我们用 com.body 把 b 替换掉，就会发现，这和我们最开始介绍的 com.body.p 这种声明方式是一样的。 

我们再来回顾之前的基本元素声明方式，就会发现，默认的声明方式其实就是基于静态上下文实现的：

```python
com.body.p = "hello world"
```

我们使用的 com.body 和 com.head 就是页面的静态上下文元素。

##### 1.6 简单嵌套

有些时候，嵌套中可能只包含一个内容：

```python
with com.body.div as d:
    d.p = "Hello World"
```

这样的嵌套元素，我们就将其称为简单嵌套。

虽然 with 语法为复杂的嵌套提供了便利，但在一些简单嵌套模式下，例如：

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

像这样的多级简单嵌套，虽然我们连续声明了几层 with，但最终只是为了修饰一个内容，这种代码就显得有些臃肿累赘了。

因此，对于简单嵌套，Golia 提供了更简便的语法：

```python
com.body.big().strong().i = "bold"
```

像这样，通过链式语法，可以减少对 with 语句的使用，从而更简单快捷地声明简单嵌套元素。

我们也可以让嵌套元素包含属性：

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

利用 Python 的特性，我们可以将代码整理成更易读的形式：

```python
(com.body.div(klass="div1").
 div(klass="div2").
 div(klass="div3").
 p("paragraph", klass="p1"))
```

##### 1.7 追加声明

利用 `+=` 运算符，我们可以对已经声明的上下文追加内容：

```python
with com.body.p as p:
    p += "普通文本"
    p += "普通文本"
    p += "普通文本"
```

```html
<p>
    普通文本
    普通文本
    普通文本
</p>
```

这样，我们就可以声明一些更灵活的结构：

```python
with com.body.p as p:
    p += "普通文本"
    with p.del_() as d:
        d += "删除线文本"
    p += "普通文本" 
```

```html
<p>
    普通文本
    <del>
        删除线文本
    </del>
    普通文本
</p>
```

对于上下文元素，Golia 提供了一个行化输出方法，您只需要在上下文中调用 ln 方法即可：

```python
with com.body.p as p:
    p += "普通文本"
    with p.del_() as d:
        d += "删除线文本"
    p += "普通文本"
    p.ln()
```

```html
<p>普通文本<del>删除线文本</del>普通文本</p>
```

也可以针对特定的上下文行化：

```python
with com.body.p as p:
    p += "普通文本"
    with p.del_() as d:
        d += "删除线文本"
        d.ln()
    p += "普通文本"
```

```html
<p>
    普通文本
    <del>删除线文本</del>
    普通文本
</p>
```
