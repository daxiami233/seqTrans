extraction_prompt = """
## BACKGROUND
Suppose you are mobile phone app testers specialized in cross-platform testing. You are good at extracting testing scenarios from source scripts and understanding the functional intent behind them. Here is the source script to be extracted:
```python
{}
```
## YOUR TASK
Please read the source script carefully, try to understand it and ultimately answer the following questions.
1.What kind of functionality is the script designed to test?
2.Summarize the detailed test steps in the testing procedure(including `operation type`, `parameters` and `description`).
3.What is the expected result of implementation? 
Additionally, I've provided screenshots of the function tested by this script to assist you in further understanding.
Answer these three questions one by one to ensure the accuracy.

## CONSTRAINT
Your output must strictly be a valid jSON object with three keys!
`Target Function`: the answer to the first question.
`Test Steps`: the answer to the second question. Its format must be a list, where each item is a sublist containing `operation type`, `parameters` and `description`.
`Result`: the answer to the third question.
Return **only** the JSON object without any additional text, explanations, or formatting.

## EXAMPLE
Example target script: 
`d(description="确定").click()
d(resourceId="com.android.settings:id/device_name").set_text("Xiaomi 14")`
Example answers: 
```json
{{
    "Target Function": "Implement a click on the OK button.",
    "Test Steps": [
        {{
            "Operation Type": "Click",
            "Parameters": "description=\"确定\"",
            "description": "A click on the OK button."
        }},
        {{
            "Operation Type": "Input",
            "Parameters": "resourceId=\"com.android.settings:id/device_name\", text=\"Xiaomi 14\"",
            "description": "Enter 'Xiaomi 14' as the new device name."
        }},
    ],
    "Result": "Button is successfully clicked to achieve the action."
}}
```
"""

detection_prompt = """
## Task
I have uploaded two images. The first one is a screenshot of the current mobile phone page, and the second one is a screenshot of a clickable component on the current page. 
Please briefly describe the function of this component in no more than 15 characters in Chinese.
## Example
['关闭设备名称编辑窗口']  // Must include square brackets and single quotes

Please strictly follow the format in the example, without any additional explanations or text.
"""


next_action_prompt = """
## Test Scenario: 
{}
Note: The original test scenario is from Android platform and needs to be adapted to the HarmonyOS platform. There may be differences in UI layouts, element identifiers, and interaction patterns between these platforms.

## Clickable Elements on the Current Screen:
{}

## Operations Completed So Far:
{}

## Feedback and Suggestions from the Previous Operation:
{}

## Your Task
Based on the test scenario, the current screenshot, the list of clickable elements, the operations completed, 
and the feedback and suggestions from the previous operation, determine what the next operation should be.

Consider the following when making your decision:
1. Focus on the functional intent rather than exact UI element matching.
2. Adapt to the current UI state even if it differs from the original Android scenario.
3. Choose the most appropriate element that serves the same purpose as in the original scenario.
4. If the exact element is not available, look for alternatives with similar functionality.
5. According to the feedback, avoid repeating operations that have already been executed.
6. Recognize equivalent functionality across different naming conventions (e.g., "屏幕超时"、"自动锁屏"、"休眠" may all refer to the same auto-lock functionality).
7. Consider semantic relationships between settings (e.g., "显示和亮度" section might contain screen timeout settings that control auto-lock behavior).
8. If you can't find the target element but notice a list, scrollable view, or navigation menu, try swiping to reveal more content. Look for visual cues like partial items at screen edges or scroll indicators.
9. When swiping through lists, consider both the direction (up/down for vertical lists, left/right for horizontal lists) and the context of what you're looking for (e.g., swipe down to find settings that might be lower in a list).

## Available Operations
You can only choose from the following types of actions:
1. "click": Specify the element ID from the provided list
2. "input": Specify the element ID and the text to be entered
3. "swipe": Specify the direction ("up", "down", "left", "right")
4. "back": Press the back button
5. "home": Return to the home screen (close the application)
6. "finish": If the test scenario is finished

## Response Format
Return your decision strictly in the following JSON format, without any explanatory language:
{{"action": "click", "element_id": 3}}
{{"action": "input", "element_id": 2, "text": "测试文本"}}
{{"action": "swipe", "direction": "up"}}
{{"action": "back"}}
{{"action": "home"}}
{{"action": "finish"}}
"""


verify_prompt = """
## Test Scenario: The original test scenario comes from similar applications on different platforms and needs to be adapted to the current target platform and application. There may be differences in interfaces and interaction methods between them.
{}

## Operations Performed
{}

## Interface Elements Before Operation
{}

## Interface Elements After Operation
{}

## Analysis Task
Please carefully analyze the screenshots and UI element changes before and after the operation, and strictly evaluate according to the following dimensions:

1. Goal Direction:
   - Whether the operation performed is moving in the correct direction toward the test goal
   - Whether there is any deviation from the test goal
   - If there is deviation, what specific aspects it manifests in

2. Interface Response:
   - Whether the interface has undergone significant changes (ignoring status information such as time and battery)
   - Whether the changes align with the expected operation results
   - If there are no changes, what might be the possible reasons

3. Goal Completion:
   - Whether the current state has completed the result described in the test scenario
   - Whether further operations are needed
   - Specific manifestations of the completion level

4. Next Step Recommendations:
   - Based on the current state, what operations should be taken to continue testing
   - If the current path is incorrect, how to adjust


## Output Requirements
Please return the analysis results strictly in the following format:
{{
    "validity": true/false, // Whether the operation is valid (successfully executed, correct UI response, matches functional intent, and leads to reasonable state change)
    "goal_completion": true/false, // Whether the test scenario's objective has been fully achieved
    "analysis": "Detailed analysis of the operation's effectiveness, interface changes, and progress toward the test goal",
    "next_steps": "Suggested next steps based on the current state, including correction if the current path is incorrect"
}}

Ensure your analysis focuses on functional intent rather than exact UI matching, considering the cross-platform adaptation context. 
Be precise, objective, and base your evaluation solely on the evidence from screenshots and UI elements. 
If the current operation deviates from the test goal, clearly indicate this and provide correction suggestions.

"""

