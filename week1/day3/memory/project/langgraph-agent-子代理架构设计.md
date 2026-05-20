---
name: langgraph-agent-子代理架构设计
title: LangGraph Agent 子代理架构设计
description: 确认项目核心子代理数量及职责分工方案
type: project
---
项目采用主从式5子代理架构：1）ToolRunner负责工具执行；2）MemoryRetrieval处理记忆查询；3）Memory管理记忆CRUD；4）PermissionReview执行安全审查；5）ToolSearch协助工具检索。该设计通过专业化分工实现模块解耦，支持水平扩展。
