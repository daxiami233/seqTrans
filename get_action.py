import time
import cv2
from detection import get_element_info_for_llm
from openai import OpenAI
import json
from prompt import next_action_prompt
from detection import encode_image
import re
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url=os.getenv("GOOGLE_BASE_URL"),
)


def get_next_action_from_llm(element_descriptions, test_scenario, completed_actions=None, feedback=None):
    """使用大模型决定下一步操作

    Args:
        element_descriptions: 可点击元素列表
        test_scenario: 测试场景描述
        completed_actions: 已完成的操作列表
        feedback: 上一步操作的反馈信息

    Returns:
        操作指令，格式为字典，包含操作类型和参数
    """
    print("-----------------------大模型决定下一步操作-----------------------")

    if completed_actions is None:
        completed_actions = []

    if feedback is None:
        feedback = []

    # 构建提示词
    prompt = next_action_prompt.format(test_scenario, element_descriptions, completed_actions, feedback)

    screenshot = cv2.imread('resource/screenshot/snapshot.jpeg')

    # 准备消息内容
    messages = [
        {"role": "system", "content": "You are a UI testing assistant that helps users decide what to do next."},
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(screenshot)}"}}]}, ]

    # 调用大模型API
    try:
        response = client.chat.completions.create(
            # model="kimi-latest",
            # model="GPT-4o",
            # model="gemini-2.5-pro-exp-03-25",
            model="gemini-2.0-flash",
            messages=messages,
            stream=False,
        )
        action_json = response.choices[0].message.content
        try:
            # 尝试解析JSON
            action = json.loads(action_json)
        except json.JSONDecodeError as e:
            action = json.loads(re.search(r'\{.*\}', action_json, re.DOTALL).group(0))

        print("大模型返回的下一步动作：", action)
        return action

    except Exception as e:
        print(f"调用大模型API失败: {e}")
        return {"action": "error", "message": str(e)}


if __name__ == '__main__':
    from extraction import extraction
    from detection import detection

    with open("tests/test2.py", "r", encoding="utf-8") as file:
        script = file.read()
    scenario = extraction(script)
    print(scenario)
    elements = detection()
    element_descriptions = '/n'.join(get_element_info_for_llm(elements))
    next_action = get_next_action_from_llm(elements, scenario)
    from execution import execute_action

    exe_action_log = execute_action(next_action, elements)
    print(exe_action_log)
    from verify import verify_operation_result

    verify_operation_result(scenario, exe_action_log, element_descriptions)
