# 如何编写 Markdown 公式之符号表

## 摘要

在 Markdown 公式中，可以使用各种符号。本节将提供大量 Markdown 公式中可用的符号，并按照小节分类。你不必——当然也不可能——将它们全部记住，需要时在此处查阅或上网搜索即可。

## 希腊字母

下列是常用的**小写希腊字母**：

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

下列是常用的**大写希腊字母**：

命令 | 效果 | 变体 | 效果 | 命令 | 效果 | 变体 | 效果
:--------: | :--------: | :-----------: | :-----------: | :--------: | :--------: | :-----------: | :-----------:
`\Gamma`   | $\Gamma$   | `\varGamma`   | $\varGamma$   | `\Delta`   | $\Delta$   | `\varDelta`   | $\varDelta$
`\Theta`   | $\Theta$   | `\varTheta`   | $\varTheta$   | `\Lambda`  | $\Lambda$  | `\varLambda`  | $\varLambda$
`\Xi`      | $\Xi$      | `\varXi`      | $\varXi$      | `\Pi`      | $\Pi$      | `\varPi`      | $\varPi$
`\Sigma`   | $\Sigma$   | `\varSigma`   | $\varSigma$   | `\Upsilon` | $\Upsilon$ | `\varUpsilon` | $\varUpsilon$
`\Phi`     | $\Phi$     | `\varPhi`     | $\varPhi$     | `\Psi`     | $\Psi$     | `\varPsi`     | $\varPsi$
`\Omega`   | $\Omega$   | `\varOmega`   | $\varOmega$

上面所有以 `\var` 开头的命令都是原命令的变体或斜体。

## 重音

下列是一些**数学重音**：

命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果
:---------: | :-----------: | :---------: | :-----------: | :---------: | :-----------: | :---------: | :-----------: |
`\acute`    | $\acute x$    | `\grave`    | $\grave x$    | `\ddot`     | $\ddot x$     | `\dddot`    | $\dddot x$    |
`\ddddot`   | $\ddddot x$   | `\tilde`    | $\tilde x$    | `\bar`      | $\bar x$      | `\breve`    | $\breve x$    |
`\check`    | $\check x$    | `\hat`      | $\hat x$      | `\vec`      | $\vec x$      | `\dot`      | $\dot x$      |
`\mathring` | $\mathring x$ | `\widetilde` | $\widetilde{abc}$ | `\widehat` | $\widehat{abc}$

数学重音可以嵌套使用，例如 `\hat{\bar x}` 得到 $\hat{\bar x}$。

## 普通符号

下列是一些**数学普通符号**：

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

数学普通符号在公式中与单个字符渲染效果几乎等同。

## 数学算子

### 带上下标的算子

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

这类算子的上下标一般在上方、下方或角落处，参见[特殊符号上下标]({{ url_for('helps', howto='write-markdown-equations', _anchor='特殊符号上下标') }})一节。

可以使用 `\limits`、`\nolimits` 等命令控制上下标的位置，参见[改变上下标的位置]({{ url_for('helps', howto='write-markdown-equations', _anchor='改变上下标的位置') }})一节。

### 普通算子

另一类数学算子，其不带上下标，或上下标样式与普通字符相同，如 $\log$ 等：

命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果
:-------: | :------: | :------: | :------: | :------: | :------: | :------: | :-----: | :------: | :-------:
`\log`    | $\log$   |`\lg`     | $\lg$    |`\ln`     | $\ln$    |`\sin`    | $\sin$   |`\arcsin` | $\arcsin$
`\cos`    | $\cos$   |`\arccos` | $\arccos$|`\tan`    | $\tan$   |`\arctan` | $\arctan$|`\cot`    | $\cot$
`\sinh`   | $\sinh$  |`\cosh`   | $\cosh$  |`\tanh`   | $\tanh$  |`\coth`   | $\coth$  |`\sec`    | $\sec$
`\csc`    | $\csc$   |`\arg`    | $\arg$   |`\ker`    | $\ker$   |`\dim`    | $\dim$   |`\hom`    | $\hom$
`\exp`    | $\exp$   |`\deg`    | $\deg$

