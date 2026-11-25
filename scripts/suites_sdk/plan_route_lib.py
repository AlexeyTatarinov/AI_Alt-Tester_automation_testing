# -*- coding: utf-8 -*-
"""Планировщик маршрута по кругам-препятствиям (A* на сетке 0,2 м). Тот же алгоритм, что plan_route.py, но как функция."""
import heapq
import math


def plan(start, goal, obstacles, margin=0.7, h=0.2, pad=12.0, spacing=4.0):
    """obstacles: [(x, z, r)] - r уже включает радиус игрока. Возвращает (вехи, длина, макс. боковое смещение) или (None, None, ближайшая точка)."""
    # препятствия, внутри круга которых стоит старт или цель, отбрасываем (круг по AABB грубее реального коллайдера)
    obstacles = [o for o in obstacles if math.hypot(start[0] - o[0], start[1] - o[1]) > o[2] + margin and math.hypot(goal[0] - o[0], goal[1] - o[1]) > o[2] + margin]
    x0 = min(start[0], goal[0]) - pad
    x1 = max(start[0], goal[0]) + pad
    z0 = min(start[1], goal[1]) - pad
    z1 = max(start[1], goal[1]) + pad
    W, H = int((x1 - x0) / h) + 1, int((z1 - z0) / h) + 1
    bl = [[False] * H for _ in range(W)]
    for ox, oz, r in obstacles:
        r = r + margin
        for i in range(max(0, int((ox - r - x0) / h)), min(W, int((ox + r - x0) / h) + 1)):
            for j in range(max(0, int((oz - r - z0) / h)), min(H, int((oz + r - z0) / h) + 1)):
                if math.hypot(x0 + i * h - ox, z0 + j * h - oz) <= r:
                    bl[i][j] = True
    cell = lambda p: (min(W - 1, max(0, int((p[0] - x0) / h))), min(H - 1, max(0, int((p[1] - z0) / h))))
    s, g = cell(start), cell(goal)
    bl[s[0]][s[1]] = False
    bl[g[0]][g[1]] = False
    pq, came, cost = [(0, s)], {s: None}, {s: 0}
    while pq:
        _, u = heapq.heappop(pq)
        if u == g:
            break
        for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            v = (u[0] + di, u[1] + dj)
            if not (0 <= v[0] < W and 0 <= v[1] < H) or bl[v[0]][v[1]]:
                continue
            nc = cost[u] + math.hypot(di, dj)
            if v not in cost or nc < cost[v]:
                cost[v] = nc
                came[v] = u
                heapq.heappush(pq, (nc + math.hypot(g[0] - v[0], g[1] - v[1]), v))
    if g not in came:
        best = min(came, key=lambda v: math.hypot(g[0] - v[0], g[1] - v[1]))
        return None, None, (x0 + best[0] * h, z0 + best[1] * h)
    path, u = [], g
    while u:
        path.append((x0 + u[0] * h, z0 + u[1] * h))
        u = came[u]
    path = path[::-1]
    L = sum(math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]) for i in range(len(path) - 1))
    D = math.hypot(goal[0] - start[0], goal[1] - start[1]) or 1.0
    lat = max(abs((goal[0] - start[0]) * (start[1] - p[1]) - (start[0] - p[0]) * (goal[1] - start[1])) / D for p in path)
    way = [path[0]]
    for p in path[1:]:
        if math.hypot(p[0] - way[-1][0], p[1] - way[-1][1]) >= spacing:
            way.append(p)
    if way[-1] != path[-1]:
        way.append(path[-1])
    return way, L, lat


def plan_rects(start, goal, rects, margin=0.7, player_r=0.3, h=0.1, pad=10.0, spacing=3.0, free_r=0.6):
    """rects: [(cx, cz, ex, ez)] - AABB коллайдеров (полуразмеры). Препятствие = прямоугольник, расширенный на player_r + margin.
    Клетки в free_r вокруг старта и цели считаются свободными. Возвращает (вехи, длина, боковое) или (None, None, ближайшая точка)."""
    x0 = min(start[0], goal[0]) - pad
    x1 = max(start[0], goal[0]) + pad
    z0 = min(start[1], goal[1]) - pad
    z1 = max(start[1], goal[1]) + pad
    W, H = int((x1 - x0) / h) + 1, int((z1 - z0) / h) + 1
    bl = [[False] * H for _ in range(W)]
    e = player_r + margin
    for cx, cz, ex, ez in rects:
        for i in range(max(0, int((cx - ex - e - x0) / h)), min(W, int((cx + ex + e - x0) / h) + 1)):
            for j in range(max(0, int((cz - ez - e - z0) / h)), min(H, int((cz + ez + e - z0) / h) + 1)):
                bl[i][j] = True
    for c in (start, goal):
        for i in range(max(0, int((c[0] - free_r - x0) / h)), min(W, int((c[0] + free_r - x0) / h) + 1)):
            for j in range(max(0, int((c[1] - free_r - z0) / h)), min(H, int((c[1] + free_r - z0) / h) + 1)):
                if math.hypot(x0 + i * h - c[0], z0 + j * h - c[1]) <= free_r:
                    bl[i][j] = False
    cell = lambda p: (min(W - 1, max(0, int((p[0] - x0) / h))), min(H - 1, max(0, int((p[1] - z0) / h))))
    s, g = cell(start), cell(goal)
    pq, came, cost = [(0, s)], {s: None}, {s: 0}
    while pq:
        _, u = heapq.heappop(pq)
        if u == g:
            break
        for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            v = (u[0] + di, u[1] + dj)
            if not (0 <= v[0] < W and 0 <= v[1] < H) or bl[v[0]][v[1]]:
                continue
            nc = cost[u] + math.hypot(di, dj)
            if v not in cost or nc < cost[v]:
                cost[v] = nc
                came[v] = u
                heapq.heappush(pq, (nc + math.hypot(g[0] - v[0], g[1] - v[1]), v))
    if g not in came:
        best = min(came, key=lambda v: math.hypot(g[0] - v[0], g[1] - v[1]))
        return None, None, (x0 + best[0] * h, z0 + best[1] * h)
    path, u = [], g
    while u:
        path.append((x0 + u[0] * h, z0 + u[1] * h))
        u = came[u]
    path = path[::-1]
    L = sum(math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]) for i in range(len(path) - 1))
    D = math.hypot(goal[0] - start[0], goal[1] - start[1]) or 1.0
    lat = max(abs((goal[0] - start[0]) * (start[1] - p[1]) - (start[0] - p[0]) * (goal[1] - start[1])) / D for p in path)
    way = [path[0]]
    for p in path[1:]:
        if math.hypot(p[0] - way[-1][0], p[1] - way[-1][1]) >= spacing:
            way.append(p)
    if way[-1] != path[-1]:
        way.append(path[-1])
    return way, L, lat
