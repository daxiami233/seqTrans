import base64
import json
import subprocess
import cv2
import re
from openai import OpenAI
from prompt import detection_prompt
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url=os.getenv("MOONSHOT_BASE_URL"),
)

clickable_elements = []
clickable_elements_information = []


def add_information(element, i=0):
    information = {'pos': '', 'type': '', 'text': [], 'image': [], 'other': []}
    attributes = element.get('attributes', {})
    
    # 只为顶层元素设置位置和类型
    if i == 0:
        information['pos'] = attributes.get('bounds', '')
        information['type'] = attributes.get('type', '')
    
    # 收集文本和图片信息
    if attributes.get('text'):
        information['text'].append(attributes['text'])
    if attributes.get('type') == 'Image':
        information['image'].append('Image')
    
    # 收集其他有用信息
    for attr_name in ['checked', 'description', 'hint', 'id', 'key']:
        if attributes.get(attr_name):
            information['other'].append(attributes[attr_name])
    
    # 递归收集子元素信息
    if 'children' in element:
        for idx, child in enumerate(element['children']):
            child_information = add_information(child, i + 1)
            
            # 合并文本信息，避免重复
            for text_item in child_information['text']:
                if text_item not in information['text']:
                    information['text'].append(text_item)
            
            # 合并图片信息，避免重复
            for image_item in child_information['image']:
                if image_item not in information['image']:
                    information['image'].append(image_item)
            
            # 合并其他信息，限制数量为5个
            if len(information['other']) < 5:
                for other_item in child_information['other']:
                    if other_item not in information['other'] and len(information['other']) < 5:
                        information['other'].append(other_item)
    
    return information


def extract_clickable_elements(layout_data):
    """递归查找可点击元素，排除嵌套的可点击元素，但保留特定容器下的可点击元素"""
    # 检查当前节点
    attrs = layout_data.get("attributes", {})

    # 检查是否可点击
    is_clickable = attrs.get("clickable") == "true"
    is_enabled = attrs.get("enabled") == "true"
    is_visible = attrs.get("visible") == "true"
    # element_type = attrs.get("type", "")
    
    # 定义特殊容器类型列表，这些容器即使可点击，也应该检测其子元素
    # special_containers = ["NavRouter", "Stack", "Grid", "List"]
    
    # 判断当前元素是否为特殊容器
    # is_special_container = element_type in special_containers
    
    # 如果元素可点击、启用且可见，并且父元素不是可点击的（或父元素是特殊容器）
    if is_clickable and is_enabled and is_visible:
        information = add_information(layout_data)
        clickable_elements.append(information)
        
        # 只有当不是特殊容器时，才将当前元素标记为可点击传递给子元素
        # if not is_special_container:
        #     parent_clickable = True
        # else:
        #     # 对于特殊容器，不阻止子元素被检测
        #     parent_clickable = False
    
    # 递归处理子元素，传递父元素的可点击状态
    if 'children' in layout_data:
        for i, child in enumerate(layout_data['children']):
            # # 如果当前元素是特殊容器，则传递False给子元素，允许子元素被检测
            # child_parent_clickable = parent_clickable if not is_special_container else False
            extract_clickable_elements(child)


def layout():
    subprocess.run(
        [
            "hdc",
            "shell",
            "uitest",
            "dumpLayout",
            "-p",
            "/data/local/tmp/layout.json",
        ],
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "hdc",
            "file",
            "recv",
            "/data/local/tmp/layout.json",
            "resource/layout/layout.json",
        ],
        capture_output=True,
        text=True,
    )


def snapshot():
    subprocess.run(
        [
            "hdc",
            "shell",
            "snapshot_display",
            "-f",
            "/data/local/tmp/snapshot.jpeg",
        ],
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "hdc",
            "file",
            "recv",
            "/data/local/tmp/snapshot.jpeg",
            "resource/screenshot/snapshot.jpeg",
        ],
        capture_output=True,
        text=True,
    )


def encode_image(image):
    _, buffer = cv2.imencode('.jpeg', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return encoded_image


def crop_image(image, pos):
    pos = re.findall(r'\d+', pos)
    pos = list(map(int, pos))
    x, y, width, height = pos[0], pos[1], pos[2] - pos[0], pos[3] - pos[1]
    cropped_image = image[y:y + height, x:x + width]
    return cropped_image


def detection():
    print("-----------------------控件检测-----------------------")
    clickable_elements.clear()
    clickable_elements_information.clear()

    snapshot()
    layout()

    # 读取图片和layout
    screenshot = cv2.imread('resource/screenshot/snapshot.jpeg')
    with open("resource/layout/layout.json", "r", encoding="utf8") as fp:
        json_data = json.load(fp)
        extract_clickable_elements(json_data)
        # print(len(clickable_elements))
        # print(clickable_elements)

    for element in clickable_elements:
        if len(element['text']) >= 5 or len(element['image']) >= 5:
            continue
        elif len(element['text']) != 0 and len(element['text']) < 5:
            clickable_elements_information.append(
                {'pos': element['pos'], 'type': element['type'], 'information': element['text']})
        elif len(element['image']) != 0:
            content = [{"type": "text",
                        "text": detection_prompt},
                       {"type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot)}"}},
                       {"type": "image_url", "image_url": {
                           "url": f"data:image/jpeg;base64,{encode_image(crop_image(screenshot, element['pos']))}"}}]

            response = client.chat.completions.create(
                model="kimi-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a UI Testing Assistant.",
                    },
                    {
                        "role": "user",
                        "content": content,
                    },
                ],
                stream=False,
            )
            response = response.choices[0].message.content

            clickable_elements_information.append(
                {'pos': element['pos'], 'type': element['type'], 'information': response})
        else:
            clickable_elements_information.append(
                {'pos': element['pos'], 'type': element['type'], 'information': element['other']})
    for elements in clickable_elements_information:
        pos = re.findall(r'\d+', elements['pos'])
        pos = list(map(int, pos))
        x, y, = (pos[0] + pos[2]) // 2, (pos[1] + pos[3]) // 2
        elements['pos'] = str([x, y])
    print(clickable_elements_information)

    # 在截图上标记控件
    # draw_elements_on_image(screenshot, clickable_elements)
    
    return clickable_elements_information


def get_element_info_for_llm(elements):
    """生成适合大模型理解的元素描述"""
    element_descriptions = []

    for i, elem in enumerate(elements):
        desc = f"Widget{i + 1}, "
        desc += f"Type:[{elem['type']}], "
        desc += f"Information:{elem['information']}, "
        desc += f"Position:{elem['pos']}"

        element_descriptions.append(desc)
        # print(desc)

    return element_descriptions


def draw_elements_on_image(screenshot, elements):
    """在截图上标记检测到的控件"""
    marked_image = screenshot.copy()
    for i, element in enumerate(elements):
        # 获取元素位置
        pos = re.findall(r'\d+', element['pos'])
        pos = list(map(int, pos))
        x1, y1, x2, y2 = pos[0], pos[1], pos[2], pos[3]
        
        # 绘制矩形框
        cv2.rectangle(marked_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 添加编号
        cv2.putText(marked_image, f'Widget{i+1}', (x1, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # 保存标记后的图片
    cv2.imwrite('resource/screenshot/marked_snapshot.jpeg', marked_image)
    return marked_image



if __name__ == '__main__':
    clickable_elements_information = detection()
    element_descriptions = get_element_info_for_llm(clickable_elements_information)
    print(element_descriptions)

