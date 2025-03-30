# pin语言解释器

pin语言是用拼音来当代码的项目，仅供娱乐，实际速度不如其他语言。

## 使用方法

1. 在命令行中使用 `pin` 命令运行拼语言文件：

```
pin 文件名.pin
```

2. 显示版本信息：

```
pin -v
```

3. 以调试模式运行：

```
pin --debug 文件名.pin
```

## 语法示例

```
# 变量定义
bianliang name = "拼语言"
bl age = 18

# 打印
dayin(name)
dy(age)

# 条件判断
panduan age > 10:
    dy("年龄大于10")
fouze:
    dy("年龄小于等于10")

# 循环
xunhuan cishu = 5:
    dy("循环示例")
    
# 列表操作
liebiao chuangjian languages = ["拼语言", "Python", "Java"]
liebiao huoqu languages bianhao = 0 chuandi bianliang = first_lang
liebiao bianji languages bianhao = 1 chuandi zifu("JavaScript")
```

## 安装方法

直接运行可执行文件 `pin.exe`，或者将其添加到系统 PATH 环境变量中，以便在任何地方使用 `pin` 命令。 