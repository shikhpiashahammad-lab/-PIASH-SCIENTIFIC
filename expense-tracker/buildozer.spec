[app]
title = Expense Tracker
package.name = expensetracker
package.domain = org.piash
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
version = 1.0.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0
android.permissions =
android.api = 36
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.ndk = 29
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
