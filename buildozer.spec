[app]

title = PIASH SCIENTIFIC
package.name = piashscientific
package.domain = org.piash
source.dir = .
source.include_exts = py,png,jpg,kv
version = 1.0.3
requirements = python3==3.13.7,hostpython3==3.13.7,kivy==2.3.1
orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
