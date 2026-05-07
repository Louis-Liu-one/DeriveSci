
# MathProbsOnline

为 [MathProbs 项目](https://github.com/Louis-Liu-one/MathProbs) 建立的网站，已上线，[点击前往](https://MathProbsOnline.PythonAnyWhere.com)。

## 构建方法

- 项目使用 `markdown-it` 渲染 Markdown，使用 `mdit/plugin-katex` 插件和 $\KaTeX$ 引擎渲染数学公式，使用 Font Awesome 渲染图标。初次进入网页时，需要加载各项 CDN，速度较慢，敬请谅解。

- 网页服务所需的Python第三方库有：SymPy、PyParsing、Werkzeug、Flask、Flask-Login、Flask-SQLAlchemy、Flask-Migrate、func_timeout 等，具体参见 `requirements.txt`，可以直接使用 `pip` 安装，建议使用虚拟环境。命令如下：
```bash
cd MathProbsOnline
python -m venv webenv            # 创建环境
source webenv/bin/activate       # 激活环境
pip install -r requirements.txt  # 安装支持
# 操作
deactivate                       # 退出环境
```

- 所有构建都完成时，先将你的 Flask 密钥设置在 `FLASK_SECRET_KEY` 环境变量中：
```bash
FLASK_SECRET_KEY=密钥...
export FLASK_SECRET_KEY
```
你也可以将上述命令加入 `webenv/bin/activate` 中。然后，运行 `app.py`，或从他处导入：
```python
from app import app
app.run()
```
此时，网页可在 `localhost:5000` 访问。

- 初始化 Flask-Migrate 时，使用
```bash
flask db init
```
代码进行修改后，更新数据库时，使用
```bash
flask db migrate -m '更新描述...'
flask db upgrade
```

## 部署域名

已经在 PythonAnyWhere 上部署，[点击前往](https://MathProbsOnline.PythonAnyWhere.com)。

PythonAnyWhere 上使用的 Flask 密钥与仓库中的不同，仓库中的密钥仅作测试之用。

## 使用说明

1. 本网站仅供各位数学爱好者交流题目题解，增进数学能力，共享数学之美，不供娱乐等其它目的；
2. 本网站提供的所有内容、信息及服务，仅供用户参考；用户在使用本网站时，应自行判断信息的准确性和合法性。对于因使用本网站内容而产生的任何后果，网站运营方不承担任何责任；
3. 本网站可能包含第三方链接，网站对这些链接的内容不承担任何责任；用户在使用这些链接时，应自行承担相应风险；
4. 以上内容的解释权归网站运营方所有。

使用时应该注意：
1. 必须遵守国家相关法律法规，不能进行违法行为；
2. 上传的题目、题解内容必须依法依规；要以学习为主，不包含无关内容；上传的题目要有编号，建议按照统一的格式；
3. 上传的任何图片（包括但不限于问题、题解附带图片、用户头像）必须依法依规；建议将大小控制在 100KB 以下，以保证访问速度；建议使用 SVG 格式、JPEG 格式的图像，以提高访问速度；在题目、题解正文中要用 Markdown 语法插入图像，否则图像不会显示，图像路径直接使用 `<图像文件名称>` 即可；
4. 在讨论区发布的评论必须依法依规，不发表无关内容干扰讨论；发表见解时，尊重他人，养成文明用语的习惯；不要在讨论区发布答案、题解；
5. PythonAnyWhere 服务器位于美国东海岸，国内响应速度较慢，请耐心等待；
6. 如遇任何问题或希望提供建议，请联系网站运营者 [Liu One](https://github.com/Louis-Liu-one)（微信：wxliuone）；一些题目、方法等的出处由于历史原因未能标出，如有侵权，请联系网站运营者删除相关内容。
