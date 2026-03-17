# AI功能调试说明

## 🔧 已修复的问题

### 问题1: "AI正在思考..."不消失
**原因**: 加载消息的移除逻辑依赖ID匹配，可能出现匹配失败
**解决方案**: 
- 改用直接创建DOM元素的方式，不依赖ID
- 使用 `loadingMsg.remove()` 直接移除
- 添加了 `loading-message` CSS类，便于识别

### 问题2: 用户消息消失
**原因**: 消息添加后可能被错误清除
**解决方案**:
- 优化消息ID生成，加入随机字符串避免重复
- 添加 `white-space: pre-wrap` 保持格式
- 改进日志输出，便于调试

### 问题3: AI无法回答
**可能原因**:
1. 未登录或Token过期
2. AI API配置错误
3. 网络连接问题

---

## 📋 检查清单

### 1. 检查登录状态
打开浏览器开发者工具（F12），在Console中输入：
```javascript
console.log('Token:', localStorage.getItem('authToken'));
```
如果返回 `null`，需要重新登录。

### 2. 检查AI API配置
在服务器控制台查看是否有以下错误：
- `QWEN_API_KEY environment variable is required` - 缺少API密钥
- `API request failed: 401` - API密钥无效
- `Request timeout` - 请求超时

### 3. 查看网络请求
在浏览器开发者工具的 Network 标签：
- 找到 `/api/ai/word-analysis` 等请求
- 查看状态码：
  - `200` - 成功
  - `401` - 未授权（需要登录）
  - `500` - 服务器错误
- 查看响应内容，看是否有错误信息

### 4. 查看控制台日志
浏览器Console会输出：
```
🤖 发送AI请求: word-analysis {poem_id: 1}
📡 AI响应状态: 200
📨 AI响应数据: {answer: "...", response_time: 1.5}
✅ 已移除消息: msg-xxx
```

---

## 🐛 常见错误及解决方案

### 错误1: "请先登录后使用AI助手"
**解决**: 
```bash
# 返回登录页面重新登录
# 或者在浏览器Console中手动设置token
localStorage.setItem('authToken', 'your-token-here');
```

### 错误2: "AI助手暂时无法回答您的问题"
**检查**: 
1. 服务器是否运行 `python app.py`
2. `.env` 文件中 `QWEN_API_KEY` 是否正确
3. 网络是否能访问 `https://api.siliconflow.cn`

**测试API连接**:
```bash
# 在PowerShell中测试
curl -X POST "https://api.siliconflow.cn/v1/chat/completions" `
  -H "Authorization: Bearer sk-your-api-key" `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"Qwen/Qwen2.5-7B-Instruct\",\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}'
```

### 错误3: "网络连接失败"
**检查**:
1. 服务器是否在运行
2. 端口5000是否被占用
3. 防火墙是否阻止连接

---

## 🎯 测试步骤

### 完整测试流程

1. **启动服务器**
```powershell
cd e:\poem_project\code
python app.py
```

2. **打开浏览器**
访问: http://localhost:5000

3. **登录**
使用测试账号: `test_user` / `test123`

4. **进入古诗学习页面**
选择任意一首古诗

5. **测试AI功能**
   - 点击"字词解析" - 应该自动分析关键字词
   - 点击"背景介绍" - 应该介绍创作背景
   - 点击"意境赏析" - 应该分析艺术特色
   - 输入自定义问题测试

6. **观察结果**
   - ✅ 用户消息应该显示在右侧（蓝色背景）
   - ✅ "AI正在思考..."应该出现并消失
   - ✅ AI回答应该显示在左侧（灰色背景）
   - ❌ 不应该有重复的加载提示
   - ❌ 消息不应该消失

---

## 📝 环境变量检查

确保 `.env` 文件包含：
```env
QWEN_API_KEY=sk-zzyesjjoxlxlfptbpwjnrxvxybunudvbqbaysrddqljqeiqf
QWEN_API_URL=https://api.siliconflow.cn/v1/chat/completions
```

---

## 💡 调试技巧

### 1. 启用详细日志
在 `app.py` 中设置：
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### 2. 查看完整错误信息
在浏览器Console中：
```javascript
// 启用详细日志
localStorage.setItem('debug', 'true');

// 查看所有localStorage数据
for (let key in localStorage) {
    console.log(key, ':', localStorage.getItem(key));
}
```

### 3. 手动测试API
在浏览器Console中：
```javascript
// 测试AI API
fetch('/api/ai/word-analysis', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('authToken')
    },
    body: JSON.stringify({ poem_id: 1 })
})
.then(r => r.json())
.then(d => console.log('结果:', d))
.catch(e => console.error('错误:', e));
```

---

## 🆘 仍然无法解决？

1. **清除浏览器缓存**
   - 按 Ctrl+Shift+Delete
   - 选择"缓存的图片和文件"
   - 清除后刷新页面

2. **重启服务器**
   - 停止服务器（Ctrl+C）
   - 重新运行 `python app.py`

3. **检查数据库**
   - 确保用户已创建
   - 确保古诗数据已导入

4. **查看服务器日志**
   - 服务器控制台会显示所有请求和错误
   - 关注带有 `ERROR` 或 `Exception` 的行

---

**如果问题依然存在，请提供以下信息：**
1. 浏览器Console的完整日志
2. 服务器控制台的错误信息
3. Network标签中失败请求的详情
