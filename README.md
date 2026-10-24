# 果果编程课

给果果上课用的仓库。第一课是**开关课**：计算机为什么只用开和关，数字、字母、颜色和像素怎么变成电信号。

真值在 Aura 里。网页是预览，不是另一份账本。翻一张卡片，下面的 `(define *bits* ...)` 会改；改这段程序再按「用这段程序更新画面」，卡片、八进制、十六进制和颜色一起改。同一串 0 和 1 也写在 `runtime/live.aura`，用编辑器改完，页面上按「从文件读回来」。

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

`make check` 只算位和命令，不开网络。`make http` 会真的把页面和 `/api` 走一遍。

## 目录

| 路径 | 是什么 |
| --- | --- |
| `aura/bits.aura` | 位、进制、字母、颜色、像素，以及一小段可往返的 Aura |
| `aura/serve.aura` | 只听本机的预览服务 |
| `web/index.html` | 果果点的那一页 |
| `docs/` | 以后每一课的讲稿 |
| `runtime/live.aura` | 当前这串开关，运行时才有，不进 git |

以后的编程课也放在这个仓库：新的一课加一份讲稿，需要互动时再加一页。

## 预览协议

`GET /api/state` 拿整份状态。`POST /api` 的正文是一行命令，或整段带 `(define *bits* "…")` 的程序。成功和失败都回 JSON；失败时位不变。

常用命令：`flip 0`、`set dec 65`、`set bin 01000001`、`set oct 101`、`set hex 41`、`set letter A`、`width 8`、`lamp 0`、`color ff0000`、`chan red hex 80`、`pix 0 2`、`stamp smile`、`reload`。