### 自定义算子

可以使用 `\operatorname` 命令临时自定义算子，例如：
```latex
$$ \operatorname{lcm}(a, b) \cdot \gcd(a, b) = a \cdot b $$
```
$$ \operatorname{lcm}(a, b) \cdot \gcd(a, b) = a \cdot b $$
也可以使用 `\operatorname*` 命令定义带有特殊上下标样式的算子：
```latex
$$ \lim_{x \to 0} \quad \operatorname{lim}_{x \to 0} \quad \operatorname*{lim}_{x \to 0} $$
```
$$ \lim_{x \to 0} \quad \operatorname{lim}_{x \to 0} \quad \operatorname*{lim}_{x \to 0} $$
这一例子中可以明显地看出它们的区别。

## 运算符与关系符

### 二元运算符

在公式中可以插入一些**二元运算符**。二元运算符中，$+$、$-$、$*$ 可以直接使用 `+`、`-`、`*` 字符渲染，还有其它一些二元运算符需要使用命令渲染，如下：

命令 | 效果 | 命令 | 效果 | 命令 | 效果
:----------------: | :----------------: | :---------------: | :----------------: | :---------------: | :----------------:
`\Cap` 或 `\doublecap` | $\Cap$             |`\Cup` 或 `\doublecup` | $\Cup$             |`\amalg`           | $\amalg$
`\ast` 或 `*`      | $\ast$             |`\barwedge`        | $\barwedge$        |`\bigcirc`         | $\bigcirc$
`\bigtriangledown` | $\bigtriangledown$ |`\bigtriangleup`   | $\bigtriangleup$   |`\boxdot`          | $\boxdot$
`\boxminus`        | $\boxminus$        |`\boxplus`         | $\boxplus$         |`\bullet`          | $\bullet$
`\cap`             | $\cap$             |`\cdot`            | $\cdot$            |`\centerdot`       | $\centerdot$
`\circ`            | $\circ$            |`\circledast`      | $\circledast$      |`\circledcirc`     | $\circledcirc$
`\circleddash`     | $\circleddash$     |`\cup`             | $\cup$             |`\curlyvee`        | $\curlyvee$
`\curlywedge`      | $\curlywedge$      |`\dagger`          | $\dagger$          |`\ddagger`         | $\ddagger$
`\diamond`         | $\diamond$         |`\div`             | $\div$             |`\divideontimes`   | $\divideontimes$
`\dotplus`         | $\dotplus$         |`\doublebarwedge`  | $\doublebarwedge$  |`\intercal`        | $\intercal$
`\leftthreetimes`  | $\leftthreetimes$  |`\lhd`             | $\lhd$             |`\ltimes`          | $\ltimes$
`\mp`              | $\mp$              |`\odot`            | $\odot$            |`\oplus`           | $\oplus$
`\oslash`          | $\oslash$          |`\otimes`          | $\otimes$          |`\pm`              | $\pm$
`\rhd`             | $\rhd$             |`\rightthreetimes` | $\rightthreetimes$ |`\rtimes`          | $\rtimes$
`\setminus`        | $\setminus$        |`\smallsetminus`   | $\smallsetminus$   |`\sqcap`           | $\sqcap$
`\sqcup`           | $\sqcup$           |`\star`            | $\star$            |`\times`           | $\times$
`\triangleleft`    | $\triangleleft$    |`\triangleright`   | $\triangleright$   |`\unlhd`           | $\unlhd$
`\unrhd`           | $\unrhd$           |`\uplus`           | $\uplus$           |`\vee` 或 `\lor`   | $\vee$
`\veebar`          | $\veebar$          |`\wedge` 或 `\land` | $\wedge$           |`\wr`              | $\wr$

使用 `\mathbin` 命令将其参数当作二元运算符处理。例如：
```latex
$$ a \heartsuit b \quad a \mathbin\heartsuit b $$
```
$$ a \heartsuit b \quad a \mathbin\heartsuit b $$
两者区别明显可见。

### 二元关系符

