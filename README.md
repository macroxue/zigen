# Linux下自制汉字形声码输入法

## 汉字拆分

所有GB2312的6763个汉字都在 breakdown.txt 文件中拆分。
文件的开头是独体字以及复合部件的拆分，最直接的学习方法
就是看它们是怎么被拆的。下面是一些拆分原则。

 * 取大优先。比如：‘元’拆为‘二儿’而不是‘一兀’。
 * 交重可拆。比如：‘重’拆为‘千里’，‘里’拆为‘田土’。
 * 拆单撇。比如：‘必’拆为‘心丿’，‘白’拆为‘丿日’。
 * 拆顶横。比如：‘开’拆为‘一廾’，‘天’拆为‘一大’。
   例外：‘丁’、‘王’、‘正’都是字根，所以不拆。
 * 尽量不拆单点。比如：‘亠’是字根，点不单独拆出。
   ‘为’拆为‘[两点]力’而不是‘丶力丶’。

## 编码规则

最初的编码设计对表形码有多处借鉴，但后来发现字根和英文
字母之间的象形映射对字根的安排有太多的约束，不利于方案的
优化调整。比如十字交叉形，除了X键就没有其它合适的位置了。
又比如离散两笔类有很多高频字根，却只能放在分号键上，打起来
就很不顺手。

最终决定还是采用类似五笔的分区方法，把字根分成五个大类，
比较规整地分配在键盘上。这五个类是：
 * 离散，即笔画分散，不连不交;
 * 连接，即笔画相连或相接，但不相交;
 * 交叉，即笔画相交;
 * 包围，即该字根可以包围其它字根;
 * 封闭，即该字根呈现一个封闭的区间。

每个大类里又分若干个小类，如下图所示。字根键位的安排基本上
按照食指、中指、无名指、小指，从简到繁。这样明显的规律可以
减少记忆负担，有些需要特别留意的字根已用红色标注。

![拓扑形](https://github.com/macroxue/zigen/blob/master/topo.jpg)

所有字根及其编码都在 group.txt 文件中。采用27键编码，实在
没有理由放着原位键上的分号不用， 写中文有几时用得到分号呢？
如果一定要只用26键，可以把十交叉和木交叉合并，把金字旁移到
折交叉。

编码规则是前三末一，不足四码时加拼音的前两个字母。最关键的
是：当取形超过四码时，单笔划的横、竖、撇、点将被忽略，
除非该笔划是第一码。

全码重码有158组319字，而出简不出全时的重码只有17组35字。
所有简码根据汉字使用频率自动生成，不会有重码，也没有
无理码。其中一简字27个，二简字700多个，三简和三码字近4300
个，总共有5000多个字可以三码以内输入。动态平均码长
（不含空格上屏）是2.01。

## 码表生成

生成编码的命令行是：

    ./gene.py

产生的编码文件是 code.txt。

## 安装

先安装小企鹅输入法：

    sudo apt-get install fcitx-table

拷贝配置文件：

    mkdir -p ~/.config/fcitx/table
    cp ./shape.conf ~/.config/fcitx/table

然后运行：

    ./install.sh

以后每次修改或新生成编码文件后，同样运行 ./install.sh
使改动生效。

# 前因

十几年前还是学生的时候，我对输入法的制作产生了浓厚的
兴趣。那时的拼音还不够智能，还比不上拼形编码。印象
最深的是表形码，它把汉字字根和英文字母以象形的方式
联系起来。这种联系是如此地深刻，以至于从未实际使用过
表形码的我在十几年后还记得口是O，女是A，门是N，
纟是W …… 等等。

当时是个万码腾的年代，我只会拼音，也打不快，但我会写
程序。于是萌生了一个想法，可不可以用程序自动生成一个
编码方案，并加以优化呢？热血一涌上头，我就开始了自己
的拆字工程。GB2312有6763个汉字，前后花了几个星期，
终于把容易的复合字拆完了。复合字都有明显的左右结构、
上下结构或包围结构，所以容易。剩下的独体字就难了，
不同的形码有不同的拆法。于是又花了几个星期，按照比较
熟悉的表形码规则拆完了它们。

拆字可以说是形码设计过程中最耗时、最耗体力的部份了，
因为汉字实在是太多了。我只拆了六千多字就累得半死，
更不必说拆几万字的大字库了。如果不同的设计者们能够
共享这个过程，他们就可以有更多的精力去优化编码方案。
这些都是后话。

字是拆完了，也产生了两百多个字根。当时简单地把它们
按起始笔划归类，分配到26个英文字母键上，然后写了个
Python程序把6763个汉字编码，最长四码。结果统计了一下，
竟然有将近1300个重码。于是我又写了一个优化程序，自由
地把字根分配到字母键上。即使这样完全不实用的编码，
也有将近500个重码。真是不动手就不知道难啊！

之后因为学业，就没有继续在编码上花时间了。这一放，
就放了十几年。当有一天整理以前写过的程序时，不经意
发现了这一段尘封的往事，又提起了我对输入法的兴趣。
时过境迁，拼音已不是当年的拼音，其智能输入方式早已把
大量形码远远地甩在了身后，摇身一变成为主流。搞形码的
越来越少，我又有什么理由再把以前未完成的形码捡起来呢？

有！就因为我能。这已经是一个个性化的时代了，人们做事
不再是为了生计或是图个名利。想做就做，更多的是为了
与众不同。

## 后果

这个形声码方案算是完成了，一些指标看上去也不错。有什么
前途吗？没有！有什么钱图吗？更没有！说白了这就是一个
很好的玩具，可以用来消磨业余时间，体会一下当年“万码奔腾”
的那种感觉。俱往矣！如今也就剩下输入法爱好者还在玩形码，
少数专业录入人员还在用形码。

令人欣慰的是，形码已经完成了中文信息化的历史任务，在
电脑上或是用手机输入中文早已不再是问题，在某些方面甚至
超过了英文输入。中文信息处理从编码时代进入智能时代已
不可阻挡。电脑啊，让人脑变得更懒一些吧！
