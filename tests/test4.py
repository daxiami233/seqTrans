import uiautomator2 as u2
import time

d = u2.connect()

d.app_start("com.android.settings")
d.swipe_ext("up")
time.sleep(5)
d(text="省电与电池").click()
time.sleep(1)
d(text="当前模式").click()
time.sleep(1)
d(text="省电模式").click()
time.sleep(1)
d.app_stop("com.android.settings")

