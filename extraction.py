from prompt import extraction_prompt
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url=os.getenv("MOONSHOT_BASE_URL"),
)


def extraction(script, test_file_path):
    print("-----------------------源代码语义提取-----------------------")
    
    # 构建JSON文件路径（与测试文件同目录，同名但扩展名为.json）
    json_file_path = os.path.splitext(test_file_path)[0] + ".json"
    
    # 检查是否已经存在提取结果
    if os.path.exists(json_file_path):
        # print(f"找到已保存的提取结果: {json_file_path}")
        with open(json_file_path, "r", encoding="utf-8") as f:
            scenario = json.load(f)
            print(scenario)
            return scenario
    
    # 如果不存在，则进行提取
    text = extraction_prompt.format(script)
    response = client.chat.completions.create(
        model="kimi-latest",
        messages=[
            {
                "role": "system",
                "content": "You are a UI Testing Assistant.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                ],
            },
        ],
        stream=False,
    )
    scenario = response.choices[0].message.content
    print(scenario)
    
    # 保存提取结果
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(scenario, f, ensure_ascii=False, indent=2)
    # print(f"提取结果已保存到: {json_file_path}")
    
    return scenario


if __name__ == '__main__':
    test_file_path = "tests/test1.py"
    with open(test_file_path, "r", encoding="utf-8") as file:
        script = file.read()
        extraction(script, test_file_path)