在公式中可以插入一些**二元关系符**。二元关系符中，$=$、$>$、$<$、$:$ 等可以直接使用 `=`、`>`、`<`、`:` 等字符渲染，还有其它一些二元关系符需要使用命令渲染，如下：

命令 | 效果 | 命令 | 效果 | 命令 | 效果
:-------------------: | :-------------------: | :------------------: | :-------------------: | :------------------: | :-------------------:
`\Bumpeq`             | $\Bumpeq$             |`\Join`               | $\Join$               |`\Subset`             | $\Subset$
`\Supset`             | $\Supset$             |`\Vdash`              | $\Vdash$              |`\Vvdash`             | $\Vvdash$
`\approx`             | $\approx$             |`\approxeq`           | $\approxeq$           |`\asymp`              | $\asymp$
`\backepsilon`        | $\backepsilon$        |`\backsim`            | $\backsim$            |`\backsimeq`          | $\backsimeq$
`\because`            | $\because$            |`\between`            | $\between$            |`\blacktriangleleft`  | $\blacktriangleleft$
`\blacktriangleright` | $\blacktriangleright$ |`\bowtie`             | $\bowtie$             |`\bumpeq`             | $\bumpeq$
`\circeq`             | $\circeq$             |`\cong`               | $\cong$               |`\dashv`              | $\dashv$
`\doteq`              | $\doteq$              |`\doteqdot`           | $\doteqdot$           |`\eqcirc`             | $\eqcirc$
`\eqslantgtr`         | $\eqslantgtr$         |`\eqslantless`        | $\eqslantless$        |`\equiv`              | $\equiv$
`\fallingdotseq`      | $\fallingdotseq$      |`\frown`              | $\frown$              |`\ge` 或 `\geq`       | $\ge$
`\geqq`               | $\geqq$               |`\geqslant`           | $\geqslant$           |`\gg`                 | $\gg$
`\ggg`                | $\ggg$                |`\gtrapprox`          | $\gtrapprox$          |`\gtrdot`             | $\gtrdot$
`\gtreqless`          | $\gtreqless$          |`\gtreqqless`         | $\gtreqqless$         |`\gtrless`            | $\gtrless$
`\gtrsim`             | $\gtrsim$             |`\in`                 | $\in$                 |`\le` 或 `\leq`       | $\le$
`\leqq`               | $\leqq$               |`\leqslant`           | $\leqslant$           |`\lessapprox`         | $\lessapprox$
`\lessdot`            | $\lessdot$            |`\lesseqgtr`          | $\lesseqgtr$          |`\lesseqqgtr`         | $\lesseqqgtr$
`\lessgtr`            | $\lessgtr$            |`\lesssim`            | $\lesssim$            |`\ll`                 | $\ll$
`\lll`                | $\lll$                |`\mid`                | $\mid$                |`\models`             | $\models$
`\ni` 或 `\owns`      | $\ni$                 |`\parallel`           | $\parallel$           |`\perp`               | $\perp$
`\pitchfork`          | $\pitchfork$          |`\prec`               | $\prec$               |`\precapprox`         | $\precapprox$
`\preccurlyeq`        | $\preccurlyeq$        |`\preceq`             | $\preceq$             |`\precsim`            | $\precsim$
`\propto`             | $\propto$             |`\risingdotseq`       | $\risingdotseq$       |`\shortmid`           | $\shortmid$
`\shortparallel`      | $\shortparallel$      |`\sim`                | $\sim$                |`\simeq`              | $\simeq$
`\smallfrown`         | $\smallfrown$         |`\smallsmile`         | $\smallsmile$         |`\smile`              | $\smile$
`\sqsubset`           | $\sqsubset$           |`\sqsubseteq`         | $\sqsubseteq$         |`\sqsupset`           | $\sqsupset$
`\sqsupseteq`         | $\sqsupseteq$         |`\subset`             | $\subset$             |`\subseteq`           | $\subseteq$
`\subseteqq`          | $\subseteqq$          |`\succ`               | $\succ$               |`\succapprox`         | $\succapprox$
`\succcurlyeq`        | $\succcurlyeq$        |`\succeq`             | $\succeq$             |`\succsim`            | $\succsim$
`\supset`             | $\supset$             |`\supseteq`           | $\supseteq$           |`\supseteqq`          | $\supseteqq$
`\therefore`          | $\therefore$          |`\thickapprox`        | $\thickapprox$        |`\thicksim`           | $\thicksim$
`\trianglelefteq`     | $\trianglelefteq$     |`\triangleq`          | $\triangleq$          |`\trianglerighteq`    | $\trianglerighteq$
`\vDash`              | $\vDash$              |`\varpropto`          | $\varpropto$          |`\vartriangleleft`    | $\vartriangleleft$
`\vartriangleright`   | $\vartriangleright$   |`\vdash`              | $\vdash$

