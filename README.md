# 果果编程课

给果果上课用的仓库。第一课是**开关课**：计算机为什么只用开和关，数字、字母、颜色和像素怎么变成电信号。

真值是正在跑的 Aura 工作区里的七个字符串字面量。服务启动时把 `aura/board-seed.aura` `set-code` 进去，之后翻卡片、改颜色、应用文本框，都是一次 `mutate:replace-value`。增量编译只重做被改脏的这一笔。文本框是工作区印出来的程序；「工作区原文」是 `(current-source)`。同一份原文写在 `runtime/live.aura`，用编辑器改完，页面上按「从文件读回来」，再替换那些字面量。孩子贴来的正文不会被整段 `set-code`。

## 打开

需要本机的 Aura。默认用旁边仓库里的二进制。

```sh
cd /home/dev/code/grok-dev/guoguo
make run
```

终端会打印地址，一般是 <http://127.0.0.1:8765>。第 2 课可以直接打开 <http://127.0.0.1:8765/?lesson=2>。Ctrl+C 结束。

换端口：`GUOGUO_PORT=8770 make run`。

两节课怎么讲，写在 [`docs/lesson-1.md`](docs/lesson-1.md)。

## 检查

```sh
make test
```

`make catalog` 只对课程名册，不需要 Aura。`make check` 只算位和命令，不开网络。`make http` 会真的把页面和 `/api` 走一遍。`make test` 三样都跑。

## 目录

| 路径 | 是什么 |
| --- | --- |
| `aura/bits.aura` | 位、进制、字母、颜色、像素。纯计算，不碰工作区 |
| `aura/board-seed.aura` | 装进工作区的七个定义 |
| `aura/board.aura` | 钉住字面量节点，并用 replace-value 改它们 |
| `aura/serve.aura` | 只听本机的预览服务 |
| `courses/catalog.json` | 课程名册。加一课先改这里 |
| `web/index.html` | 开关课 |
| `web/courses.html` | 全部课程 |
| `docs/` | 每一课的讲稿 |
| `runtime/live.aura` | 最近一次成功 mutation 之后的工作区原文，运行时才有，不进 git |

## 加一课

名册里加一项。`id`、`title`、`summary`、`href`、`doc`、`status` 都要有。`status` 用 `open` 或 `soon`。讲稿放在 `docs/`，`doc` 指向它。

`open` 的课要有自己的页面。`href` 写 `/` 或 `/名字.html`，页面对应 `web/index.html` 或 `web/名字.html`。页面里放上下面这块，`data-course` 用名册里的 `id`：

```html
<nav id="course-bar" data-course="这门课的 id" aria-label="课程"></nav>
<script src="/course-bar.js"></script>
```

服务只发出 `web/` 里一层的 `.html` 和 `.js`，以及 `/catalog.json`。课上如果只是改已有字面量，沿用开关课的 `replace-value`。节点个数会变的课，单独做页面和工作区。`make catalog` 会核对名册、页面和讲稿是否对得上。

## 预览协议

`GET /api/state` 拿整份状态。`POST /api` 的正文是一行命令，或整段带 `(define *bits* "…")` 的程序。成功和失败都回 JSON；失败时位不变。`nodes` 里每一项是工作区里的一个定义和它的字符串字面量。`replace-value` 之后 `define` 和 `literal` 编号不变，变的是 `text`。这一下改过的格子 `changed` 为真。

常用命令：`flip 0`、`set dec 65`、`set bin 01000001`、`set oct 101`、`set hex 41`、`set letter A`、`width 8`、`lamp 0`、`color ff0000`、`chan red hex 80`、`pix 0 2`、`stamp smile`、`reload`。
