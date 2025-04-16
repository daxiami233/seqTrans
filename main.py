from extraction import extraction
from detection import detection, get_element_info_for_llm
from execution import execute_action
from verify import verify_operation_result
from get_action import get_next_action_from_llm


def run_test_transition(file_path, max_steps=20):
    # 从sourcecode中提取场景和元素信息
    with open(file_path, "r", encoding="utf-8") as file:
        script = file.read()

    # 使用LLM提取场景和元素信息
    scenario = extraction(script, file_path)

    # 初始化测试记录
    test_record = []
    # 所有已完成的操作
    completed_actions = []
    # 反馈信息
    feedback = []
    # 界面元素信息
    clickable_elements_json_list = []

    for _ in range(max_steps):
        # 获取界面元素信息（只有第一次需要获取，后面直接使用verify获取的元素）
        if not clickable_elements_json_list:
            clickable_elements_json_list = detection()
        element_descriptions = '\n'.join(get_element_info_for_llm(clickable_elements_json_list))

        # 获取下一次操作
        next_action = get_next_action_from_llm(element_descriptions, scenario, completed_actions, feedback)

        # 执行操作
        execution_log, cmd_list = execute_action(next_action, clickable_elements_json_list)
        print(execution_log)
        if "finish" in cmd_list :
            break
        if "hdc shell uitest uiInput keyEvent Home" in cmd_list:
            test_record += cmd_list
            break

        if next_action["action"] == "back":
            # 直接返回不需要验证操作
            clickable_elements_json_list = detection()
            continue

        # 验证操作结果
        result_json, elements_json_list_after = verify_operation_result(scenario, execution_log, element_descriptions)
        clickable_elements_json_list = elements_json_list_after

        feedback.clear()
        completed_actions.append(execution_log)

        if result_json["validity"]:
            test_record += cmd_list
        feedback.append("Analysis of the previous operation: " + result_json["analysis"])
        if result_json["goal_completion"]:
            break
        feedback.append("Suggested Next Steps: " + result_json["next_steps"] + "\n")
        print("Feedback: ", feedback)

    print(completed_actions)

    # 打开文件并写入
    with open(file_path.replace(".py", ".txt"), "w", encoding="utf-8") as file:
        for item in test_record:
            file.write(item + "\n")


if __name__ == '__main__':
    file_path = "tests/test4.py"
    run_test_transition(file_path)
