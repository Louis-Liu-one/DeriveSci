# 如何编写 Markdown 公式

## 摘要

Markdown 是一种轻量级标记语言。我们的网站中所有的题目、题解、评论等需要或可能需要格式化排版的内容全部使用 Markdown 输入。由于 Markdown 公式内容较多，故单分为此篇。其它 Markdown 语法可以在[此处]({{ url_for('helps', howto='write-markdown') }})找到。

## 公式语法基础

### 行内公式与行间公式

在 Markdown 中，数学公式以 $\LaTeX$ 语法展示。行内公式以 `$` 符号包围，行间公式以 `$$` 符号包围。例如：`$x^2 + 2x + 1$` 渲染得到 $x^2 + 2x + 1$，
```
$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$
```
$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$

### 分组与整体

将多个字符用 `{...}` 包围，就得到一个**分组**。单个字符、无参数命令或分组被视为一个**整体**。

### 命令

公式中的**命令**以 `\` 开头，后面跟着一系列大写或小写字母，例如 `\alpha`、`\beta`。

命令可以带有参数。一个接受 $n$ 个参数的命令，其后的 $n$ 个整体被视为其参数。命令也可以带有可选参数，可选参数必须使用 `[...]` 包围。例如：

命令 | 渲染效果
--- | ---
`\alpha` | $\alpha$
`\sqrt[n]{13}` | $\sqrt[n]{13}$
`\frac1{x + 1}` | $\frac1{x + 1}$
`\frac{x + 1}2` | $\frac{x + 1}2$
`\frac xy` | $\frac xy$
`\sqrt2` | $\sqrt2$
`p^\alpha, q^\beta, \dots` | $p^\alpha, q^\beta, \dots$

需要注意的是，上述例子中的 `\frac xy` 不能写作 `\fracxy`，因为这样 `\fracxy` 会被视为一个命令，而非 `\frac{x}{y}`。

### 环境

一个**环境**以 `\begin{环境名}` 始，至 `\end{环境名}` 止。环境可以接受参数，其格式与命令参数的格式相同。被环境包围的内容称为环境的**内容**。例如，可以使用 `pmatrix` 环境创建矩阵：
```
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

公式中可以使用 `\` 将字符进行转义，避免其被解析。

转义 | 效果 | 转义 | 效果 | 转义 | 效果
:-: | :-: | :-: | :-: | :-: | :-:
`\%` | $\%$ | `\$` | $\$$ | `\&` | $\&$
`\#` | $\#$ | `\_` | $\_$ | `\{` | $\{$
`\}` | $\}$ | `\backslash` | $\backslash$

## 数学结构

### 上标与下标

#### 一般上下标

使用 `^` 符号插入上标，`_` 符号插入下标。例如：

命令 | 渲染效果
--- | ---
`e^x` | $e^x$
`(x + y)^2` | $(x + y)^2$
`a^{x + y} = a^x \cdot a^y` | $a^{x + y} = a^x \cdot a^y$
`F_n = F_{n - 1} + F_{n - 2}` | $F_n = F_{n - 1} + F_{n - 2}$

