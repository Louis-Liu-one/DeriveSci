# 我们的故事

我是 [LYX]({{ url_for('users', uid=2) }})。这里是我们的故事。

## 缘起

自七年级（2024 年）起，我开始自己做一些有挑战性的初等代数、平面几何题目。当时，我的班级里同样爱好数学的同学，也喜欢和我探讨这些问题。一次，不记得是哪位同学来找我要题目，我就把那道题目写在了一张借的活页纸上。

后来几经誊抄，我把这道题写到我自己的活页本上，为其编号 [0000]({{ url_for('probs', probno='0000') }})，表示“第一个”。我在题目背面写上“解法一：”，让同学们写上解法。下面的右上图是我的一位同学写的解法。

![活页本]({{ url_for('static', filename='images/notebook.jpeg') }})

于是，“数学题集”的集录开始了。

我称这段只使用活页本集录题目的时期为**活页本时代**。我的活页本上记录了编号为 [003E]({{ url_for('probs', probno='003E') }}) 前（含）的所有题目。

## PDF 时代

八年级（2024 年），随着我对 $\LaTeX$ 的了解不断深入，同时考虑到活页本难以记录众多的题目解法，我逐渐将这些题目与解法转移到电子文档中，使用 $\LaTeX$ 编写解法。

![PDF]({{ url_for('static', filename='images/latex-pdf.jpeg') }})

以上是我用 $\LaTeX$ 编辑的题目 [0089]({{ url_for('probs', probno='0089') }})。文档的格式、排版历经多次优化达到最后的效果，我的题集也有了“MathProbs”这一名称。

这段时间一直持续到九年级上学期（2026 年），我一共集录了 205 道题目，最大的编号为 [00CC]({{ url_for('probs', probno='00CC') }})，我称这一时期为**PDF 时代**。

现在，我的 PDF 版题集仍可以在 [GitHub](https://github.com/Louis-Liu-one/MathProbs)、[Gitee](https://gitee.com/Louis-Liu-one/MathProbs) 上找到。

## 初版网页

八年级（2025 年）我的题集进入 PDF 时代不久，我就有为题集建站的构想，并开启了一个项目，名为“MathProbs-HTML”，下图是我在该项目中实现的唯一页面。不过由于当时 Web 开发技术不精，对这一方面了解不够，这一项目很快烂尾，我也不再考虑建立网站。

![初版网页]({{ url_for('static', filename='images/old-webpage.jpeg') }})

九年级寒假（2026 年）的一个普通的下午，我打开许久不用的 U 盘检查，发现了一个文件夹 `mathprobs-html`。当时随着题目越来越多，编辑时间不断膨胀，PDF 时代即将走进尾声。我这时想起建站的事，这是多么伟大的构想呢！我当即着手重启项目，开始建站。

## 网站时代

由于投入时间开发，我停止向 PDF 文档中增加题目。我将题集网站项目易名为“MathProbsOnline”，经过一两周的开发，项目最后在 PythonAnyWhere 上线。上线至今，我一直从 PDF 文档将题目迁移到网站，同时也上传一些新题目，也不断为网站项目推出新功能、新优化，这段时间我称为**网站时代**。我的 MathProbsOnline 项目可以在 [GitHub](https://github.com/Louis-Liu-one/MathProbsOnline)、[Gitee](https://gitee.com/Louis-Liu-one/MathProbsOnline) 上找到。

网站草创之初，很多题目、题解有缺失，敬请谅解。