一些二元关系符具有否定形式。一般来说，可以使用 `\not` 命令将二元关系符变为其否定形式，例如 `\not\in` 渲染得到 $\not\in$。然而，一些二元关系符的否定形式具有专门的命令，例如 `\notin` 渲染得到 $\notin$，其效果比直接使用 `\not\in` 更好。

以下是一些二元关系符的否定形式：

命令 | 效果 | 命令 | 效果 | 命令 | 效果
:-----------------: | :-----------------: | :----------------: | :-----------------: | :-----------------: | :----------------:
`\gnapprox`         | $\gnapprox$         |`\gneq`             | $\gneq$             |`\gneqq`            | $\gneqq$
`\gnsim`            | $\gnsim$            |`\gvertneqq`        | $\gvertneqq$        |`\lnapprox`         | $\lnapprox$
`\lneq`             | $\lneq$             |`\lneqq`            | $\lneqq$            |`\lnsim`            | $\lnsim$
`\lvertneqq`        | $\lvertneqq$        |`\nVDash`           | $\nVDash$           |`\nVdash`           | $\nVdash$
`\ncong`            | $\ncong$            |`\ne` 或 `\neq`     | $\ne$               |`\ngeq`             | $\ngeq$
`\ngeqq`            | $\ngeqq$            |`\ngeqslant`        | $\ngeqslant$        |`\ngtr`             | $\ngtr$
`\nleq`             | $\nleq$             |`\nleqq`            | $\nleqq$            |`\nleqslant`        | $\nleqslant$
`\nless`            | $\nless$            |`\nmid`             | $\nmid$             |`\notin`            | $\notin$
`\nparallel`        | $\nparallel$        |`\nprec`            | $\nprec$            |`\npreceq`          | $\npreceq$
`\nshortmid`        | $\nshortmid$        |`\nshortparallel`   | $\nshortparallel$   |`\nsim`             | $\nsim$
`\nsubseteq`        | $\nsubseteq$        |`\nsubseteqq`       | $\nsubseteqq$       |`\nsucc`            | $\nsucc$
`\nsucceq`          | $\nsucceq$          |`\nsupseteq`        | $\nsupseteq$        |`\nsupseteqq`       | $\nsupseteqq$
`\ntriangleleft`    | $\ntriangleleft$    |`\ntrianglelefteq`  | $\ntrianglelefteq$  |`\ntriangleright`   | $\ntriangleright$
`\ntrianglerighteq` | $\ntrianglerighteq$ |`\nvDash`           | $\nvDash$           |`\nvdash`           | $\nvdash$
`\precnapprox`      | $\precnapprox$      |`\precneqq`         | $\precneqq$         |`\precnsim`         | $\precnsim$
`\subsetneq`        | $\subsetneq$        |`\subsetneqq`       | $\subsetneqq$       |`\succnapprox`      | $\succnapprox$
`\succneqq`         | $\succneqq$         |`\succnsim`         | $\succnsim$         |`\supsetneq`        | $\supsetneq$
`\supsetneqq`       | $\supsetneqq$       |`\varsubsetneq`     | $\varsubsetneq$     |`\varsubsetneqq`    | $\varsubsetneqq$
`\varsupsetneq`     | $\varsupsetneq$     |`\varsupsetneqq`    | $\varsupsetneqq$