可见，上标或下标的用法与命令基本相同，其将其后的一个[整体](#分组与整体)视为上下标的内容。上标或下标前面的内容，如上例中的 $e$、$(x + y)$、$a$、$F$，任何时候都不需要用花括号包围。

上标和下标可以嵌套使用，例如 `2^{2^x} + 1` 得到 $2^{2^x} + 1$。然而，嵌套使用上下标时，大括号不可少，例如 `2^2^x + 1` 是错误的。

#### 特殊符号上下标

对于 $\max$、$\min$、$\sum$、$\prod$ 等算子，其在行间公式模式下的上下标在其正上下方。例如：
```
$$ \sum_{n = 1}^\infty \frac1{n^s} = \prod_p \frac1{1 - p^{-s}} $$
```
$$ \sum_{n = 1}^\infty \frac1{n^s} = \prod_p \frac1{1 - p^{-s}} $$

对于 $\int$ 等符号，其在行间公式模式下的上下标通常在角落处，例如：
```
$$ I = \int_0^{+\infty} \frac{\sin x}x \mathrm dx $$
```
$$ I = \int_0^{+\infty} \frac{\sin x}x \mathrm dx $$

#### 行内公式上下标

对于行内公式，无论算符，上下标都在右上角或右下角，例如行内公式 `\sum_{n = 0}^\infty` 得到 $\sum_{n = 0}^\infty$。

#### 改变上下标的位置

可以在上下标前使用 `\limits`、`\nolimits` 命令改变上下标的位置。例如在行内公式中：

命令 | 渲染效果
--- | ---
`\sum_{n = 0}^\infty` | $\sum_{n = 0}^\infty$
`\sum\limits_{n = 0}^\infty` | $\sum\limits_{n = 0}^\infty$

行间公式中：
```
$$ \sum\nolimits_{n = 0}^\infty $$
```
$$ \sum\nolimits_{n = 0}^\infty $$

### 分式与二项式系数

#### 分式

使用 `\frac` 命令渲染分式。其接受两个参数，分别表示分子和分母。例如，`\frac{x + 1}{x - 1}` 在行内渲染得到 $\frac{x + 1}{x - 1}$。

行内分式与行间分式的渲染结果不同。上例在行间分式中的表现为
$$ \frac{x + 1}{x - 1} $$
可以使用 `\tfrac`、`\dfrac` 命令指定分式渲染使用行内还是行间模式。例如：
```
$$ f = \frac1{\dfrac1u + \dfrac1v} $$
```
$$ f = \frac1{\dfrac1u + \dfrac1v} $$
以及
```
$$ \tfrac n{H_n} = \sum\nolimits_{i = 1}^n \tfrac1{x_i} $$
```
$$ \tfrac n{H_n} = \sum\nolimits_{i = 1}^n \tfrac1{x_i} $$

即使在行间公式中，位于分子或分母上的分式也会按照行内模式渲染。此时，就可以使用 `\dfrac` 命令指定仍使用行间模式。

#### 二项式系数

使用 `\binom` 命令渲染二项式系数，其用法与 `\frac` 命令相同。例如：
```
$$ \binom nk = \frac{n!}{k!(n - k)!} $$
```
$$ \binom nk = \frac{n!}{k!(n - k)!} $$
也可以使用 `n \choose k` 得到相同的结果。与 `\frac` 相似，`\binom` 命令也有孪生的 `\tbinom`、`\dbinom` 命令指定行内或行间模式。

#### 自定义分式

使用 `\genfrac` 命令自定义分式。其接受六个参数，如下：
```
\genfrac{左括号}{右括号}{线宽}{样式}{分子}{分母}
```
其中样式的意义是：

样式 | 对应命令 | 意义
--- | --- | ---
0 | `\displaystyle` | 行间模式
1 | `\textstyle` | 行内模式
2 | `\scriptstyle` | 角标模式
3 | `\scriptscriptstyle` | 小角标模式

指定渲染分式的模式。若置空，则模式由当前所处位置决定。

以下是例子：
```
$$ \genfrac{\{}{\}}{1pt}{}nk $$
```
$$ \genfrac{\{}{\}}{1pt}{}nk $$

### 根式、上下划线与上下括号

#### 根式

使用 `\sqrt` 命令渲染根式。其接受一个可选参数，表示几次根。

命令 | 渲染效果
--- | ---
`\sqrt x \cdot \sqrt y = \sqrt{xy} \quad (x, y > 0)` | $\sqrt x \cdot \sqrt y = \sqrt{xy} \quad (x, y > 0)$
`\sqrt[n]x = x^{\frac1n}` | $\sqrt[n]x = x^{\frac1n}$

注意到在使用 `\sqrt x + \sqrt y` 渲染 $\sqrt x + \sqrt y$ 时，左右高度不同，此时可以使用 `\mathstrut` 命令控制：
```
$\sqrt{\mathstrut x} + \sqrt{\mathstrut y}$
```
渲染得到 $\sqrt{\mathstrut x} + \sqrt{\mathstrut y}$。

#### 上下划线与上下括号

使用 `\overline`、`\underline` 等命令创建上下划线：

命令 | 渲染效果 | 命令 | 渲染效果
:---: | :---: | :---: | :---:
`\underline{x + y}` | $\underline{x + y}$ | `\overline{x + y}` | $\overline{x + y}$
`\underleftarrow{x + y}` | $\underleftarrow{x + y}$ | `\overleftarrow{x + y}` | $\overleftarrow{x + y}$
`\underrightarrow{x + y}` | $\underrightarrow{x + y}$ | `\overrightarrow{x + y}` | $\overrightarrow{x + y}$
`\underleftrightarrow{x + y}` | $\underleftrightarrow{x + y}$ | `\overleftrightarrow{x + y}` | $\overleftrightarrow{x + y}$
`\underbrace{x + y}` | $\underbrace{x + y}$ | `\overbrace{x + y}` | $\overbrace{x + y}$

上下划线与上下括号可以嵌套。划线与括号高度同样可以使用 `\mathstrut` 控制。

### 矩阵

可以使用 `matrix`、`pmatrix` 等环境创建矩阵。具体用法如下：
```
\begin{矩阵环境名}
    a & b & c \\
    d & e & f \\
    g & h & i
\end{矩阵环境名}
```
使用 `\\` 分隔矩阵的每行，使用 `&` 分隔矩阵的每列。以下是一些矩阵环境及效果：

环境 | 渲染效果 | 环境 | 渲染效果 | 环境 | 渲染效果
:---: | :---: | :---: | :---: | :---: | :---:
`matrix` | $\begin{matrix} a & b \\ c & d \end{matrix}$ | `bmatrix` | $\begin{bmatrix} a & b \\ c & d \end{bmatrix}$ | `vmatrix` | $\begin{vmatrix} a & b \\ c & d \end{vmatrix}$
`pmatrix` | $\begin{pmatrix} a & b \\ c & d \end{pmatrix}$ | `Bmatrix` | $\begin{Bmatrix} a & b \\ c & d \end{Bmatrix}$ | `Vmatrix` | $\begin{Vmatrix} a & b \\ c & d \end{Vmatrix}$

矩阵中可以使用 `\cdots`、`\vdots` 等省略号：
```
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

## 字体、符号与文字

### 数学字体

#### 字体样式

除了默认字体，还可以使用 `\mathrm` 等命令使用其它数学字体，使用方法是 `\mathrm{...}`。以下是一些数学字体及其渲染效果：

命令 | 名称 | 字母效果 | 数字效果
:----------------: | :----: | :-: | :-:
`\mathnormal{...}` | 默认字体 | $ABCDEFGHIJKLMNOPQRSTUVWXYZ$ | $1234567890$
`\mathit{...}`     | 意大利体 | $\mathit{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathit{1234567890}$
`\mathrm{...}`     | 罗马体 | $\mathrm{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathrm{1234567890}$
`\mathsf{...}`     | 无衬线体 | $\mathsf{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathsf{1234567890}$
`\mathtt{...}`     | 打字机体 | $\mathtt{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathtt{1234567890}$
`\mathbb{...}`     | 黑板体 | $\mathbb{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathbb{1234567890}$
`\mathcal{...}`    | 书法体 | $\mathcal{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathcal{1234567890}$
`\mathscr{...}`    | 花体 | $\mathscr{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathscr{1234567890}$
`\mathfrak{...}`   | 哥特体 | $\mathfrak{ABCDEFGHIJKLMNOPQRSTUVWXYZ}$ | $\mathfrak{1234567890}$

例如，可以使用 `\mathrm dx` 渲染 $\mathrm dx$。注意，由于这里没有显式指定参数，命令后的第一个整体，即 `d` 被指定为第一个参数，故只有 `d` 被渲染为罗马体。

#### 字体大小

可以使用如下四个命令调整字体大小：

命令 | 名称 | 渲染效果
:-----------------------: | :----: | :-:
`\displaystyle{...}`      | 行间模式 | $\displaystyle{\frac{x + 1}{x + 2}}$
`\textstyle{...}`         | 行内模式 | $\textstyle{\frac{x + 1}{x + 2}}$
`\scriptstyle{...}`       | 角标模式 | $\scriptstyle{\frac{x + 1}{x + 2}}$
`\scriptscriptstyle{...}` | 小角标模式 | $\scriptscriptstyle{\frac{x + 1}{x + 2}}$

### 符号

公式中可以使用各种符号。

#### 希腊字母

下列是常用的小写希腊字母：

命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果
:--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------:
`\alpha`   | $\alpha$   | `\beta`    | $\beta$    | `\gamma`   | $\gamma$   | `\delta`   | $\delta$
`\epsilon` | $\epsilon$ | `\zeta`    | $\zeta$    | `\eta`     | $\eta$     | `\theta`   | $\theta$
`\iota`    | $\iota$    | `\kappa`   | $\kappa$   | `\lambda`  | $\lambda$  | `\mu`      | $\mu$
`\nu`      | $\nu$      | `\xi`      | $\xi$      | `\pi`      | $\pi$      | `\rho`     | $\rho$
`\sigma`   | $\sigma$   | `\tau`     | $\tau$     | `\upsilon` | $\upsilon$ | `\phi`     | $\phi$
`\chi`     | $\chi$     | `\psi`     | $\psi$     | `\omega`   | $\omega$
`\varepsilon` | $\varepsilon$ | `\vartheta` | $\vartheta$ | `\varkappa` | $\varkappa$ | `\varpi` | $\varpi$
`\varrho` | $\varrho$ | `\varsigma` | $\varsigma$ | `\varphi` | $\varphi$ | `\digamma` | $\digamma$

下列是常用的大写希腊字母：

命令 | 效果 | 变体 | 效果 | 命令 | 效果 | 变体 | 效果
:--------: | :--------: | :-----------: | :-----------: | :--------: | :--------: | :-----------: | :-----------:
`\Gamma`   | $\Gamma$   | `\varGamma`   | $\varGamma$   | `\Delta`   | $\Delta$   | `\varDelta`   | $\varDelta$
`\Theta`   | $\Theta$   | `\varTheta`   | $\varTheta$   | `\Lambda`  | $\Lambda$  | `\varLambda`  | $\varLambda$
`\Xi`      | $\Xi$      | `\varXi`      | $\varXi$      | `\Pi`      | $\Pi$      | `\varPi`      | $\varPi$
`\Sigma`   | $\Sigma$   | `\varSigma`   | $\varSigma$   | `\Upsilon` | $\Upsilon$ | `\varUpsilon` | $\varUpsilon$
`\Phi`     | $\Phi$     | `\varPhi`     | $\varPhi$     | `\Psi`     | $\Psi$     | `\varPsi`     | $\varPsi$
`\Omega`   | $\Omega$   | `\varOmega`   | $\varOmega$

上面所有以 `\var` 开头的命令都是原命令的变体。

#### 重音

下列是一些数学重音：

命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果
:---------: | :-----------: | :---------: | :-----------: | :---------: | :-----------: | :---------: | :-----------: |
`\acute`    | $\acute x$    | `\grave`    | $\grave x$    | `\ddot`     | $\ddot x$     | `\dddot`    | $\dddot x$    |
`\ddddot`   | $\ddddot x$   | `\tilde`    | $\tilde x$    | `\bar`      | $\bar x$      | `\breve`    | $\breve x$    |
`\check`    | $\check x$    | `\hat`      | $\hat x$      | `\vec`      | $\vec x$      | `\dot`      | $\dot x$      |
`\mathring` | $\mathring x$ | `\widetilde` | $\widetilde{abc}$ | `\widehat` | $\widehat{abc}$

数学重音可以嵌套使用，例如 `\hat{\bar x}` 得到 $\hat{\bar x}$。

#### 普通符号

下列是一些数学普通符号：

命令 | 效果 | 命令 | 效果 | 命令 | 效果
:------------------: | :------------------: | :------------------: | :------------------: | :------------------: | :--------------------:
`\hbar`              | $\hbar$              | `\imath`             | $\imath$             | `\jmath`             | $\jmath$
`\ell`               | $\ell$               | `\wp`                | $\wp$                | `\Re`                | $\Re$
`\Im`                | $\Im$                | `\partial`           | $\partial$           | `\infty`             | $\infty$
`\prime`             | $\prime$             | `\emptyset`          | $\emptyset$          | `\nabla`             | $\nabla$
`\surd`              | $\surd$              | `\top`               | $\top$               | `\bot`               | $\bot$
`\angle`             | $\angle$             | `\triangle`          | $\triangle$          | `\forall`            | $\forall$
`\exists`            | $\exists$            | `\neg`               | $\neg$               | `\flat`              | $\flat$
`\natural`           | $\natural$           | `\sharp`             | $\sharp$             | `\clubsuit`          | $\clubsuit$
`\diamondsuit`       | $\diamondsuit$       | `\heartsuit`         | $\heartsuit$         | `\spadesuit`         | $\spadesuit$
`\backslash`         | $\backslash$         | `\backprime`         | $\backprime$         | `\hslash`            | $\hslash$
`\varnothing`        | $\varnothing$        | `\vartriangle`       | $\vartriangle$       | `\blacktriangle`     | $\blacktriangle$
`\triangledown`      | $\triangledown$      | `\blacktriangledown` | $\blacktriangledown$ | `\square`            | $\square$
`\blacksquare`       | $\blacksquare$       | `\lozenge`           | $\lozenge$           | `\blacklozenge`      | $\blacklozenge$
`\circledS`          | $\circledS$          | `\bigstar`           | $\bigstar$           | `\sphericalangle`    | $\sphericalangle$
`\measuredangle`     | $\measuredangle$     | `\nexists`           | $\nexists$           | `\complement`        | $\complement$
`\mho`               | $\mho$               | `\eth`               | $\eth$               | `\Finv`              | $\Finv$
`\diagup`            | $\diagup$            | `\Game`              | $\Game$              | `\diagdown`          | $\diagdown$
`\Bbbk`              | $\Bbbk$

#### 数学算子

##### 带上下标的算子

**数学算子**包括带上下标、大小可变的算子，例如 $\sum$、$\int$ 等，被称为**巨算符**。下列是一些常用的巨算符：

命令 | 效果 | 命令 | 效果 | 命令 | 效果
:----------: | :--------------------------------------------: | :----------: | :--------------------------------------------: | :----------: | :--------------------------------------------:
`\sum`       | $\textstyle\sum \displaystyle\sum$             | `\prod`      | $\textstyle\prod \displaystyle\prod$           | `\coprod`    | $\textstyle\coprod \displaystyle\coprod$
`\int`       | $\textstyle\int \displaystyle\int$             | `\iint`      | $\textstyle\iint \displaystyle\iint$           | `\iiint`     | $\textstyle\iiint \displaystyle\iiint$
`\oint`      | $\textstyle\oint \displaystyle\oint$           | `\bigcup`    | $\textstyle\bigcup \displaystyle\bigcup$       | `\biguplus`  | $\textstyle\biguplus \displaystyle\biguplus$
`\bigsqcup`  | $\textstyle\bigsqcup \displaystyle\bigsqcup$   | `\bigvee`    | $\textstyle\bigvee \displaystyle\bigvee$       | `\bigwedge`  | $\textstyle\bigwedge \displaystyle\bigwedge$
`\bigcap`    | $\textstyle\bigcap \displaystyle\bigcap$       | `\bigodot`   | $\textstyle\bigodot \displaystyle\bigodot$     | `\bigoplus`  | $\textstyle\bigoplus \displaystyle\bigoplus$
`\bigotimes` | $\textstyle\bigotimes \displaystyle\bigotimes$

还有一些带上下标的算子，但仅由罗马体字母组成：

命令 | 效果 | 命令 | 效果 | 命令 | 效果
:-----------: | :-----------: | :-----------: | :-----------: | :-----------: | :-----------:
`\lim`        | $\lim$        | `\limsup`     | $\limsup$     | `\liminf`     | $\liminf$
`\max`        | $\max$        | `\min`        | $\min$        | `\sup`        | $\sup$
`\inf`        | $\inf$        | `\det`        | $\det$        | `\Pr`         | $\Pr$
`\gcd`        | $\gcd$        | `\varliminf`  | $\varliminf$  | `\varlimsup`  | $\varlimsup$
`\injlim`     | $\injlim$     | `\projlim`    | $\projlim$    | `\varinjlim`  | $\varinjlim$
`\varprojlim` | $\varprojlim$

这类算子的上下标一般在上方、下方或角落处，参见[特殊符号上下标](#特殊符号上下标)一节。

可以使用 `\limits`、`\nolimits` 等命令控制上下标的位置，参见[改变上下标的位置](#改变上下标的位置)一节。

##### 普通算子

另一类数学算子，其不带上下标，或上下标样式与普通字符相同，如 $\log$ 等：

命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果
:-------: | :------: | :------: | :------: | :------: | :------: | :------: | :-----: | :------: | :-------:
`\log`    | $\log$   |`\lg`     | $\lg$    |`\ln`     | $\ln$    |`\sin`    | $\sin$   |`\arcsin` | $\arcsin$
`\cos`    | $\cos$   |`\arccos` | $\arccos$|`\tan`    | $\tan$   |`\arctan` | $\arctan$|`\cot`    | $\cot$
`\sinh`   | $\sinh$  |`\cosh`   | $\cosh$  |`\tanh`   | $\tanh$  |`\coth`   | $\coth$  |`\sec`    | $\sec$
`\csc`    | $\csc$   |`\arg`    | $\arg$   |`\ker`    | $\ker$   |`\dim`    | $\dim$   |`\hom`    | $\hom$
`\exp`    | $\exp$   |`\deg`    | $\deg$

##### 自定义算子

可以使用 `\operatorname` 命令临时自定义算子，例如：
```
$$ \operatorname{lcm}(a, b) \cdot \gcd(a, b) = a \cdot b $$
```
$$ \operatorname{lcm}(a, b) \cdot \gcd(a, b) = a \cdot b $$
也可以使用 `\operatorname*` 命令定义带有特殊上下标样式的算子：
```
$$ \lim_{x \to 0} \quad \operatorname{lim}_{x \to 0} \quad \operatorname*{lim}_{x \to 0} $$
```
$$ \lim_{x \to 0} \quad \operatorname{lim}_{x \to 0} \quad \operatorname*{lim}_{x \to 0} $$
这一例子中可以明显地看出它们的区别。

#### 运算符与关系符（待编）

#### 括号与定界符（待编）

#### 数学标点与省略号（待编）

### 正文文字

使用 `\text` 命令在公式中插入文字，例如：
```
$$ E = mc^2 \Rightarrow \text{能量} = \text{质量} \times \text{光速}^2 $$
```
$$ E = mc^2 \Rightarrow \text{能量} = \text{质量} \times \text{光速}^2 $$

若要在 `\text` 的内容中插入行内公式，需要使用 `\(...\)` 将公式包围。
