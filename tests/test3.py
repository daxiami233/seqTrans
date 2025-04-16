import uiautomator2 as u2
import time

d = u2.connect()

d.app_start("com.shark.jizhang")
time.sleep(1)
d.xpath(
    '//*[@resource-id="com.shark.jizhang:id/addTabFloat"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]').click()
time.sleep(1)
d(resourceId="com.shark.jizhang:id/categoryItemText", text="宠物").click()
time.sleep(1)
d(resourceId="com.shark.jizhang:id/remarkName", text="点击填写备注")
time.sleep(1)
d(resourceId="com.shark.jizhang:id/remarkName").set_text("测试备注")
time.sleep(1)
d.click(0.5, 0.301)
time.sleep(1)
d(resourceId="com.shark.jizhang:id/six").click()
d(resourceId="com.shark.jizhang:id/six").click()
d(resourceId="com.shark.jizhang:id/six").click()
d(resourceId="com.shark.jizhang:id/done").click()
time.sleep(1)
d.app_stop("com.shark.jizhang")
