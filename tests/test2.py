import uiautomator2 as u2
import time

d = u2.connect()

d.app_start("com.android.settings")

d(text="我的设备").click()
time.sleep(1)
d(resourceId="com.android.settings:id/summary").click()
time.sleep(1)
d(resourceId="com.android.settings:id/device_name").set_text("Xiaomi 14")
time.sleep(1)
d.xpath('//android.widget.ImageView[@content-desc="确定"]').click()
d(description="确定").click()
time.sleep(1)
d.app_stop("com.android.settings")

