# KaTeX 公式指南

## 摘要

**Markdown** 是一种轻量级标记语言。我们的网站中所有的题目、题解、评论等需要或可能需要格式化排版的内容全部使用 Markdown 输入。我们为 Markdown 输入添加了 $\KaTeX$ 公式的支持。由于 $\KaTeX$ 公式内容较多，故单分为此篇。其它 Markdown 语法可以在[此处]({{ url_for('helps', howto='write-markdown') }})找到。

本篇内容仅包含常用的公式用法，更多内容参见[此处](https://katex.org/docs/support_table)。

## 公式语法基础

### 行内公式与行间公式

在 $\KaTeX$ 中，行内公式要用 `$` 符号包围，行间公式要用 `$$` 符号包围。例如：`$x^2 + 2x + 1$` 渲染得到 $x^2 + 2x + 1$，
```latex
$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$
```
$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$

### 分组与整体

将多个字符用 `{...}` 包围，就得到一个**分组**，分组可以嵌套。单个字符、单个无参数命令或单个分组被视为一个**整体**。

### 命令

公式中的**命令**以 `\` 开头，后面跟着一系列连续的大写或小写字母，例如 `\alpha`、`\beta`。

命令可以带有参数。一个接受 $n$ 个参数的命令，其后的 $n$ 个整体被视为其参数。命令也可以带有可选参数，可选参数必须使用 `[...]` 包围。例如：

命令 | 效果 | 命令 | 效果
--------------- | --------------- | --------------- | ---------------
`\alpha`        | $\alpha$        | `\sqrt[n]{13}`  | $\sqrt[n]{13}$
`\frac1{x + 1}` | $\frac1{x + 1}$ | `\frac{x + 1}2` | $\frac{x + 1}2$
`\frac xy`      | $\frac xy$      | `\sqrt2`        | $\sqrt2$
`p^\alpha, q^\beta, \dots` | $p^\alpha, q^\beta, \dots$

需要注意的是，上述例子中的 `\frac xy` 不能写作 `\fracxy`，因为这样 `\fracxy` 会被视为一个命令，而非 `\frac{x}{y}`。

### 环境

一个**环境**以 `\begin{环境名}` 始，至 `\end{环境名}` 止。环境可以接受参数，其格式与命令参数的格式相同。被环境包围的内容称为环境的**内容**。例如，可以使用 `pmatrix` 环境创建[矩阵](#矩阵)：
```latex
$$
\begin{pmatrix}
    a & b \\
    c & d
\end{pmatrix}
$$
```
$$
\begin{pmatrix}
    a & b \\
    c & d
\end{pmatrix}
$$

### 转义字符

公式中可以使用 `\` 将字符进行**转义**，避免其被解析。

转义 | 效果 | 转义 | 效果 | 转义 | 效果 | 转义 | 效果
:--: | :--: | :--: | :--: | :--: | :--: | :--: | :--:
`\%` | $\%$ | `\$` | $\$$ | `\&` | $\&$ | `\#` | $\#$
`\_` | $\_$ | `\{` | $\{$ | `\}` | $\}$ | `\backslash` | $\backslash$

## 数学结构

**数学结构**是公式编写中最重要的部分。

### 上标与下标

#### 一般上下标

使用 `^` 符号插入上标，`_` 符号插入下标。例如：

命令 | 效果
----------------------------- | -----------------------------
`e^x`                         | $e^x$
`(x + y)^2`                   | $(x + y)^2$
`a^{x + y} = a^x \cdot a^y`   | $a^{x + y} = a^x \cdot a^y$
`F_n = F_{n - 1} + F_{n - 2}` | $F_n = F_{n - 1} + F_{n - 2}$

可见，上标或下标的用法与命令基本相同，其将其后的一个[整体](#分组与整体)视为上下标的内容。上标或下标前面的内容，如上例中的 $e$、$(x + y)$、$a$、$F$，任何时候都不需要用花括号包围。

上标和下标可以嵌套使用，例如 `2^{2^x} + 1` 得到 $2^{2^x} + 1$。然而，嵌套使用上下标时，大括号不可少，例如 `2^2^x + 1` 是错误的。

#### 特殊符号上下标

对于 $\max$、$\min$、$\sum$、$\prod$ 等算子，其在行间公式模式下的上下标在其正上下方。例如：
```latex
$$ \sum_{n = 1}^\infty \frac1{n^s} = \prod_p \frac1{1 - p^{-s}} $$
```
$$ \sum_{n = 1}^\infty \frac1{n^s} = \prod_p \frac1{1 - p^{-s}} $$

对于 $\int$ 等符号，其在行间公式模式下的上下标通常在角落处，例如：
```latex
$$ I = \int_0^{+\infty} \frac{\sin x}x \mathrm dx $$
```
$$ I = \int_0^{+\infty} \frac{\sin x}x \mathrm dx $$

#### 行内公式上下标

对于行内公式，无论算符，上下标都在右上角或右下角，例如行内公式 `\sum_{n = 0}^\infty` 得到 $\sum_{n = 0}^\infty$。

#### 改变上下标的位置

可以在上下标前使用 `\limits`、`\nolimits` 命令改变上下标的位置。例如在行内公式中：

命令 | 效果
---------------------------- | ----------------------------
`\sum_{n = 0}^\infty`        | $\sum_{n = 0}^\infty$
`\sum\limits_{n = 0}^\infty` | $\sum\limits_{n = 0}^\infty$

行间公式中：
```latex
$$ \sum\nolimits_{n = 0}^\infty $$
```
$$ \sum\nolimits_{n = 0}^\infty $$

### 分式与二项式系数

#### 分式

使用 `\frac` 命令渲染分式。其接受两个参数，分别表示分子和分母。例如，`\frac{az + b}{cz + d}` 在行内渲染得到 $\frac{az + b}{cz + d}$。

行内分式与行间分式的渲染结果有所不同。上例在行间分式中的表现为
$$ \frac{az + b}{cz + d} $$
可以使用 `\tfrac`、`\dfrac` 命令指定分式渲染使用行内还是行间模式。例如：
```latex
$$ f = \frac1{\dfrac1u + \dfrac1v} $$
```
$$ f = \frac1{\dfrac1u + \dfrac1v} $$
以及
```latex
$$ \tfrac n{H_n} = \sum\nolimits_{i = 1}^n \tfrac1{x_i} $$
```
$$ \tfrac n{H_n} = \sum\nolimits_{i = 1}^n \tfrac1{x_i} $$

即使在行间公式中，位于分子或分母上的分式也会按照行内模式渲染。此时，就可以使用 `\dfrac` 命令指定仍使用行间模式。

#### 二项式系数

使用 `\binom` 命令渲染二项式系数，其用法与 `\frac` 命令相同。例如：
```latex
$$ \binom nk = \frac{n!}{k!(n - k)!} $$
```
$$ \binom nk = \frac{n!}{k!(n - k)!} $$
也可以使用 `n \choose k` 得到相同的结果。与 `\frac` 相似，`\binom` 命令也有孪生的 `\tbinom`、`\dbinom` 命令，用于指定行内或行间模式。

#### 自定义分式

使用 `\genfrac` 命令自定义分式。其接受六个参数，如下：
```latex
\genfrac{左括号}{右括号}{线宽}{样式}{分子}{分母}
```
其中样式的意义是：

样式 | 对应命令 | 意义
-- | -------------------- | ---------
0  | `\displaystyle`      | 行间模式
1  | `\textstyle`         | 行内模式
2  | `\scriptstyle`       | 角标模式
3  | `\scriptscriptstyle` | 小角标模式

指定渲染分式的模式。若置空，则模式由当前所处位置决定。

以下是例子：
```latex
$$ \genfrac{\{}{\}}{1pt}{}nk $$
```
$$ \genfrac{\{}{\}}{1pt}{}nk $$

### 根式、上下划线与上下括号

#### 根式

使用 `\sqrt` 命令渲染根式。其接受一个可选参数，表示几次根。

命令 | 效果
--- | ---
`\sqrt x \cdot \sqrt y = \sqrt{xy} \quad (x, y > 0)` | $\sqrt x \cdot \sqrt y = \sqrt{xy} \quad (x, y > 0)$
`\sqrt[n]x = x^{\frac1n}` | $\sqrt[n]x = x^{\frac1n}$

注意到在使用 `\sqrt x + \sqrt y` 渲染 $\sqrt x + \sqrt y$ 时，左右高度不同，此时可以使用 `\mathstrut` 命令控制：
```latex
$\sqrt{\mathstrut x} + \sqrt{\mathstrut y}$
```
渲染得到 $\sqrt{\mathstrut x} + \sqrt{\mathstrut y}$。

#### 上下划线与上下括号

使用 `\overline`、`\underline` 等命令创建上下划线：
命令 | 效果 | 命令 | 效果
:---: | :---: | :---: | :---:
`\underline{x + y}` | $\underline{x + y}$ | `\overline{x + y}` | $\overline{x + y}$
`\underleftarrow{x + y}` | $\underleftarrow{x + y}$ | `\overleftarrow{x + y}` | $\overleftarrow{x + y}$
`\underrightarrow{x + y}` | $\underrightarrow{x + y}$ | `\overrightarrow{x + y}` | $\overrightarrow{x + y}$
`\underleftrightarrow{x + y}` | $\underleftrightarrow{x + y}$ | `\overleftrightarrow{x + y}` | $\overleftrightarrow{x + y}$
`\underbrace{x + y}` | $\underbrace{x + y}$ | `\overbrace{x + y}` | $\overbrace{x + y}$

上下划线与上下括号可以嵌套。划线与括号高度同样可以使用 `\mathstrut` 控制。

### 矩阵

可以使用 `matrix`、`pmatrix` 等环境创建矩阵。具体用法如下：
```latex
\begin{矩阵环境名}
    a & b & c \\
    d & e & f \\
    g & h & i
\end{矩阵环境名}
```
使用 `\\` 分隔矩阵的每行，使用 `&` 分隔矩阵的每列。以下是一些矩阵环境及效果：
环境 | 效果 | 环境 | 效果 | 环境 | 效果
:---: | :---: | :---: | :---: | :---: | :---:
`matrix` | $\begin{matrix} a & b \\ c & d \end{matrix}$ | `bmatrix` | $\begin{bmatrix} a & b \\ c & d \end{bmatrix}$ | `vmatrix` | $\begin{vmatrix} a & b \\ c & d \end{vmatrix}$
`pmatrix` | $\begin{pmatrix} a & b \\ c & d \end{pmatrix}$ | `Bmatrix` | $\begin{Bmatrix} a & b \\ c & d \end{Bmatrix}$ | `Vmatrix` | $\begin{Vmatrix} a & b \\ c & d \end{Vmatrix}$

矩阵中可以使用 `\cdots`、`\vdots` 等省略号：
```latex
$$
\begin{pmatrix}
    a_{11} & \cdots & a_{1n} \\
    \vdots & \ddots & \vdots \\
    a_{n1} & \cdots & a_{nn}
\end{pmatrix}_{n \times n}
$$
```
$$
\begin{pmatrix}
    a_{11} & \cdots & a_{1n} \\
    \vdots & \ddots & \vdots \\
    a_{n1} & \cdots & a_{nn}
\end{pmatrix}_{n \times n}
$$

对于行内公式，可以使用 `smallmatrix` 环境。其提供的矩阵不带括号，可以通过[定界符]({{ url_for('helps', howto='write-markdown-equations-symbols', _anchor='定界符') }})添加。例如，`\left( \begin{smallmatrix} a & b \\ c & d \end{smallmatrix} \right)` 在行内渲染得到 $\left( \begin{smallmatrix} a & b \\ c & d \end{smallmatrix} \right)$。

## 字体、符号与文字

### 数学字体

公式中可以动态指定不同的数学字体。

#### 字体样式

除了默认字体，还可以使用 `\mathrm` 等命令使用其它数学字体，使用方法是 `\mathrm{...}`。以下是一些数学字体及其渲染效果：
命令 | 名称 | 字母效果 | 数字效果
:----------------: | :----: | :-: | :-:
`\mathnormal` | 默认字体 | $ABCDEFGHIJKLMNOPQRSTUVWXYZ$            | $1234567890$
`\mathit`     | 意大利体 | $\mathit{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$   | $\mathit{1234567890}$
`\mathrm`     | 罗马体   | $\mathrm{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$   | $\mathrm{1234567890}$
`\mathsf`     | 无衬线体 | $\mathsf{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$   | $\mathsf{1234567890}$
`\mathtt`     | 打字机体 | $\mathtt{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$   | $\mathtt{1234567890}$
`\mathbb`     | 黑板体   | $\mathbb{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$   | $\mathbb{1234567890}$
`\mathcal`    | 书法体   | $\mathcal{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$  | $\mathcal{1234567890}$
`\mathscr`    | 花体     | $\mathscr{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$  | $\mathscr{1234567890}$
`\mathfrak`   | 哥特体   | $\mathfrak{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathfrak{1234567890}$

例如，可以使用 `\mathrm dx` 渲染 $\mathrm dx$。注意，由于这里没有显式指定参数，命令后的第一个整体，即 `d` 被指定为第一个参数，故只有 `d` 被渲染为罗马体。

#### 字体大小

可以使用如下四个命令调整字体大小：
命令 | 名称 | 效果
:------------------: | :------: | :----------------------------------------:
`\displaystyle`      | 行间模式  | $\displaystyle{\frac{x + 1}{x + 2}}$
`\textstyle`         | 行内模式  | $\textstyle{\frac{x + 1}{x + 2}}$
`\scriptstyle`       | 角标模式  | $\scriptstyle{\frac{x + 1}{x + 2}}$
`\scriptscriptstyle` | 小角标模式 | $\scriptscriptstyle{\frac{x + 1}{x + 2}}$

上述命令不接受任何参数。在公式中使用上述命令时，将影响本条公式中其后所有内容。

### 水平间距与盒子

合理利用水平间距与各类盒子，可以自主调整文本样式，更好地控制公式间距。

#### 长度单位

要使用水平间距，需要先了解长度单位。下列是公式中可用的长度单位：
长度 | 效果 | 备注
---------------------: | :--------------------- | ---
对照组                  | $AA$
$20\,\mathrm{pt}$      | $A\hspace{20pt}A$      | point，点/磅
$1310720\,\mathrm{sp}$ | $A\hspace{1310720sp}A$ | scaled point，最小单位
$20\,\mathrm{bp}$      | $A\hspace{20bp}A$      | big point，大点，$72\,\mathrm{bp} = 1\,\mathrm{in}$
$20\,\mathrm{dd}$      | $A\hspace{20dd}A$      | didot point，$1157\,\mathrm{dd} = 1238\,\mathrm{pt}$
$2\,\mathrm{pc}$       | $A\hspace{2pc}A$       | pica，四号字大小，$1\,\mathrm{pc} = 12\,\mathrm{pt}$
$2\,\mathrm{cc}$       | $A\hspace{2cc}A$       | cicero，$1\,\mathrm{cc} = 12\,\mathrm{dd}$
$10\,\mathrm{mm}$      | $A\hspace{10mm}A$      | mm，毫米，$10\,\mathrm{mm} = 1\,\mathrm{cm}$
$1\,\mathrm{cm}$       | $A\hspace{1cm}A$       | cm，厘米，$2.54\,\mathrm{cm} = 1\,\mathrm{in}$
$0.5\,\mathrm{in}$     | $A\hspace{.5in}A$      | inch，英寸，$1\,\mathrm{in} = 72.27\,\mathrm{pt}$
$10\,\mathrm{ex}$      | $A\hspace{10ex}A$      | 字号相关的长度，本指当前字号下字符 x 的高度
$5\,\mathrm{em}$       | $A\hspace{5em}A$       | 字号相关的长度，本指当前字号下字符 M 的宽度

#### 水平间距

可以使用 `\hspace` 命令产生**水平间距**：
```latex
$$ a, b, \hspace{10pt}, c $$
```
$$ a, b, \hspace{10pt}, c $$

可以使用 `\thinspace` 等预定义的水平间距：
命令 | 宽度 | 效果 | 备注
:--------------------: | ---------------------: | :---------------- | ---
对照组                  |       $0\,\mathrm{em}$ | $AA$
`\thinspace` 或 `\,`   |  $0.1667\,\mathrm{em}$ |$A\,A$             | 不可换行
`\negthinspace`        | $-0.1667\,\mathrm{em}$ |$A\negthinspace A$ | 不可换行
`\enspace`             |     $0.5\,\mathrm{em}$ |$A\enspace A$      | 不可换行
`\nobreakspace` 或 `~` | 空格                    |$A~A$              | 不可换行
`\quad`                |       $1\,\mathrm{em}$ | $A\quad A$
`\qquad`               |       $2\,\mathrm{em}$ | $A\qquad A$
`\enskip`              |     $0.5\,\mathrm{em}$ | $A\enskip A$
`\ `                   | 空格                    | $A\ A$

#### 盒子

可以使用 `\fbox` 命令产生**带边框的盒子**，盒子中的内容不能换行：
```latex
$$ \fbox{\text{无法换行的内容……}} $$
```
$$ \fbox{\text{无法换行的内容……}} $$

可以使用 `\llap`、`\rlap` 命令产生左、右边的**重叠效果**：
```latex
$$ \text{左边内容\llap{重叠}} \hspace{20pt} \text{\rlap{重叠}右边内容} $$
```
$$ \text{左边内容\llap{重叠}} \hspace{20pt} \text{\rlap{重叠}右边内容} $$

可以使用 `\phantom` 命令产生**幻影盒子**，盒子中的内容不显示，但保留其间距：
```latex
$$
\begin{align*}
    1 \phantom{+ 2} + 3 \phantom{+ 4} + 5 \phantom{+ 6} &= 9 \\
    \phantom{+ 1} + 2 \phantom{+ 3} + 4 \phantom{+ 5} + 6 &= 12
\end{align*}
$$
```
$$
\begin{align*}
    1 \phantom{+ 2} + 3 \phantom{+ 4} + 5 \phantom{+ 6} &= 9 \\
    \phantom{+ 1} + 2 \phantom{+ 3} + 4 \phantom{+ 5} + 6 &= 12
\end{align*}
$$

### 数学符号

公式中可以插入各种符号。前往[这里]({{ url_for('helps', howto='write-katex-symbols') }})查看符号表。

### 插入正文文字

使用 `\text` 命令在公式中插入文字，例如：
```latex
$$ E = mc^2 \Rightarrow \text{能量} = \text{质量} \times \text{光速}^2 $$
```
$$ E = mc^2 \Rightarrow \text{能量} = \text{质量} \times \text{光速}^2 $$

若要在 `\text` 的内容中插入行内公式，需要使用 `$...$` 将公式包围：
```latex
$$ \text{能量 $E$} = \text{质量 $m$} \times \text{光速 $c$}^2 $$
```
$$ \text{能量 $E$} = \text{质量 $m$} \times \text{光速 $c$}^2 $$

## 多行公式排版

参见[此处]({{ url_for('helps', howto='write-katex-multiline') }})。

## 参考与引用

我们在编写这一文档时，参考了《$\LaTeX$ 入门》一书中的第四章有关公式的内容。如有侵权，请联系删除。

本篇内容仅包含常用的公式用法，难免有疏漏之处，有关 $\KaTeX$ 公式的所有内容参见[此处](https://katex.org/docs/support_table)。