使用 `\mathrel` 命令将其参数当作关系符处理，其用法与 `\mathbin` 相同。参见[运算符](#运算符)一节。

#### 各种箭头

**箭头**也是一种二元关系符。如下是一些箭头：

命令 | 效果 | 命令 | 效果 | 命令 | 效果
:--------------------: | :--------------------: | :-------------------: |  :-------------------: | :-------------------: | :-------------------:
`\Downarrow`           | $\Downarrow$           |`\Leftarrow`           | $\Leftarrow$           |`\Leftrightarrow`      | $\Leftrightarrow$
`\Lleftarrow`          | $\Lleftarrow$          |`\Longleftarrow`       | $\Longleftarrow$       |`\Longleftrightarrow`  | $\Longleftrightarrow$
`\Longrightarrow`      | $\Longrightarrow$      |`\Lsh`                 | $\Lsh$                 |`\Rightarrow`          | $\Rightarrow$
`\Rrightarrow`         | $\Rrightarrow$         |`\Rsh`                 | $\Rsh$                 |`\Uparrow`             | $\Uparrow$
`\Updownarrow`         | $\Updownarrow$         |`\circlearrowleft`     | $\circlearrowleft$     |`\circlearrowright`    | $\circlearrowright$
`\curvearrowleft`      | $\curvearrowleft$      |`\curvearrowright`     | $\curvearrowright$     |`\downarrow`           | $\downarrow$
`\downdownarrows`      | $\downdownarrows$      |`\downharpoonleft`     | $\downharpoonleft$     |`\downharpoonright`    | $\downharpoonright$
`\hookleftarrow`       | $\hookleftarrow$       |`\hookrightarrow`      | $\hookrightarrow$      |`\leadsto`             | $\leadsto$
`\leftarrow` 或 `\gets` | $\leftarrow$           |`\leftarrowtail`       | $\leftarrowtail$       |`\leftharpoondown`     | $\leftharpoondown$
`\leftharpoonup`       | $\leftharpoonup$       |`\leftleftarrows`      | $\leftleftarrows$      |`\leftrightarrow`      | $\leftrightarrow$
`\leftrightarrows`     | $\leftrightarrows$     |`\leftrightharpoons`   | $\leftrightharpoons$   |`\leftrightsquigarrow` | $\leftrightsquigarrow$
`\longleftarrow`       | $\longleftarrow$       |`\longleftrightarrow`  | $\longleftrightarrow$  |`\longmapsto`          | $\longmapsto$
`\longrightarrow`      | $\longrightarrow$      |`\looparrowleft`       | $\looparrowleft$       |`\looparrowright`      | $\looparrowright$
`\mapsto`              | $\mapsto$              |`\multimap`            | $\multimap$            |`\nLeftarrow`          | $\nLeftarrow$
`\nLeftrightarrow`     | $\nLeftrightarrow$     |`\nRightarrow`         | $\nRightarrow$         |`\nearrow`             | $\nearrow$
`\nleftarrow`          | $\nleftarrow$          |`\nleftrightarrow`     | $\nleftrightarrow$     |`\nrightarrow`         | $\nrightarrow$
`\nwarrow`             | $\nwarrow$             |`\rightarrow` 或 `\to` | $\rightarrow$          |`\rightarrowtail`      | $\rightarrowtail$
`\rightharpoondown`    | $\rightharpoondown$    |`\rightharpoonup`      | $\rightharpoonup$      |`\rightleftarrows`     | $\rightleftarrows$
`\rightleftharpoons`   | $\rightleftharpoons$   |`\rightrightarrows`    | $\rightrightarrows$    |`\rightsquigarrow`     | $\rightsquigarrow$
`\searrow`             | $\searrow$             |`\swarrow`             | $\swarrow$             |`\twoheadleftarrow`    | $\twoheadleftarrow$
`\twoheadrightarrow`   | $\twoheadrightarrow$   |`\uparrow`             | $\uparrow$             |`\updownarrow`         | $\updownarrow$
`\upharpoonleft` | $\upharpoonleft$ |`\upharpoonright` 或 `\restriction` | $\upharpoonright$ |`\upuparrows` | $\upuparrows$

#### 添加关系描述

可以使用 `\stackrel` 命令在关系符上方添加描述。其接受两个参数，第一个表示要添加的描述，第二个表示下方的关系符。例如：
```latex
$$ \mathrm{2CuO + C \stackrel\triangle= 2Cu + CO_2} $$
```
$$ \mathrm{2CuO + C \stackrel\triangle= 2Cu + CO_2} $$
当然，本例中还可以使用 `\triangleq` 渲染 $\triangleq$ 得到类似的效果。

然而，当描述文字过长时，上述用法可能有所不足。这时，可以利用如下命令生成更好的效果：

命令 | 效果 | 命令 | 效果 | 命令 | 效果
:--------------------: | :----------------------------------------------: | :--------------------: | :----------------------------------------------: |  :--------------------: | :----------------------------------------------:
`\xleftarrow`          | $\xleftarrow[\text{催化剂}]{\text{加热}}$          | `\xrightarrow`         | $\xrightarrow[\text{催化剂}]{\text{加热}}$         | `\xlongequal`          | $\xlongequal[\text{催化剂}]{\text{加热}}$
`\xleftrightarrow`     | $\xleftrightarrow[\text{催化剂}]{\text{加热}}$     | `\xLeftrightarrow`     | $\xLeftrightarrow[\text{催化剂}]{\text{加热}}$

上面这些命令的格式均为
```
\命令[关系符下方内容]{关系符上方内容}
```
其中方括号包围的是可选参数，可以省略。如下是一个例子：
```latex
$$ \mathrm{2H_2O_2 \xlongequal{土豆丝} 2H_2O + O_2} $$
```
$$ \mathrm{2H_2O_2 \xlongequal{土豆丝} 2H_2O + O_2} $$

## 括号与定界符

### 括号

公式中可以使用**括号**。一对括号左侧的称为开符号，右侧的称为闭符号。如下是常用的括号：

开符号 | 闭符号 | 效果 | 备注
:---------------: | :--------------: | :----------------: | :------:
`(`               | `)`              | $(x)$              | 圆括号
`[`               | `]`              | $[x]$              | 方括号
`\{` 或 `\lbrace` | `\}` 或 `\rbrace` | $\{x\}$            | 花括号
`\langle`         | `\rangle`        | $\langle x\rangle$ | 尖括号
`\lfloor`         | `\rfloor`        | $\lfloor x\rfloor$ | 向下取整
`\lceil`          | `\rceil`         | $\lceil x\rceil$   | 向上取整
`\lvert`          | `\rvert`         | $\lvert x\rvert$   | 绝对值
`\lVert`          | `\rVert`         | $\lVert x\rVert$   | 范数

使用上表中的 `\lvert`、`\rvert`、`\lVert`、`\rVert` 比直接使用 `\vert`、`\Vert` 或 `|`、`\|` 更好，因为它们提供了良好的间距。

### 定界符

有时，直接使用括号会导致括号内容突出。这时，可以使用**定界符**调整括号的大小以适应内容。定界符使用 `\left` 和 `\right` 命令定义，例如：
```latex
$$ ( \frac{az + b}{cz + d} ) \quad \left( \frac{az + b}{cz + d} \right) $$
```
$$ ( \frac{az + b}{cz + d} ) \quad \left( \frac{az + b}{cz + d} \right) $$
二者区别立见。

所有的括号都可以通过在开符号前加 `\left`、闭符号前加 `\right` 使之变成定界符。另外，还有一些非括号定界符，如下：

符号 | 效果 | 符号 | 效果
:------------: | :--------------------------------------------------------: | :------------: | :--------------------------------------------------------:
`/` | $\displaystyle\left/\frac{az + b}{cz + d}\right/$ | `\backslash` | $\displaystyle\left\backslash\frac{az + b}{cz + d}\right\backslash$
`\vert` 或 `\|` | $\displaystyle\left\vert\frac{az + b}{cz + d}\right\vert$ | `\Vert` 或 `\\|` | $\displaystyle\left\Vert\frac{az + b}{cz + d}\right\Vert$
`\uparrow` | $\displaystyle\left\uparrow\frac{az + b}{cz + d}\right\uparrow$ | `\Uparrow` | $\displaystyle\left\Uparrow\frac{az + b}{cz + d}\right\Uparrow$
`\downarrow` | $\displaystyle\left\downarrow\frac{az + b}{cz + d}\right\downarrow$ | `\Downarrow` | $\displaystyle\left\Downarrow\frac{az + b}{cz + d}\right\Downarrow$
`\updownarrow` | $\displaystyle\left\updownarrow\frac{az + b}{cz + d}\right\updownarrow$ | `\Updownarrow` | $\displaystyle\left\Updownarrow\frac{az + b}{cz + d}\right\Updownarrow$

以上效果均为行间公式的渲染效果。定界符左右两端的符号可以不配对。如果符号是 `.`，则该端的定界符将为空，例如
```latex
$$ \left( \frac{az + b}{cz + d} \right. $$
```
$$ \left( \frac{az + b}{cz + d} \right. $$
定界符可以嵌套使用。当 `\langle`、`\rangle` 作为定界符使用时，可以直接使用 `\left<`、`\right>`。

另外，可以使用 `\middle` 命令，在定界符间插入一个大小相同的符号，例如：
```latex
$$ S = \left\{ x \middle\vert x \le \frac1{36} \right\} $$
```
$$ S = \left\{ x \middle\vert x \le \frac1{36} \right\} $$

### 手动调整定界符的大小

有时，定界符的大小并不尽如人意。可以使用如下命令手动调整定界符的大小：

命令 | 效果 | 命令 | 效果
:--------------------------: | :------------------------: | :--------------------------: | :------------------------:
无命令                        | $( \| )$
`\big  \bigl  \bigm  \bigr ` | $\bigl( \bigm\| \bigr)$    | `\Big  \Bigl  \Bigm  \Bigr ` | $\Bigl( \Bigm\| \Bigr)$
`\bigg \biggl \biggm \biggr` | $\biggl( \biggm\| \biggr)$ | `\Bigg \Biggl \Biggm \Biggr` | $\Biggl( \Biggm\| \Biggr)$

## 数学标点与省略号

### 数学标点

常用的**数学标点**有 `,`、`;`、`!`、`?`，可以直接通过键盘键入；对于冒号，直接键入的 `:` 是二元关系符，渲染比例时建议使用 `\mathbin:` 得到二元运算符，作为数学标点的 `\colon` 两侧有不同的间距，需注意区别。

可以使用 `\mathpunct` 将符号作为数学标点处理。

### 省略号

以下是一些**数学省略号**：

命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果 | 命令 | 效果
:------: | :------: | :------: | :------: | :------: | :------: | :------: | :------: | :------: | :------:
`\ldots` | $\ldots$ | `\cdots` | $\cdots$ | `\vdots` | $\vdots$ | `\ddots` | $\ddots$
`\dotsc` | $\dotsc$ | `\dotsb` | $\dotsb$ | `\dotsm` | $\dotsm$ | `\dotsi` | $\dotsi$ | `\dotso` | $\dotso$

对于一行公式中的复杂情形，可以直接使用 `\dots` 自动判断并选择合适的符号。例如：
```latex
$$ 1, \dots, n \qquad 1 + \dots + n \qquad a_1 = \dots = a_n $$
```
$$ 1, \dots, n \qquad 1 + \dots + n \qquad a_1 = \dots = a_n $$
此外，还可以使用上表中的第二行五个细分的省略号，分别对应逗号（comma）、二元运算符与关系符（binary）、乘法运算（multiplication）、积分（integral）和其它情形（other）。

省略号可以用于排版矩阵，参见[矩阵]({{ url_for('helps', howto='write-markdown-equations', _anchor='矩阵') }})一节。

## 参考与引用

我们在编写这一文档时，参考了《$\LaTeX$ 入门》一书中的第四章有关公式的内容。如有侵权，请联系删除。
