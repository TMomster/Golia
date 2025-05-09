# Gollback.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
import re

app = FastAPI()


def document_to_golia(html: str) -> str:
    """转换完整HTML文档到Golia代码"""
    code = [
        "from golia import Container",
        "com = Container()\n"
    ]

    # 文档类型处理
    if re.search(r'<!DOCTYPE html>', html):
        code.append("# 自动添加文档类型声明")

    # 提取主要结构
    head_content = re.search(r'<head>(.*?)</head>', html, re.DOTALL)
    body_content = re.search(r'<body>(.*?)</body>', html, re.DOTALL)

    # 处理head部分
    if head_content:
        code.append("\n# Head 部分")
        code.extend(_parse_section(head_content.group(1), 'head'))

    # 处理body部分
    if body_content:
        code.append("\n# Body 部分")
        code.extend(_parse_section(body_content.group(1), 'body'))

    # 添加渲染语句
    code.extend([
        "\n# 生成最终文档",
        "rendered = com.render()"
    ])

    return '\n'.join(code)


def _parse_section(content: str, section: str) -> list:
    """解析文档片段"""
    lines = []
    indent = 1
    stack = []

    # 匹配标签和文本
    pattern = re.compile(
        r'<(/?)(\w+)(.*?)(/?)>|([^<]+)',
        re.DOTALL
    )

    for match in pattern.finditer(content):
        tag_close, tag_name, attrs, self_close, text = match.groups()

        if text:  # 处理文本节点
            clean_text = text.strip().replace('\n', ' ')
            if clean_text:
                lines.append(f'{"    " * indent}com.{section}.text("{clean_text}")')
            continue

        if tag_close:  # 闭合标签
            if stack and stack[-1] == tag_name:
                stack.pop()
                indent = max(1, indent - 1)
            continue

        # 处理属性
        attr_str = _convert_attrs(attrs)

        # 生成代码
        lines.append(f'{"    " * indent}com.{section}.{tag_name}({attr_str})')

        if not self_close:  # 非自闭合标签
            stack.append(tag_name)
            indent += 1

    return lines


def _convert_attrs(attrs: str) -> str:
    """转换HTML属性到Python参数"""
    attr_map = {
        'class': 'klass',
        'for': 'for_',
        'async': 'async_',
        'type': 'type_'
    }

    attrs_dict = {}
    for name, value in re.findall(r'(\w+)=["\'](.*?)["\']', attrs):
        py_name = attr_map.get(name, name)
        attrs_dict[py_name] = value

    return ', '.join([f'{k}="{v}"' for k, v in attrs_dict.items()])


@app.post("/derender")
async def derender(html: str):
    try:
        return PlainTextResponse(document_to_golia(html))
    except Exception as e:
        raise HTTPException(400, detail=f"转换失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)