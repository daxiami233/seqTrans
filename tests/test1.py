import uiautomator2 as u2
import time

d = u2.connect()

d.app_start("com.android.settings")
time.sleep(1)
d.swipe_ext("up")
time.sleep(5)
d(text="锁屏").click()
time.sleep(1)
d(text="自动锁屏").click()
time.sleep(1)
d(text="5 分钟").click()
time.sleep(1)
d.app_stop("com.android.settings")

