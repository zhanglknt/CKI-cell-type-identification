# v0.5.5 发布链 phase-2 审计 — Zenodo DOI 回写闭环

日期：2026-10-03 00:20（GMT+8）
提交：3a99762（phase-2）+ ff5b0db（清理 z_tmp.json），远端 main = ff5b0db（ls-remote 核对）

## 四件套终态（零开口）

| 件 | 值 |
|---|---|
| tag | v0.5.5（phase-1 @421b1ec 已建） |
| Zenodo record | **23104178**（state done；conceptrecid 20405458，共 17 版最新） |
| version DOI | **10.5281/zenodo.23104178**（已回写 MS Code availability ×1 + 三处 v0.5.4→v0.5.5） |
| Release | id 401857516，资产 **605985574**（13,880,581 B，readback sha256 MATCH，body 已补注 version DOI + nc59 说明） |

- 旧资产 605711011（phase-1，无 DOI 无 nc59）已删
- DOI 三件套：concept 20405458 / version 23104178 / record 页全部解析正常
- phase-2 构建 **218/218**（A15 锚已同步 v0.5.5 DOI）
- 最终资产含 nc59 全部变更（SI Notes/Tables 首引重排 + CL 修订）+ DOI 回写

## 代理故障排障记录（phase-2 前置阻塞 ~2h）
- 沙箱代理 127.0.0.1:58367 白名单只放行 GitHub（zenodo/google 恒 502）——非故障，是沙箱策略
- 系统代理 127.0.0.1:10808（注册表 ProxyEnable=1）一度三走法全超时（客户端/节点失效）；用户恢复后：google 204 / zenodo 200
- Zenodo 搜索端点 /api/records?q=... 对默认 curl UA 返回空 body（HTTP 200 size 0）；**必须带浏览器 UA**；直接 /api/records/{id} 无此问题
- conceptrecid 是 20405458（22735744 是 v0.5.0 的 version record id，非 concept）
- 轮询脚本 _v058_zenodo_poll.py（task 9A6kDx）150min 超时自灭，64 轮全 502 系沙箱代理所致
