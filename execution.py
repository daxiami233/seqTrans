import subprocess
import time

def execute_action(action, elements):
    """执行大模型决定的操作

    Args:
        action: 操作指令，格式为字典
        elements: 可点击元素列表

    Returns:
        操作结果反馈
    """
    print("-----------------------执行大模型决定的操作-----------------------")

    action_type = action.get("action")
    cmd_list = []

    if action_type == "click":
        # 点击元素
        element_id = action.get("element_id")
        if element_id is not None and 1 <= element_id <= len(elements):
            element = elements[element_id - 1]
            center_x, center_y = eval(element["pos"])[0], eval(element["pos"])[1]

            cmd = f"hdc shell uitest uiInput click {center_x} {center_y}"
            print(f"执行点击: {cmd}")
            subprocess.run(cmd, shell=True)
            cmd_list.append(cmd)
            return f"Click widget{element_id}: {element.get('information', '')} at ({center_x}, {center_y})", cmd_list
        else:
            return f"无效的元素ID: {element_id}", cmd_list

    elif action_type == "input":
        # 输入文本
        element_id = action.get("element_id")
        text = action.get("text", "")

        if element_id is not None and 1 <= element_id <= len(elements):
            element = elements[element_id - 1]
            center_x, center_y = eval(element["pos"])[0], eval(element["pos"])[1]

            # 先点击元素
            click_cmd = f"hdc shell uitest uiInput click  {center_x} {center_y}"
            print(f"执行点击: {click_cmd}")
            subprocess.run(click_cmd, shell=True)
            cmd_list.append(click_cmd)

            time.sleep(1)

            # 输入文本
            input_cmd = f"hdc shell uitest uiInput inputText {center_x} {center_y} '{text}'"
            print(f"执行输入: {input_cmd}")
            subprocess.run(input_cmd, shell=True)
            cmd_list.append(input_cmd)

            return f"{text} was entered in element {element_id}", cmd_list
        else:
            return f"无效的元素ID: {element_id}", cmd_list

    elif action_type == "swipe":
        # 滑动屏幕
        direction = action.get("direction")
        
        # 根据方向设置滑动命令
        if direction == "up":
            cmd = "hdc shell uitest uiInput dircFling 3"
        elif direction == "down":
            cmd = "hdc shell uitest uiInput dircFling 2"
        elif direction == "left":
            cmd = "hdc shell uitest uiInput dircFling 0 500"
        elif direction == "right":
            cmd = "hdc shell uitest uiInput dircFling 1 600"
        else:
            return f"无效的滑动方向: {direction}", cmd_list
            
        print(f"执行滑动: {cmd}")
        subprocess.run(cmd, shell=True)
        cmd_list.append(cmd)
        return f"执行{direction}方向的滑动操作", cmd_list

    elif action_type == "back":
        # 返回
        cmd = "hdc shell uitest uiInput keyEvent Back"
        print(f"执行返回: {cmd}")
        subprocess.run(cmd, shell=True)
        cmd_list.append(cmd)
        return "A return operation was performed", cmd_list

    elif action_type == "home":
        # 返回
        cmd = "hdc shell uitest uiInput keyEvent Home"
        print(f"执行回桌面: {cmd}")
        subprocess.run(cmd, shell=True)
        cmd_list.append("home")
        return "A return home operation was performed", cmd_list

    elif action_type == "finish":
        cmd_list.append("finish")
        # 完成测试
        return "Test finished", cmd_list

    else:
        return f"未知的操作类型: {action_type}", cmd_list
