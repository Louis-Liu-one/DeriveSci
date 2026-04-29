# KaTeX 公式多行排版

## 摘要

在 $\KaTeX$ 公式中，常常需要渲染多行公式。然而，不能在 `$$ ... $$` 中直接使用 `\\` 换行，而需要使用一些环境。

## 直接合并公式

可以直接使用 `gather` 环境合并多个公式，其中可以使用 `\\` 换行：
```latex
$$
\begin{gather}
    \cos(x) = \sum_{k = 0}^\infty \frac{(-1)^k}{(2k)!}x^{2k} \\
    \sin(x) = \sum_{k = 0}^\infty \frac{(-1)^k}{(2k + 1)!}x^{2k + 1}
\end{gather}
$$
```
$$
\begin{gather}
    \cos(x) = \sum_{k = 0}^\infty \frac{(-1)^k}{(2k)!}x^{2k} \\
    \sin(x) = \sum_{k = 0}^\infty \frac{(-1)^k}{(2k + 1)!}x^{2k + 1}
\end{gather}
$$
可以使用 `gather*` 环境生成无编号的多行公式环境。

## 拆分单行公式

可以将 `split` 环境用于公式环境中。其将单行公式渲染为多行，并在 `align` 等环境中被作为单行处理：
```latex
$$
\begin{align}
    \begin{split}
        \sqrt{1 - x^2} \mathrm dx &= (\cos u) \mathrm d(\sin u) \\
        &= \cos^2 u \mathrm du
    \end{split}
\end{align}
$$
```
$$
\begin{align}
    \begin{split}
        \sqrt{1 - x^2} \mathrm dx &= (\cos u) \mathrm d(\sin u) \\
        &= \cos^2 u \mathrm du
    \end{split}
\end{align}
$$

`split` 环境支持和 `align`、`align*` 环境类似的对齐方式，但不支持多列对齐。

## 对齐多行公式

注意到上面的多行公式中，等号不是对齐的。可以在 `align` 环境中使用 `&` 符以支持对齐：
```latex
$$
\begin{align}
    \cos(x) &= \sum_{k = 0}^\infty \frac{(-1)^k}{(2k)!}x^{2k} \\
    \sin(x) &= \sum_{k = 0}^\infty \frac{(-1)^k}{(2k + 1)!}x^{2k + 1}
\end{align}
$$
```
$$
\begin{align}
    \cos(x) &= \sum_{k = 0}^\infty \frac{(-1)^k}{(2k)!}x^{2k} \\
    \sin(x) &= \sum_{k = 0}^\infty \frac{(-1)^k}{(2k + 1)!}x^{2k + 1}
\end{align}
$$
同样，可以使用 `align*` 环境生成无编号的多行公式环境。

如果 `align`、`align*` 环境中，一行有多个 `&` 符，则第偶数个 `&` 符会自动插入间距，例如：
```latex
$$
\begin{align*}
    \int_{-\pi}^\pi \sin nx \mathrm dx &= 0 & \int_{-\pi}^\pi \cos nx \mathrm dx &= 0 \\
    \int_{-\pi}^\pi \sin nx \sin kx \mathrm dx &= 0 & \int_{-\pi}^\pi \cos nx \cos kx \mathrm dx &= 0
\end{align*}
$$
```
$$
\begin{align*}
    \int_{-\pi}^\pi \sin nx \mathrm dx &= 0 & \int_{-\pi}^\pi \cos nx \mathrm dx &= 0 \\
    \int_{-\pi}^\pi \sin nx \sin kx \mathrm dx &= 0 & \int_{-\pi}^\pi \cos nx \cos kx \mathrm dx &= 0
\end{align*}
$$

可以使用 `alignat`、`alignat*` 环境对对齐方式做更多的调整。此环境接受一个正整数为参数，表示水平方向上有几组公式要对齐，每两列为一组，每列以 `&` 符隔开。同时，此环境不会在各组公式间添加间距。例如：
```latex
$$
\begin{alignat*}{5}
    (1 &  &+{}& 2 &   &+{}& 3 &)^2 &={}& 36 \\
    1 &^2 &+{}& 2 &^2 &+{}& 3 &^2  &={}& 14
\end{alignat*}
$$
```
$$
\begin{alignat*}{5}
    (1 &  &+{}& 2 &   &+{}& 3 &)^2 &={}& 36 \\
    1 &^2 &+{}& 2 &^2 &+{}& 3 &^2  &={}& 14
\end{alignat*}
$$

