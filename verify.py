from openai import OpenAI
import base64
import time
import cv2
from detection import detection, get_element_info_for_llm, snapshot
import json
from prompt import verify_prompt
import re
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url=os.getenv("GOOGLE_BASE_URL"),
)


def verify_operation_result(test_scenario, operation, element_descriptions_before):
    """验证操作结果

    Args:
        test_scenario: 测试场景
        operation: 执行的操作
        element_descriptions_before: 操作前界面元素

    Returns:
        验证结果，包含成功/失败状态和详细信息
    """
    print("-----------------------验证操作结果-----------------------")

    # 等待UI更新
    time.sleep(2)

    # 获取操作后的屏幕状态
    before_screenshot_path = "./resource/screenshot/before_operation.jpeg"
    after_screenshot_path = "./resource/screenshot/after_operation.jpeg"

    # 重命名当前截图为操作前截图（如果存在）
    if os.path.exists("./resource/screenshot/snapshot.jpeg"):
        os.rename(
            "./resource/screenshot/snapshot.jpeg",
            before_screenshot_path
        )

    # 获取操作后的截图
    snapshot()
    screenshot = cv2.imread('resource/screenshot/snapshot.jpeg')
    if screenshot is not None:
        cv2.imwrite(after_screenshot_path, screenshot)

    # 获取操作后的UI元素
    elements_after = detection()
    element_descriptions_after = '\n'.join(get_element_info_for_llm(elements_after))

    # 准备图像内容
    before_image_content = None
    after_image_content = None

    try:
        if os.path.exists(before_screenshot_path):
            with open(before_screenshot_path, "rb") as image_file:
                image_bytes = image_file.read()
                before_image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                before_image_content = f"data:image/jpeg;base64,{before_image_base64}"

        if os.path.exists(after_screenshot_path):
            with open(after_screenshot_path, "rb") as image_file:
                image_bytes = image_file.read()
                after_image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                after_image_content = f"data:image/jpeg;base64,{after_image_base64}"
    except Exception as e:
        print(f"读取截图失败: {e}")

    # 构建提示词
    prompt = verify_prompt.format(test_scenario, operation, element_descriptions_before, element_descriptions_after)

    # 准备消息内容
    messages = [
        {"role": "system",
         "content": "You are a UI test verification assistant that helps users verify the results of their actions."}
    ]

    # 添加用户消息
    user_message = {"role": "user", "content": [{"type": "text", "text": prompt}]}

    # 如果有图像，添加到消息中
    user_message["content"].extend([
        {"type": "image_url", "image_url": {"url": before_image_content}},
        {"type": "image_url", "image_url": {"url": after_image_content}}
    ])

    messages.append(user_message)

    # 调用大模型API
    response = client.chat.completions.create(
        # model="kimi-latest",
        # model="GPT-4o",
        # model="gemini-2.5-pro-exp-03-25",
        model="gemini-2.0-flash",
        messages=messages,
        stream=False,
    )
    result_text = response.choices[0].message.content
    print("验证结果:", result_text)

    # 解析JSON
    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
    if json_match:
        result = json.loads(json_match.group(0))
        return result, elements_after