### 对齐连等式

对于连等式，为了避免丑陋的间距，有如下两种解决方案：
1. 在等号前使用 `&` 符，并在首行添加幻影盒子，例如：
```latex
$$
\begin{align*}
    &\mathrel{\phantom=} \int_{-\pi}^\pi \sin nx \cos kx \mathrm dx \quad (n \ne k) \\
    &= \frac12\int_{-\pi}^\pi (\sin(n + k)x + \sin(n - k)x) \mathrm dx \\
    &= \left.\frac12\left(\frac{\sin(n + k)x}{n + k}
        + \frac{\sin(n - k)x}{n - k}\right)\right|_{-\pi}^\pi \\
    &= \frac12(0 + 0) - \frac12(0 + 0) = 0
\end{align*}
$$
```
2. 在等号后使用 `&` 符，并在每个等号后添加空分组以保证间距，例如：
```latex
$$
\begin{align*}
    & \int_{-\pi}^\pi \sin nx \cos kx \mathrm dx \quad (n \ne k) \\
    ={}& \frac12\int_{-\pi}^\pi (\sin(n + k)x + \sin(n - k)x) \mathrm dx \\
    ={}& \left.\frac12\left(\frac{\sin(n + k)x}{n + k}
        + \frac{\sin(n - k)x}{n - k}\right)\right|_{-\pi}^\pi \\
    ={}& \frac12(0 + 0) - \frac12(0 + 0) = 0
\end{align*}
$$
```

以上两种方案都能得到如下的效果：
$$
\begin{align*}
    & \int_{-\pi}^\pi \sin nx \cos kx \mathrm dx \quad (n \ne k) \\
    ={}& \frac12\int_{-\pi}^\pi (\sin(n + k)x + \sin(n - k)x) \mathrm dx \\
    ={}& \left.\frac12\left(\frac{\sin(n + k)x}{n + k}
        + \frac{\sin(n - k)x}{n - k}\right)\right|_{-\pi}^\pi \\
    ={}& \frac12(0 + 0) - \frac12(0 + 0) = 0
\end{align*}
$$

`\mathrel` 命令参见[此处]({{ url_for('helps', howto='write-katex-symbols', _anchor='二元关系符') }})。

## 合并公式成块

可以使用 `cases` 环境表示多种情况：
```latex
$$
D(x) = \begin{cases}
    1, & x \in \mathbb Q \\
    0, & x \in \mathbb R \setminus \mathbb Q
\end{cases}
$$
```
$$
D(x) = \begin{cases}
    1, & x \in \mathbb Q \\
    0, & x \in \mathbb R \setminus \mathbb Q
\end{cases}
$$
`cases` 环境中使用行内公式渲染模式。如果需要使用行间公式模式，可以使用 `dcases` 环境。

另外，可以使用 `gathered`、`aligned` 组合公式，例如
```latex
$$
\left\{ \begin{aligned}
    AB &= A'B' \\ \angle ABC &= \angle A'B'C' \\ BC &= B'C'
\end{aligned} \right. \Rightarrow \triangle ABC \cong \triangle A'B'C' \text{(SAS)}
$$
```
$$
\left\{ \begin{aligned}
    AB &= A'B' \\ \angle ABC &= \angle A'B'C' \\ BC &= B'C'
\end{aligned} \right. \Rightarrow \triangle ABC \cong \triangle A'B'C' \text{(SAS)}
$$

## 控制编号

可以使用 `\notag` 命令禁用多行公式中某行的编号，使用 `\tag` 命令定制编号样式，例如：
```latex
$$
\begin{align}
    \cos(x) &= \sum_{k = 0}^\infty \frac{(-1)^k}{(2k)!}x^{2k} \tag{$\alpha$} \\
    \sin(x) &= \sum_{k = 0}^\infty \frac{(-1)^k}{(2k + 1)!}x^{2k + 1} \notag \\
    \exp(x) &= \sum_{k = 0}^\infty \frac1{k!}x^k \tag{$\gamma$}
\end{align}
$$
```
$$
\begin{align}
    \cos(x) &= \sum_{k = 0}^\infty \frac{(-1)^k}{(2k)!}x^{2k} \tag{$\alpha$} \\
    \sin(x) &= \sum_{k = 0}^\infty \frac{(-1)^k}{(2k + 1)!}x^{2k + 1} \notag \\
    \exp(x) &= \sum_{k = 0}^\infty \frac1{k!}x^k \tag{$\gamma$}
\end{align}
$$
